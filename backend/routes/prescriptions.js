const express = require('express');
const router = express.Router();
const pool = require('../db');

// Get prescriptions for logged-in user
router.get('/', async (req, res) => {
  try {
    const userId = req.user.id;
    const role = req.user.role;
    let result;
    if (role === 'patient') {
      result = await pool.query(
        "SELECT p.id, to_char(p.date, 'YYYY-MM-DD') AS date, p.medication, p.dosage, d.name AS doctor_name " +
        "FROM prescriptions p JOIN users d ON p.doctor_id = d.id WHERE p.patient_id = $1 ORDER BY p.date DESC",
        [userId]
      );
    } else if (role === 'doctor') {
      const patientId = req.query.patientId;
      if (patientId) {
        // Only return prescriptions for the given patient by this doctor
        result = await pool.query(
          "SELECT p.id, to_char(p.date, 'YYYY-MM-DD') AS date, p.medication, p.dosage " +
          "FROM prescriptions p WHERE p.patient_id = $1 AND p.doctor_id = $2 ORDER BY p.date DESC",
          [patientId, userId]
        );
      } else {
        // If no patient specified, return all prescriptions by this doctor (with patient name)
        result = await pool.query(
          "SELECT p.id, to_char(p.date, 'YYYY-MM-DD') AS date, p.medication, p.dosage, u.name AS patient_name " +
          "FROM prescriptions p JOIN users u ON p.patient_id = u.id WHERE p.doctor_id = $1 ORDER BY p.date DESC",
          [userId]
        );
      }
    } else {
      return res.status(403).json({ message: 'Access denied' });
    }
    res.json({ prescriptions: result.rows });
  } catch (err) {
    console.error('Error fetching prescriptions:', err);
    res.status(500).json({ message: 'Server error fetching prescriptions' });
  }
});

// Add a new prescription (doctor only)
router.post('/', async (req, res) => {
  try {
    const userId = req.user.id;
    const role = req.user.role;
    if (role !== 'doctor') {
      return res.status(403).json({ message: 'Only doctors can add prescriptions' });
    }
    const { patientId, medication, dosage } = req.body;
    if (!patientId || !medication || !dosage) {
      return res.status(400).json({ message: 'Missing prescription data' });
    }
    // Check patient exists and is a patient
    const patCheck = await pool.query('SELECT id, role FROM users WHERE id=$1', [patientId]);
    if (patCheck.rows.length === 0 || patCheck.rows[0].role !== 'patient') {
      return res.status(400).json({ message: 'Invalid patient' });
    }
    // Optional: ensure that this doctor has a relationship (appointment) with this patient
    const relCheck = await pool.query('SELECT id FROM appointments WHERE patient_id=$1 AND doctor_id=$2', [patientId, userId]);
    if (relCheck.rows.length === 0) {
      return res.status(403).json({ message: 'Cannot prescribe to this patient (no relation)' });
    }
    // Add prescription (date as today)
    await pool.query(
      'INSERT INTO prescriptions(patient_id, doctor_id, date, medication, dosage) VALUES($1, $2, CURRENT_DATE, $3, $4)',
      [patientId, userId, medication, dosage]
    );
    res.status(201).json({ message: 'Prescription added successfully' });
  } catch (err) {
    console.error('Error adding prescription:', err);
    res.status(500).json({ message: 'Server error adding prescription' });
  }
});

module.exports = router;
