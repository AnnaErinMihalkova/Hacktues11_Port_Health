module.exports = (sequelize, DataTypes) => {
    return sequelize.define('Prescription', {
      medicine: { type: DataTypes.STRING, allowNull: false },
      dosage: { type: DataTypes.STRING, allowNull: true },
      patientId: { type: DataTypes.INTEGER, allowNull: false },
      doctorId: { type: DataTypes.INTEGER, allowNull: false }
    });
  };
  