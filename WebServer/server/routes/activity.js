/**
 * module for activity
 * GET /acitivities [search activity]
 * GET /acitivity/:id [get activity by id]
 * POST /activities [upload an activity]
 * DELETE /activity/:id [delete an activity]
 */
const express = require('express');
const router = express.Router();
const config = require('../config.js');
const utils = require('../utils');
const jwt = require('jsonwebtoken');

const multipart = require('connect-multiparty');
const multipartMiddleware = multipart();
const fs = require('fs');

const { body, header, validationResult } = require('express-validator');
const client = utils.client;
const redis_client = utils.redis_client;
const Activity = require('../models').activities;



// search activities by keywords and other filters
router.get('/activities', (req, res, next) => {
	// this part handles the input parameters and
	// construct query for elasticsearch

	// keyword for search
	if (req.query.key === undefined) {
		return res.json({msg: 'missing param: key'});
	}
	if (req.query.location == 1 && req.query.state == undefined) {
		return res.json({msg: 'missing param: state'});
	}
	var query = { bool : {
		must: [{
			multi_match : {
				query: req.query.key,
				fields: ['name', 'tags']
			}}
		],
		must_not: []
	}};

	var filter = { bool : {
		should:[]
	}};
	if (req.query.start !== undefined) {
		var start = parseInt(req.query.start);
		filter.bool.should.push({range:{activity_date:{ gte: start}}});
	}
	if (req.query.end !== undefined) {
		var end = parseInt(req.query.end);
		if (filter.bool.should.length == 0) {
			filter.bool.should.push({range:{activity_date:{lte: end}}});
		} else {
			filter.bool.should[0].range.activity_date.lte = end;
		}
	} else {
		filter.bool.should.push({term:{activity_date: 0}});
	}

	// location info for activity
	if (req.query.location !== undefined) {
		// online event
		if (req.query.location == 0) {
			query.bool.must.push({term:{"location.keyword": 'Online Event'}});
		} else if (req.query.location == 1) {
			query.bool.must_not.push({term: {"location.keyword": 'Online Event'}});
			// add state
			query.bool.must.push({term:{"state.keyword": req.query.state}});
			// add city
			if (req.query.city !== undefined) {
				query.bool.must.push({term:{"city.keyword": req.query.city}});
			}
		}
	}

	// paid info for activity
	if (req.query.paid !== undefined) {
		if (req.query.paid == 0) {
			query.bool.must.push({term: {price: 'free'}});
		} else if (req.query.paid == 1) {
			query.bool.must.push({term: {price: 'donation'}});
		} else if (req.query.paid == 2) {
			query.bool.must_not.push({term: {price: 'free'}});
			query.bool.must_not.push({term: {price: 'donation'}});
		}
	}
	if (filter.length > 0) {
		query.bool.filter = filter;
	}

	query.bool.filter = filter;

	// process offset
	var from = 0;
	if (req.query.offset !== undefined) {
		from = parseInt(req.query.offset);
	}

	// console.log(JSON.stringify(query));
	// construct query
	req.es_query = {
		index: config.es.index,
		type: config.es.doc_type,
		from: from,
		size: 10,
		body: {query: query},
		sort: ['activity_date:asc'],
		_source: ['name', 'activity_date', 'price', 'thumbnail', 'tags', 'location', 'state', 'city']
	};
	next();
}, async (req, res) => {
	search_err = null;
	const {body} = await client.search(req.es_query).catch(err => {
		search_err = err;
	});
	if (search_err != null) {
		return res.json({msg: search_err});
	}
	var result = new Array();
	for (var hit of body.hits.hits) {
		result.push({
			id: hit._id,
			date: hit._source.activity_date,
			name: hit._source.name,
			price: hit._source.price,
			thumbnail: hit._source.thumbnail,
			location: hit._source.location,
			state: hit._source.state,
			city: hit._source.city
		});
	}
	// insert keyword into recommand lib
	if (body.hits.total.value > 0) {
		addKeyIntoRecommand(req, req.query.key);
	}
	return res.json({
		count: body.hits.total.value,
		results: result
	});
});


/**
 * upload an activity
 * @param  {[type]} '/activities'                                          [description]
 * @param  {[type]} [	body('name').not().isEmpty().withMessage('Name       empty')       [description]
 * @param  {[type]} body('date').not().isEmpty().withMessage('Date         empty')       [description]
 * @param  {[type]} body('price').not().isEmpty().withMessage('Price       empty')       [description]
 * @param  {[type]} body('location').not().isEmpty().withMessage('Location empty')]      [description]
 * @param  {[type]} multipartMiddleware                                    [description]
 * @param  {[type]} (req,                                                  res           [description]
 * @return {[type]}                                                        [description]
 */
