CREATE DATABASE IF NOT EXISTS mahehub;
USE mahehub;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'organiser', 'student') NOT NULL,
    dept VARCHAR(255),
    reg_no VARCHAR(100),
    year INT
);

-- Default admin account (hardcoded)
INSERT INTO users (name, email, password, role)
VALUES ('Administrator', 'admin@mahehub.com', 'admin123', 'admin');

-- Default organiser accounts (hardcoded)
INSERT INTO users (name, email, password, role)
VALUES 
    ('Organiser One', 'organiser1@mahehub.com', 'org123', 'organiser'),
    ('Organiser Two', 'organiser2@mahehub.com', 'org456', 'organiser');

CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    date DATE,
    time TIME,
    status ENUM('draft', 'pending', 'approve', 'reject') DEFAULT 'pending',
    organiser_id INT,
    FOREIGN KEY (organiser_id) REFERENCES users(id)
);

CREATE TABLE registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    event_id INT,
    registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (event_id) REFERENCES events(id),
    UNIQUE KEY unique_registration (student_id, event_id)
);
