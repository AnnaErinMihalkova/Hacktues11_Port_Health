const sequelize = require('../database');  // Import database.js
const { DataTypes } = require('sequelize');

// Load models
const User = require('./user')(sequelize, DataTypes);
const Appointment = require('./appointment')(sequelize, DataTypes);
const Prescription = require('./prescription')(sequelize, DataTypes);
const Message = require('./message')(sequelize, DataTypes);

module.exports = { sequelize, User, Appointment, Prescription, Message };
