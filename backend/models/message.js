module.exports = (sequelize, DataTypes) => {
    return sequelize.define('Message', {
      content: { type: DataTypes.TEXT, allowNull: false },
      senderId: { type: DataTypes.INTEGER, allowNull: false },
      receiverId: { type: DataTypes.INTEGER, allowNull: false }
    });
  };
  