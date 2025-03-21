const express = require('express');
const router = express.Router();
const pool = require('../db');

// GET prescriptions for logged-in user
router.get('/', async (req, res) => {
  try {
    const userId = req.user.id;
    const role = req.user.role;
    let query, params;
    if (role === 'doctor') {
      // For a doctor, fetch prescriptions they have written, including the patient's name.
      query = `
        SELECT p.id,
               to_char(p.start_date, 'YYYY-MM-DD') AS start_date,
               to_char(p.end_date, 'YYYY-MM-DD') AS end_date,
               p.medication, 
               p.dosage, 
               p.dose_times,
               u.name AS patient_name
        FROM prescriptions p 
        JOIN users u ON p.patient_id = u.id
        WHERE p.doctor_id = $1
        ORDER BY p.start_date DESC
      `;
      params = [userId];
    } else if (role === 'patient') {
      // For a patient, fetch prescriptions that have been written for them, including the doctor's name.
      query = `
        SELECT p.id,
               to_char(p.start_date, 'YYYY-MM-DD') AS start_date,
               to_char(p.end_date, 'YYYY-MM-DD') AS end_date,
               p.medication, 
               p.dosage, 
               p.dose_times,
               u.name AS doctor_name
        FROM prescriptions p 
        JOIN users u ON p.doctor_id = u.id
        WHERE p.patient_id = $1
        ORDER BY p.start_date DESC
      `;
      params = [userId];
    } else {
      return res.status(403).json({ message: 'Access denied' });
    }
    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (err) {
    console.error('Error fetching prescriptions:', err);
    res.status(500).json({ message: 'Server error fetching prescriptions' });
  }
});

// POST a new prescription (only for doctors)
router.post('/', async (req, res) => {
  try {
    const userId = req.user.id;
    const role = req.user.role;
    if (role !== 'doctor') {
      return res.status(403).json({ message: 'Only doctors can add prescriptions' });
    }
    // Expect the following keys in the payload:
    // patientId, medicine, dosage, start_date, end_date, dose_times (an array)
    const { patientId, medicine, dosage, start_date, end_date, dose_times } = req.body;
    if (!patientId || !medicine || !dosage || !start_date || !end_date || !dose_times) {
      return res.status(400).json({ message: 'Missing prescription data' });
    }
    // Insert prescription into the database.
    await pool.query(
      `INSERT INTO prescriptions(patient_id, doctor_id, start_date, end_date, medication, dosage, dose_times)
       VALUES($1, $2, $3, $4, $5, $6, $7)`,
      [patientId, userId, start_date, end_date, medicine, dosage, dose_times]
    );
    res.status(201).json({ message: 'Prescription added successfully' });
  } catch (err) {
    console.error('Error adding prescription:', err);
    res.status(500).json({ message: 'Server error adding prescription' });
  }
});

module.exports = router;
