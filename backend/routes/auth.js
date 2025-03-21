const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const pool = require('../db');
const JWT_SECRET = process.env.JWT_SECRET || 'porthealth-secret';

const authenticateMid = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  if (!authHeader) return res.status(401).json({ message: 'No token provided' });
  const token = authHeader.split(' ')[1];
  if (!token) return res.status(401).json({ message: 'No token provided' });
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ message: 'Invalid or expired token' });
  }
};

// User signup
router.post('/signup', async (req, res) => {
  try {
    const { name, email, password, role } = req.body;
    if (!name || !email || !password || !role) {
      return res.status(400).json({ message: 'Missing required fields' });
    }
    if (!['patient', 'doctor'].includes(role)) {
      return res.status(400).json({ message: 'Invalid role' });
    }
    // Check if email already exists
    const exist = await pool.query('SELECT id FROM users WHERE email=$1', [email]);
    if (exist.rows.length > 0) {
      return res.status(400).json({ message: 'Email already in use' });
    }
    // Hash password and insert new user
    const hash = await bcrypt.hash(password, 10);
    await pool.query(
      'INSERT INTO users(name, email, password, role) VALUES($1, $2, $3, $4) RETURNING id',
      [name, email, hash, role]
    );
    return res.status(201).json({ message: 'User created successfully' });
  } catch (err) {
    console.error('Signup error:', err);
    res.status(500).json({ message: 'Server error during signup' });
  }
});

// User login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password) {
      return res.status(400).json({ message: 'Email and password required' });
    }
    const result = await pool.query('SELECT * FROM users WHERE email=$1', [email]);
    if (result.rows.length === 0) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }
    const user = result.rows[0];
    const match = await bcrypt.compare(password, user.password);
    if (!match) {
      return res.status(401).json({ message: 'Invalid credentials' });
    }
    // Generate JWT
    const token = jwt.sign({ id: user.id, role: user.role }, JWT_SECRET, { expiresIn: '8h' });
    // Return user info excluding password
    res.json({
      token: token,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role,
        theme: user.theme
      }
    });
  } catch (err) {
    console.error('Login error:', err);
    res.status(500).json({ message: 'Server error during login' });
  }
});

// Profile update (requires auth middleware, add in server or use router with separate instance)
router.put('/profile', authenticateMid, async (req, res) => {
  try {
    // req.user is set by auth middleware in server
    const userId = req.user.id;
    const { name, email, theme } = req.body;
    if (!name || !email) {
      return res.status(400).json({ message: 'Name and email are required' });
    }
    // Check if email is taken by another user
    const check = await pool.query('SELECT id FROM users WHERE email=$1 AND id <> $2', [email, userId]);
    if (check.rows.length > 0) {
      return res.status(400).json({ message: 'Email already in use' });
    }
    const themePref = theme === 'dark' ? 'dark' : 'light';
    const result = await pool.query(
      'UPDATE users SET name=$1, email=$2, theme=$3 WHERE id=$4 RETURNING id, name, email, role, theme',
      [name, email, themePref, userId]
    );
    const updatedUser = result.rows[0];
    res.json({ user: updatedUser });
  } catch (err) {
    console.error('Profile update error:', err);
    res.status(500).json({ message: 'Server error during profile update' });
  }
});

module.exports = router;
