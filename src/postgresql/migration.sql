CREATE TABLE IF NOT EXISTS Users (
    user_id SERIAL PRIMARY KEY,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    name VARCHAR(100)
);


CREATE TABLE IF NOT EXISTS Branch (
    branch_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);


CREATE TABLE IF NOT EXISTS Doctors (
    doctor_id SERIAL PRIMARY KEY,
    branch_id INTEGER REFERENCES Branch(branch_id),
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100)
);


CREATE TABLE IF NOT EXISTS Appointments (
    appointment_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES Users(user_id),
    doctor_id INTEGER REFERENCES Doctors(doctor_id),
    appointment_time TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'scheduled',
    google_event_id VARCHAR(255)
);
