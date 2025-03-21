// backend/routes/doctors.js
const express = require('express');
const router = express.Router();
const pool = require('../db');

// Search for doctors by name (case-insensitive)
router.get('/search', async (req, res) => {
  try {
    const name = req.query.name;
    if (!name) {
      return res.status(400).json({ message: 'Name query parameter is required' });
    }
    const result = await pool.query(
      "SELECT id, name FROM users WHERE role = 'doctor' AND LOWER(name) LIKE LOWER('%' || $1 || '%')",
      [name]
    );
    return res.json(result.rows);
  } catch (err) {
    console.error('Error searching for doctor:', err);
    res.status(500).json({ message: 'Server error searching for doctor' });
  }
});

module.exports = router;
