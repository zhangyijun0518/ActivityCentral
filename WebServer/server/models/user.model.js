/**
 * User Model
 * @param  {Sequelize} sequelize instance of Sequelize
 * @param  {Sequelize} Sequelize Sequelize
 * @return {Model}           User Model
 */
module.exports = (sequelize, Sequelize) => {
	const User = sequelize.define("user", {
		id: {
			type: Sequelize.DataTypes.INTEGER,
			primaryKey: true,
			autoIncrement: true,
			allowNull: false
		}, name: {
			type: Sequelize.DataTypes.STRING
		}, avatar: {
			type: Sequelize.DataTypes.STRING
		}, email: {
			type: Sequelize.DataTypes.STRING,
			unique: true,
			allowNull: false
		}, pwd: {
			type: Sequelize.DataTypes.STRING,
			allowNull: false
		}, token: {
			type: Sequelize.DataTypes.STRING,
			unique: true
		}, expire_time: {
			type: Sequelize.DataTypes.INTEGER
		}, status: {
			type: Sequelize.DataTypes.INTEGER,
			defaultValue: 0
		}
	}, {
		freezeTableName: true,
		createdAt: 'create_time',
		updatedAt: false
	});

	/**
	 * Check whether the input email has already been used
	 * @param  {String} input_str email to be checked
	 * @return {Boolean}          return true if used, elsewise false
	 */
	User.isEmailTakenAsync = async (input_str) => {
		const user = await User.findOne({ where: { email: input_str }});
		if (user == null) {
			return false;
		} else {
			return true;
		}
	}

	return User;
}