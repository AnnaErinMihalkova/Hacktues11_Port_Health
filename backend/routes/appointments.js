const express = require('express');
const router = express.Router();
const pool = require('../db');

// Get appointments for logged-in user
router.get('/', async (req, res) => {
  try {
    const userId = req.user.id;
    const role = req.user.role;
    let result;
    if (role === 'patient') {
      result = await pool.query(
        "SELECT a.id, to_char(a.datetime, 'YYYY-MM-DD HH24:MI') AS datetime, a.reason, d.name AS doctor_name " +
        "FROM appointments a JOIN users d ON a.doctor_id = d.id WHERE a.patient_id = $1 ORDER BY a.datetime ASC",
        [userId]
      );
    } else if (role === 'doctor') {
      result = await pool.query(
        "SELECT a.id, to_char(a.datetime, 'YYYY-MM-DD HH24:MI') AS datetime, a.reason, p.id AS patient_id, p.name AS patient_name " +
        "FROM appointments a JOIN users p ON a.patient_id = p.id WHERE a.doctor_id = $1 ORDER BY a.datetime ASC",
        [userId]
      );
    } else {
      return res.status(403).json({ message: 'Access denied' });
    }
    return res.json({ appointments: result.rows });
  } catch (err) {
    console.error('Error fetching appointments:', err);
    res.status(500).json({ message: 'Server error fetching appointments' });
  }
});

// Create new appointment (patient only)
router.post('/', async (req, res) => {
  try {
    const userId = req.user.id;
    const role = req.user.role;
    if (role !== 'patient') {
      return res.status(403).json({ message: 'Only patients can create appointments' });
    }
    const { doctorId, datetime, reason } = req.body;
    if (!doctorId || !datetime || !reason) {
      return res.status(400).json({ message: 'Missing appointment data' });
    }
    // Check that the doctor exists and has the role 'doctor'
    const docCheck = await pool.query('SELECT id, role FROM users WHERE id = $1', [doctorId]);
    if (docCheck.rows.length === 0 || docCheck.rows[0].role !== 'doctor') {
      return res.status(400).json({ message: 'Invalid doctor selected' });
    }
    // Create the appointment
    await pool.query(
      'INSERT INTO appointments(patient_id, doctor_id, datetime, reason) VALUES($1, $2, $3, $4)',
      [userId, doctorId, datetime, reason]
    );

    // Update the patient's doctorid field if not already set.
    await pool.query(
      'UPDATE users SET doctorid = $1 WHERE id = $2 AND doctorid IS NULL',
      [doctorId, userId]
    );

    res.status(201).json({ message: 'Appointment scheduled successfully' });
  } catch (err) {
    console.error('Error creating appointment:', err);
    res.status(500).json({ message: 'Server error creating appointment' });
  }
});

// Update an appointment (doctor only)
router.put('/:id', async (req, res) => {
  try {
    const userId = req.user.id;
    const role = req.user.role;
    if (role !== 'doctor') {
      return res.status(403).json({ message: 'Only doctors can update appointments' });
    }
    const apptId = req.params.id;
    const { datetime, reason } = req.body;
    // Find the appointment
    const result = await pool.query('SELECT * FROM appointments WHERE id = $1', [apptId]);
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Appointment not found' });
    }
    const appt = result.rows[0];
    if (appt.doctor_id !== userId) {
      return res.status(403).json({ message: 'Not authorized to edit this appointment' });
    }
    const newDate = datetime || appt.datetime;
    const newReason = reason || appt.reason;
    await pool.query('UPDATE appointments SET datetime = $1, reason = $2 WHERE id = $3', [newDate, newReason, apptId]);
    res.json({ message: 'Appointment updated successfully' });
  } catch (err) {
    console.error('Error updating appointment:', err);
    res.status(500).json({ message: 'Server error updating appointment' });
  }
});

// Get taken slots for a doctor
router.get('/taken/:doctorId', async (req, res) => {
  try {
    const doctorId = req.params.doctorId;
    const result = await pool.query(
      'SELECT to_char(datetime, \'YYYY-MM-DD"T"HH24:MI\') as datetime FROM appointments WHERE doctor_id = $1',
      [doctorId]
    );
    res.json({ takenSlots: result.rows.map(r => r.datetime) });
  } catch (err) {
    console.error('Error fetching taken slots:', err);
    res.status(500).json({ message: 'Server error fetching taken slots' });
  }
});

module.exports = router;
