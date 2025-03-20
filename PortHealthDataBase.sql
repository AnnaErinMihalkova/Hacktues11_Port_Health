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

ALTER TABLE appointments ADD external_booking_link TEXT;

INSERT INTO appointments (patient_id, doctor_id, appointment_time, external_booking_link, status) 
VALUES (1, 2, '2025-04-01 10:00:00', 'https://superdoc.com/confirm/12345', 'scheduled');

ALTER TABLE medical_history 
ADD created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE prescriptions 
ADD instructions TEXT;

ALTER TABLE users ADD age INT;

ALTER TABLE users ADD gender VARCHAR(10);


