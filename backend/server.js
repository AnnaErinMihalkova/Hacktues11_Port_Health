const express = require('express');
const http = require('http');
const { Pool } = require('pg');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const nodemailer = require('nodemailer');
const cron = require('node-cron');
const { Server: WebSocketServer } = require('ws');

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

const JWT_SECRET = process.env.JWT_SECRET || 'porthealth-secret';
const PORT = process.env.PORT || 4000;

const pool = require('./db');

// Middleware for JSON parsing
app.use(express.json());

// Authentication middleware for protected routes
const authenticate = (req, res, next) => {
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

// Routes
const authRoutes = require('./routes/auth');
const userRoutes = require('./routes/users');
const appointmentRoutes = require('./routes/appointments');
const prescriptionRoutes = require('./routes/prescriptions');
const chatRoutes = require('./routes/chat');

app.use('/auth', authRoutes);
app.use('/users', authenticate, userRoutes);
app.use('/appointments', authenticate, appointmentRoutes);
app.use('/prescriptions', authenticate, prescriptionRoutes);
app.use('/chat', authenticate, chatRoutes);

// WebSocket connections map (userId -> socket)
const clients = new Map();

wss.on('connection', (socket, request) => {
  // Parse token from query params
  const params = new URL(request.url, `http://${request.headers.host}`).searchParams;
  const token = params.get('token');
  if (!token) {
    socket.close();
    return;
  }
  let user;
  try {
    user = jwt.verify(token, JWT_SECRET);
  } catch (err) {
    socket.close();
    return;
  }
  // Store connection
  socket.userId = user.id;
  clients.set(user.id, socket);
  // Handle incoming messages from this client
  socket.on('message', async (msg) => {
    try {
      const data = JSON.parse(msg);
      const toId = data.to;
      const content = data.content;
      if (!toId || !content) return;
      const fromId = user.id;
      // Only allow sending if toId is provided and content not empty.
      // (Authorization between patient-doctor is assumed via contacts)
      // Save message to DB
      try {
        await pool.query('INSERT INTO messages(from_user, to_user, content) VALUES($1, $2, $3)', [fromId, toId, content]);
      } catch (dbErr) {
        console.error('DB Error inserting message:', dbErr);
      }
      // Forward message to recipient if online
      if (clients.has(toId)) {
        const outMsg = { from: fromId, content: content };
        clients.get(toId).send(JSON.stringify(outMsg));
      }
    } catch (e) {
      console.error('Error handling WS message:', e);
    }
  });
  socket.on('close', () => {
    if (socket.userId) {
      clients.delete(socket.userId);
    }
  });
});

// Email setup (if credentials provided)
let transporter = null;
if (process.env.EMAIL_USER && process.env.EMAIL_PASS) {
  transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASS
    }
  });
}

// Cron job for appointment reminders (runs every minute)
cron.schedule('* * * * *', async () => {
  try {
    // Find appointments in next 60 minutes that are not reminded
    const result = await pool.query(
      "SELECT a.id, a.datetime, a.patient_id, a.doctor_id, u.email AS patient_email, u.name AS patient_name, d.name AS doctor_name " +
      "FROM appointments a JOIN users u ON a.patient_id = u.id JOIN users d ON a.doctor_id = d.id " +
      "WHERE a.datetime > NOW() AND a.datetime <= NOW() + INTERVAL '60 minutes' AND a.reminded = false"
    );
    if (result.rows.length > 0) {
      const remindIds = [];
      for (let row of result.rows) {
        remindIds.push(row.id);
        const patientId = row.patient_id;
        const patientEmail = row.patient_email;
        const patientName = row.patient_name;
        const doctorName = row.doctor_name;
        const doctorId = row.doctor_id;
        // Format appointment time
        const apptTime = new Date(row.datetime).toLocaleString();
        const reminderText = `Dear ${patientName}, this is a reminder of your appointment with Dr. ${doctorName} at ${apptTime}.`;
        // Send email to patient
        if (transporter) {
          try {
            await transporter.sendMail({
              from: process.env.EMAIL_USER,
              to: patientEmail,
              subject: 'Appointment Reminder',
              text: reminderText
            });
          } catch (mailErr) {
            console.error('Email send error:', mailErr);
          }
        } else {
          console.log('Reminder email to', patientEmail, ':', reminderText);
        }
        // Send WebSocket notification to patient if online
        if (clients.has(patientId)) {
          const notif = { type: 'reminder', message: `Reminder: ${reminderText}` };
          clients.get(patientId).send(JSON.stringify(notif));
        }
        // Send WebSocket notification to doctor if online
        if (clients.has(doctorId)) {
          const notif2 = { type: 'reminder', message: `Reminder: You have an upcoming appointment with ${patientName} at ${apptTime}.` };
          clients.get(doctorId).send(JSON.stringify(notif2));
        }
      }
      // Mark these appointments as reminded
      await pool.query('UPDATE appointments SET reminded = true WHERE id = ANY($1)', [remindIds]);
    }
  } catch (err) {
    console.error('Error in reminder cron job:', err);
  }
});

// Initialize database tables and start server
async function initDB() {
  // Create tables if they do not exist
  await pool.query(`CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    theme TEXT DEFAULT 'light'
  )`);
  await pool.query(`CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    datetime TIMESTAMP NOT NULL,
    reason TEXT,
    reminded BOOLEAN DEFAULT FALSE
  )`);
  await pool.query(`CREATE TABLE IF NOT EXISTS prescriptions (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date DATE,
    medication TEXT,
    dosage TEXT
  )`);
  await pool.query(`CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    from_user INTEGER REFERENCES users(id) ON DELETE CASCADE,
    to_user INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )`);
}

initDB().then(() => {
  server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
  });
}).catch(err => {
  console.error('Failed to initialize database:', err);
  process.exit(1);
});
