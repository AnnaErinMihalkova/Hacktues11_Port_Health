const express = require('express');
const router = express.Router();
const pool = require('../db');

// Get list of users (filtered by role)
router.get('/', async (req, res) => {
  try {
    const roleFilter = req.query.role;
    if (roleFilter === 'doctor') {
      const result = await pool.query("SELECT id, name, email, role FROM users WHERE role='doctor'");
      return res.json({ doctors: result.rows });
    } else if (roleFilter === 'patient') {
      // Optionally, restrict patient listing (not generally allowed in this app)
      return res.status(403).json({ message: 'Access denied' });
    } else {
      // If no filter or unsupported, return all doctors by default
      const result = await pool.query("SELECT id, name, email, role FROM users WHERE role='doctor'");
      return res.json({ doctors: result.rows });
    }
  } catch (err) {
    console.error('Error fetching users:', err);
    res.status(500).json({ message: 'Server error fetching users' });
  }
});

module.exports = router;
