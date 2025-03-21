// routes/available_appointments.js
const express = require('express');
const router = express.Router();
const pool = require('../db');

// Get available appointments for a given doctor (only slots that are not booked)
router.get('/', async (req, res) => {
  try {
    const { doctorId } = req.query;
    if (!doctorId) {
      return res.status(400).json({ message: 'doctorId is required' });
    }
    const result = await pool.query(
      `SELECT id, to_char(slot, 'YYYY-MM-DD HH24:MI') as slot
       FROM available_appointments 
       WHERE doctor_id = $1 AND is_booked = false
       ORDER BY slot ASC`,
      [doctorId]
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Error fetching available appointments:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

// (Other endpoints to add or book an available appointment would go here)

module.exports = router;
