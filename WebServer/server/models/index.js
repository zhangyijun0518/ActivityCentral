const config = require('../config.js');
const Sequelize = require('sequelize');
const dbConfig = !config.debug ? config.mysql : config.mysql_debug;
const sequelize = new Sequelize(dbConfig.database, dbConfig.user, dbConfig.password, {
	host: dbConfig.host,
	dialect: 'mysql',
	pool: {
		max: 5,
		min: 0,
		acquire: 30000,
		idle: 10000
	}
});

const db = {};

db.sequelize = sequelize;
db.Sequelize = Sequelize;

db.users = require('./user.model')(sequelize, Sequelize);
db.activities = require('./activity.model')(sequelize, Sequelize);

module.exports = db;

