const express = require('express');
const router = express.Router();
const pool = require('../db');

// GET messages for a conversation room.
// Example: GET /messages?room=doctorId-patientId
router.get('/', async (req, res) => {
  try {
    const room = req.query.room;
    if (!room) {
      return res.status(400).json({ message: 'Room parameter is required' });
    }
    // Join messages with users to get sender's name.
    const result = await pool.query(
      `SELECT m.id, m.from_user, u.name AS sender_name, m.to_user, m.content, 
              to_char(m.timestamp, 'YYYY-MM-DD HH24:MI') as timestamp
       FROM messages m
       JOIN users u ON m.from_user = u.id
       WHERE m.room = $1
       ORDER BY m.timestamp ASC`,
      [room]
    );
    res.json({ messages: result.rows });
  } catch (err) {
    console.error('Error fetching messages:', err);
    res.status(500).json({ message: 'Server error fetching messages' });
  }
});

module.exports = router;
