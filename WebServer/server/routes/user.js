/**
 * module for user
 * POST /user [create a user]
 * POST /login [user login]
 */
const express = require('express');
const jwt = require('jsonwebtoken');
const express_jwt = require('express-jwt');
const router = express.Router();
const config = require('../config.js');
const User = require('../models').users;
const utils = require('../utils');
const { body, header, validationResult } = require('express-validator');


// create a new user
router.post('/users', [
		body('name').not().isEmpty().withMessage('Name empty'),
		body('pwd').not().isEmpty().withMessage('Password empty')
			.isLength({ min: 8 }).withMessage('Password too short'),
		body('email').not().isEmpty().withMessage('Email empty')
			.isEmail().withMessage('Email format error.')
			.custom(value => {
				return User.isEmailTakenAsync(value).then(taken => {
					if (taken) {
						return Promise.reject('Email address has already been taken.')
					}
				});
			})
], (req, res) => {
	const err_msg = utils.validateRequest(req);
	if (err_msg !== null) {
		return res.json({ err: err_msg });
	}

	User.create({
		name: req.body.name,
		email: req.body.email,
		pwd: utils.encryptPassword(req.body.pwd)
	}).then(user => {
		user.token = utils.signJWT(user.id, req.body.email);
		return user.save();
	}).then(user => {
		return res.json({ id: user.id, token: user.token });
	}).catch(err => {
		return res.json({ err: err.name });
	});
});

// get user info
router.get('/user', [
		header('authorization').custom(utils.validateJWT)
	], (req, res) => {
		const err_msg = utils.validateRequest(req);
		if (err_msg !== null) {
			return res.json({ err: err_msg });
		}
		console.log(req.user);
		return res.json({
			name: req.user.name,
			email: req.user.email
		});
});

// user login
router.post('/login', [
	body('email').not().isEmpty().withMessage('Email empty'),
	body('pwd').not().isEmpty().withMessage('Pwd empty')
		.custom((value, {req}) => {
			return User.findOne({ where: {
				email: req.body.email,
				pwd: utils.encryptPassword(value)
			}}).then(user => {
				if (user == null) {
					return Promise.reject('Incorrect email or password');
				}
				req._user = user;
			})
		})
], (req, res) => {
	const err_msg = utils.validateRequest(req);
	if (err_msg !== null) {
		return res.json({ err: err_msg });
	}

	req._user.token = utils.signJWT(req._user.id, req._user.email);
	req._user.save().then(() => {
		return res.json({ token: req._user.token });
	}).catch(err => {
		return res.json({ err: err });
	})
});


// user logout
router.post('/logout',[
		header('authorization').custom(utils.validateJWT)
	], (req, res) => {
		const err_msg = utils.validateRequest(req);
		if (err_msg !== null) {
			return res.json({ err: err_msg });
		}

		req.user.token = null;
		req.user.save().then(() => {
			return res.json({ status: true });
		}).catch(err => {
			return res.json({ err: 'token doesn\'t match' })
		});
	}
);




module.exports = router;