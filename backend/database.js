const { Sequelize } = require('sequelize');

const sequelize = new Sequelize('porthealth', 'porthealth_user', 'password123', {
  host: 'localhost',
  dialect: 'postgres'
});

// Test database connection
sequelize.authenticate()
  .then(() => console.log('✅ Database connected successfully!'))
  .catch(err => console.error('❌ Database connection failed:', err));

module.exports = sequelize;
