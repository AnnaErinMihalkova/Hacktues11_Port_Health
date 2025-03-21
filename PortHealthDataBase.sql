CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    title VARCHAR(50) DEFAULT NULL
);

CREATE TABLE patient_data (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    phone_number VARCHAR(20) NOT NULL,
    height DECIMAL(5,2),
    weight DECIMAL(5,2),
    diet TEXT,
    allergies TEXT,
    last_visit TIMESTAMP,
    visit_reason TEXT
);

CREATE TABLE medical_history (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    history TEXT NOT NULL,
    allergies TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES users(id) ON DELETE CASCADE,
    doctor_id INT REFERENCES users(id) ON DELETE CASCADE,
    appointment_time TIMESTAMP NOT NULL,
    notes TEXT,
    status VARCHAR(50) CHECK (status IN ('scheduled', 'completed', 'canceled')) NOT NULL
);

CREATE TABLE prescriptions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    doctor_id INT REFERENCES users(id) ON DELETE CASCADE,
    medication TEXT NOT NULL,
    instructions TEXT,
    prescribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reminders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) CHECK (type IN ('medicine', 'appointment')) NOT NULL,
    message TEXT NOT NULL,
    remind_at TIMESTAMP NOT NULL
);

CREATE TABLE chats (
    id SERIAL PRIMARY KEY,
    sender_id INT REFERENCES users(id) ON DELETE CASCADE,
    receiver_id INT REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE habits (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    habit_type VARCHAR(100) NOT NULL,
    description TEXT
);

CREAgiE TABLE doctor_visits (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(255) NOT NULL,
    diagnosis TEXT NOT NULL,
    visit_cost DECIMAL(10,2),
    need_followup BOOLEAN NOT NULL,
    followup_date DATE,
    recovery_notes TEXT,
    preparations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prescriptions (
    id SERIAL PRIMARY KEY,
    visit_id INTEGER REFERENCES doctor_visits(id) ON DELETE CASCADE,
    medicine VARCHAR(255) NOT NULL,
    dosage VARCHAR(50) NOT NULL,
    frequency VARCHAR(50) NOT NULL,
    duration VARCHAR(50) NOT NULL
);

ALTER TABLE appointments ADD external_booking_link TEXT;

INSERT INTO appointments (patient_id, doctor_id, appointment_time, external_booking_link, status) 
VALUES (1, 2, '2025-04-01 10:00:00', 'https://superdoc.com/confirm/12345', 'scheduled');

ALTER TABLE medical_history 
ADD created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE prescriptions 
ADD instructions TEXT;

ALTER TABLE users ADD age INT;

ALTER TABLE users ADD gender VARCHAR(10);

SELECT 
    a.id AS appointment_id,
    a.patient_id,
    a.doctor_id,
    u.name AS doctor_name,
    a.appointment_time,
    a.notes,
    a.status,
    a.external_booking_link
FROM 
    appointments a
JOIN 
    users u ON a.doctor_id = u.id;

CREATE VIEW appointment_details AS
SELECT 
    a.id AS appointment_id,
    a.patient_id,
    a.doctor_id,
    u.name AS doctor_name,
    a.appointment_time,
    a.notes,
    a.status,
    a.external_booking_link
FROM 
    appointments a
JOIN 
    users u ON a.doctor_id = u.id;

SELECT * FROM appointment_details;
