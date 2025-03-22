const express = require('express');
const router = express.Router();
const pool = require('../db');

// PUT endpoint for updating patient health info (patients only)
router.put('/', async (req, res) => {
  try {
    const userId = req.user.id;
    const { age, weight, allergies, chronic_diseases } = req.body;
    // Insert new record or update if it already exists.
    const result = await pool.query(
      `INSERT INTO patient_info (user_id, age, weight, allergies, chronic_diseases)
       VALUES ($1, $2, $3, $4, $5)
       ON CONFLICT (user_id) DO UPDATE SET
         age = EXCLUDED.age,
         weight = EXCLUDED.weight,
         allergies = EXCLUDED.allergies,
         chronic_diseases = EXCLUDED.chronic_diseases
       RETURNING *`,
      [userId, age, weight, allergies, chronic_diseases]
    );
    res.json({ info: result.rows[0] });
  } catch (err) {
    console.error("Error updating patient info:", err);
    res.status(500).json({ message: "Server error updating patient info" });
  }
});

// GET endpoint for fetching patient health info (accessible by doctors only)
router.get('/', async (req, res) => {
  try {
    const { patientId } = req.query;
    if (!patientId) {
      return res.status(400).json({ message: "patientId is required" });
    }
    if (req.user.role !== "doctor") {
      return res.status(403).json({ message: "Access denied. Only doctors can view patient info." });
    }
    const result = await pool.query(
      "SELECT * FROM patient_info WHERE user_id = $1",
      [patientId]
    );
    if (result.rows.length === 0) {
      return res.status(404).json({ message: "Patient info not found." });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error("Error fetching patient info:", err);
    res.status(500).json({ message: "Server error fetching patient info" });
  }
});

module.exports = router;
