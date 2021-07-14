var config = {
	debug: true,
	port: 3000,
	name: 'ActivityCentral',
	host: 'http://ec2-18-144-24-182.us-west-1.compute.amazonaws.com:3000',
	es: {
		index: 'ac',
		doc_type: 'activity',
		node: 'https://search-activitycentral-3ijgjqeqjwhttatbqbhgt445ia.us-east-2.es.amazonaws.com'
	},
	mysql: {
		host: 'activitycentral.cxhuq09r6rdf.us-west-1.rds.amazonaws.com',
		user: 'admin',
		password: 'cmpe295B!',
		database: 'activitycentral'
	},
	mysql_debug: {
		host: 'localhost',
		user: 'root',
		password: '12345678',
		database: 'activitycentral'
	},
	jwt_secret: 'group_rocket_cmpe295'

};

module.exports = config;

