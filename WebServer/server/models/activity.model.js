/**
 * Activity Model
 * @param  {Sequelize} sequelize instance of Sequelize
 * @param  {Sequelize} Sequelize Sequelize
 * @return {Model}           User Model
 */
module.exports = (sequelize, Sequelize) => {
	const Activity = sequelize.define("activity", {
		id: {
			type: Sequelize.DataTypes.INTEGER,
			primaryKey: true,
			autoIncrement: true,
			allowNull: false
		}, uuid: {
			type: Sequelize.DataTypes.STRING,
			unique: true
		}, name: {
			type: Sequelize.DataTypes.STRING
		}, date: {
			type: Sequelize.DataTypes.INTEGER
		}, price: {
			type: Sequelize.DataTypes.STRING,
			allowNull: false
		}, thumbnail: {
			type: Sequelize.DataTypes.STRING,
			allowNull: false
		}, location: {
			type: Sequelize.DataTypes.STRING
		}
	}, {
		freezeTableName: true,
		createdAt: 'create_time',
		updatedAt: 'update_time'
	});

	return Activity;
}