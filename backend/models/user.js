const bcrypt = require('bcrypt');
module.exports = (sequelize, DataTypes) => {
  const User = sequelize.define('User', {
    name: { type: DataTypes.STRING, allowNull: false },
    email: { type: DataTypes.STRING, allowNull: false, unique: true },
    password: { type: DataTypes.STRING, allowNull: false },  // hashed password
    role: { type: DataTypes.STRING, allowNull: false },      // 'doctor' or 'patient'
    doctorId: { type: DataTypes.INTEGER, allowNull: true },  // if patient, their primary doctor's User ID
    theme: { type: DataTypes.STRING, allowNull: false, defaultValue: 'light' } // 'light' or 'dark'
  });
  // Hash password before creating a new user record
  User.beforeCreate(async (user, options) => {
    if (user.password) {
      user.password = await bcrypt.hash(user.password, 10);
    }
  });
  return User;
};
