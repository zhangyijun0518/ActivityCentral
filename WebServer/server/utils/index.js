const md5 = require('md5');
const config = require('../config');
const jwt = require('jsonwebtoken');
const { validationResult } = require('express-validator');
const User = require('../models').users;

// es connection
const { Client } = require('@elastic/elasticsearch');
const AWS = require('aws-sdk');
const connector = require('aws-elasticsearch-connector');

const aws_config = new AWS.Config({
	accessKeyId: 'AKIAIOMQ5YQ5EIVEFU2A',
	secretAccessKey: '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',
	region: 'us-east-2'
});

const bluebird = require('bluebird');
const redis = require('redis');
bluebird.promisifyAll(redis);
const redis_client = (config.debug) ?
redis.createClient()
: redis.createClient(6379, 'activitycentral.ptm5qa.ng.0001.usw1.cache.amazonaws.com');

redis_client.on('connect', () => {
	console.log('connect');
});

redis_client.on('error', err => {
	console.log(err);
});

exports.redis_client = redis_client;

exports.client = new Client({
	...connector(aws_config),
	node: config.es.node
});


/**
 * encrypt user password with salt
 * @param  {String} pwd user password
 * @return {String}     encrypted password
 */
exports.encryptPassword = (pwd) => {
	return md5(pwd + '123');
}

exports.extractToken = (bearer) => {
	return bearer.split(' ')[1];
}

/**
 * sign a jsonwebtoken
 * @param  {Integer} id    user id
 * @param  {String} email  user email
 * @return {String}        json web token
 */
exports.signJWT = (id, email) => {
	return jwt.sign({ id: id, email: email}, config.jwt_secret);
}

/**
 * validate jsonwebtoken from request, add an User instance to the user model
 * @param  {String} value        authorization in headers
 * @param  {Object} options.req  request object
 * @return {Promise}             if validate fail, throw a rejection promise
 */
exports.validateJWT = async (value, {req}) => {
	if (value.split(' ')[0] !== 'Bearer') {
		return Promise.reject('Token format error');
	}
	const token = value.split(' ')[1];
	var decoded;
	try {
		decoded = jwt.verify(token, config.jwt_secret);
	} catch (err) {
		return Promise.reject('Token invalid 1');
	}
	user = await User.findOne({ where: {id: decoded.id, token: token }});
	if (user === null) {
		return Promise.reject('Token invalid 2');
	}
	req.user = user;
}


/**
 * check whether the request has correct parameters
 * @param  {Object} req Request object
 * @return {String}     return null if no error; elsewise return error message
 */
exports.validateRequest = (req) => {
	const errors = validationResult(req);
	if (config.debug && !errors.isEmpty()) {
		console.log(errors);
	}
	return errors.isEmpty() ? null : errors.array()[0].msg;
}

