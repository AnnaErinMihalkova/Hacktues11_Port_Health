const express = require('express');
const router = express.Router();
const pool = require('../db');

// Get chat contacts for the logged-in user
router.get('/contacts', async (req, res) => {
  try {
    const userId = req.user.id;
    const role = req.user.role;
    let result;
    if (role === 'patient') {
      result = await pool.query(
        "SELECT DISTINCT d.id, d.name, d.role FROM appointments a JOIN users d ON a.doctor_id = d.id WHERE a.patient_id = $1",
        [userId]
      );
    } else if (role === 'doctor') {
      result = await pool.query(
        "SELECT DISTINCT p.id, p.name, p.role FROM appointments a JOIN users p ON a.patient_id = p.id WHERE a.doctor_id = $1",
        [userId]
      );
    } else {
      return res.status(403).json({ message: 'Access denied' });
    }
    res.json({ contacts: result.rows });
  } catch (err) {
    console.error('Error fetching contacts:', err);
    res.status(500).json({ message: 'Server error fetching contacts' });
  }
});

// Get chat history with a specific contact
router.get('/history', async (req, res) => {
  try {
    const userId = req.user.id;
    const contactId = req.query.with;
    if (!contactId) {
      return res.status(400).json({ message: 'Missing contact id' });
    }
    // Retrieve messages between user and contact
    const result = await pool.query(
      "SELECT from_user, to_user, content, to_char(timestamp, 'YYYY-MM-DD HH24:MI') AS timestamp " +
      "FROM messages WHERE (from_user=$1 AND to_user=$2) OR (from_user=$2 AND to_user=$1) ORDER BY timestamp ASC",
      [userId, contactId]
    );
    res.json({ messages: result.rows });
  } catch (err) {
    console.error('Error fetching chat history:', err);
    res.status(500).json({ message: 'Server error fetching chat history' });
  }
});

module.exports = router;
