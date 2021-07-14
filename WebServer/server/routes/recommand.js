const express = require('express');
const router = express.Router();
const config = require('../config.js');
const utils = require('../utils');
const jwt = require('jsonwebtoken');

const redis_client = utils.redis_client;
const es_client = utils.client;

router.get('/recommand', async (req, res) => {
	// process token
	var redis_key = '';
	var keys = [];
	if (req.headers.authorization != null) {
		const token = req.headers.authorization.split(' ')[1];
		var decoded;
		try {
			decoded = jwt.verify(token, config.jwt_secret);
			redis_key = 'hot:' + decoded.id;
			keys = await redis_client.zrevrangeAsync(redis_key, 0, 3);
		} catch (err) {
			return res.json({err: err});
		}
	}
	// add to three keys
	if (keys.length < 3) {
		var keys_all = await redis_client.zrevrangeAsync('hot:all', 0, 6);
		for (var index in keys_all) {
			if (keys.includes(keys_all[index])) {
				continue;
			}
			if (keys.length == 3) {
				break;
			}
			keys.push(keys_all[index]);
		}
	}

	const es_query = {
		index: config.es.index,
		type: config.es.doc_type,
		// size: 10,
		// from: 0,
		body: {query: {bool: {
			must: [{
				multi_match: {
					query: keys.join(' '),
					fields: ['name', 'tag']
				}
			}],
			should: [{
				range: {
					activity_date: {gte: Date.now()/1000}
				}
			}]
		}}},
		// sort: ['activity_date:asc'],
		// _source: ['name', 'activity_date', 'price', 'thumbnail', 'tags', 'location', 'state', 'city']
	};

	try {
		const count = await es_client.count(es_query).catch(err => {
			throw err;
		})

		if (count.body.count <= 10) {
			es_query.from = 0;
		} else {
			const offset = count.body.count - 10;

			es_query.from = Math.floor(Math.random() * offset);
		}
		es_query.size = 10;
		es_query.sort = ['activity_date:asc'];
		es_query._source = ['name', 'activity_date', 'price', 'thumbnail', 'tags', 'location', 'state', 'city'];

		const {body} = await es_client.search(es_query).catch(err => {
			throw err;
		});

		var result = [];
		for (var hit of body.hits.hits) {
			result.push({
				id: hit._id,
				date: hit._source.activity_date,
				name: hit._source.name,
				price: hit._source.price,
				thumbnail: hit._source.thumbnail,
				location: hit._source.location,
				state: hit._source.state,
				city: hit._source.city,
				// tags: hit._source.tags
			});
		}
		return res.json({
			count: count.body.count <= 10 ? count.body.count : 10,
			results: result
		});
	} catch (err) {
		return res.json({msg: err});
	}

});

module.exports = router;