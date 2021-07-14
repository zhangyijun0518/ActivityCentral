const expect = require('chai').expect;
const request = require('request');
const config = require('../config.js');
const host = config.debug ? "http://localhost:3000" : config.host;

describe("register", () => {
	it("missing parameters", () => {
		expect(host).to.equal('http://localhost:3000');
		console.log(host+'/users');
		// request.post(host+'/users', {
		// 	json: true
		// }, (err, resp, body) => {
		// 	console.log(body);
		// 	expect(body).to.equal('');
		// });
	});

});

// describe("login", () => {

// });

// it("login", done => {
// 	request(config.host + '/login', (err, resp, body) => {
// 		expect(body).to.equal('');
// 		done();
// 	});
// });