router.post('/activities', multipartMiddleware, [
	header('authorization').not().isEmpty().withMessage('Token missing')
		.custom(utils.validateJWT),
	body('name').not().isEmpty().withMessage('Name empty'),
	body('date').not().isEmpty().withMessage('Date empty')
		.custom(value => {
			const number = parseInt(value);
			if (isNaN(number)) {
				return Promise.reject('Date type error');
			}
 			if (number !== 0 && number < Date.now()/1000) {
				return Promise.reject('must be future time');
			}
			return true;
		}),
	body('price').not().isEmpty().withMessage('Price empty'),
	body('location').not().isEmpty().withMessage('Location empty'),
	body('tags').toArray(),
	body('description').not().isEmpty().withMessage('Description empty')
], async (req, res) => {
	var err_msg = utils.validateRequest(req);
	if (err_msg !== null) {
		return res.json({ err: err_msg });
	}
	err_msg = validateAndProcessThumbnail(req);
	if (err_msg !== null) {
		return res.json({ err: err_msg });
	}
	state = "";
	city = "";
	if (req.body.loaction != 'Online Event') {
		if (req.body.city == undefined || req.body.state == undefined) {
			return res.json({ err: 'missing state or city'});
		} else {
			state = req.body.state;
			city = req.body.city;
		}
	}
	var has_error = false;
	const id = await uploadActivityToES(req).catch(err => {
		has_error = true;
		// console.log(err.body.error.root_cause);
		return res.json({err: 'es error'});
	});
	const activity = await Activity.create({
		uuid: id,
		name: req.body.name,
		date: req.body.date,
		price: req.body.price,
		thumbnail: config.host + req._path,
		location: req.body.location,
		city: city,
		state: state
	}).catch(err => {
		has_error = true;
		console.log("err"+err);
		// delete activity from es
		client.delete({
			index: config.es.index,
			type: config.es.doc_type,
			id: id
		}).catch(err => {
			if (config.debug) {
				console.log(err);
			}
		});
		return res.json({ err: 'mysql error' });
	});
	if (config.debug) {
		client.delete({
			index: config.es.index,
			type: config.es.doc_type,
			id: id
		});
	}

	if (!has_error) {
		return res.json({status: true, id: activity.uuid});
	}
});

// get activity by id
router.get('/activity/:id', async (req, res) => {
	const { body } = await client.get({
		index: config.es.index,
		id: req.params.id
	}).catch(err => {
		return res.json({msg: err.body});
	});
	// console.log(body);
	res.json({
		name: body._source.name,
		date: body._source.activity_date,
		organizer: body._source.organizer,
		description: body._source.description,
		location: body._source.location,
		price: body._source.price,
		tags: body._source.tags,
		source: body._source.source,
		thumbnail: body._source.thumbnail,
		platform: body._source.platform,
		state: body._source.state,
		city: body._source.city
	});
});


router.delete('/activity/:id', async(req, res) => {
	const { body } = await client.delete({
			index: config.es.index,
			type: config.es.doc_type,
			id: req.params.id
	}).catch(err => {
		return res.json({msg: err.body});
	});
	// console.log(body);
	res.json({status: true});
});

module.exports = router;

/**
 * validate the upload image and store it in the server
 * @param  {Object} req Request object.
 * @return {String}     Error message when error, othersise null.
 */
function validateAndProcessThumbnail(req) {
	if (req.files.thumbnail === undefined) {
		return 'Thumbnial missing';
	}
	if (req.files.thumbnail instanceof Array) {
		return 'Only one picture is allowed';
	}
	// TODO: limit the size of the upload image here
	if (req.files.thumbnail.size == 0) {
		return 'Illege image size.';
	}
	var folderPath = './public/images/' + req.user.id;
	if (!fs.existsSync(folderPath)) {
    	fs.mkdirSync(folderPath);
  	}
  	var image = req.files.thumbnail;
  	const imagePath = folderPath + '/' + image.originalFilename;
    fs.renameSync(image.path, imagePath);
    req._path = '/images/' + req.user.id + '/' + image.originalFilename;
    req.files = null;
    return null;
}

async function uploadActivityToES(req) {
	var state = "";
	var city = "";
	if (req.body.loaction != 'Online Event') {
		state = req.body.state;
		city = req.body.city;
	}
	const record = await client.index({
		index: config.es.index,
		type: config.es.doc_type,
		refresh: 'true',
		body: {
			activity_date: req.body.date,
			description: req.body.description,
			location: req.body.location,
			name: req.body.name,
			organizer: req.user.name,
			platform: config.name,
			price: req.body.price,
			tags: req.body.tags,
			thumbnail: config.host + req._path,
			state: state,
			city: city
		}
	});
	return record.body._id;
}


function addKeyIntoRecommand(req, key) {
	// check whether token is empty to decide which recommand to add
	var redis_key = '';
	if (req.headers.authorization != null) {
		const token = req.headers.authorization.split(' ')[1];
		var decoded;
		try {
			decoded = jwt.verify(token, config.jwt_secret);
			redis_key = 'hot:' + decoded.id;
			redis_client.zincrby(redis_key, 1, key);
		} catch (err) {
			console.log(err);
		}
	}

	// add key into redis
	redis_client.zincrby('hot:all', 1, key);
}
