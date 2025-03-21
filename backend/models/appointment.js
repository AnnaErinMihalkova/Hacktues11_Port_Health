module.exports = (sequelize, DataTypes) => {
    return sequelize.define('Appointment', {
      datetime: { type: DataTypes.DATE, allowNull: false },
      description: { type: DataTypes.STRING, allowNull: true },
      patientId: { type: DataTypes.INTEGER, allowNull: false },
      doctorId: { type: DataTypes.INTEGER, allowNull: false }
    });
  };
  