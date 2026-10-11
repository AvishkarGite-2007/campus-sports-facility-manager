
CREATE DATABASE IF NOT EXISTS campus_sports;
USE campus_sports;

DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS facilities;
DROP TABLE IF EXISTS users;


-- =========================================
-- 1. USERS TABLE
-- Passwords are stored as SHA-256 hashes, not plain text.
-- =========================================

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

INSERT INTO users (username, password)
VALUES
('admin',    SHA2('1234', 256)),
('avishkar', SHA2('12345', 256)),
('student1', SHA2('student123', 256));


-- =========================================
-- 2. FACILITIES TABLE
-- =========================================

CREATE TABLE facilities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    facility_name VARCHAR(100) NOT NULL UNIQUE,
    facility_type VARCHAR(50)
);

INSERT INTO facilities (facility_name, facility_type)
VALUES
('Football Ground',  'Outdoor'),
('Cricket Ground',   'Outdoor'),
('Basketball Court', 'Outdoor'),
('Badminton Court',  'Indoor'),
('Volleyball Court', 'Outdoor'),
('Table Tennis',     'Indoor');


-- =========================================
-- 3. BOOKINGS TABLE
-- booking_date is now a real DATE column so sorting and
-- filtering by date work correctly.
-- =========================================

CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    facility_name VARCHAR(100) NOT NULL,
    booking_date DATE NOT NULL,
    time_slot VARCHAR(50) NOT NULL,
    purpose VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Confirmed',
    FOREIGN KEY (username) REFERENCES users(username),
    FOREIGN KEY (facility_name) REFERENCES facilities(facility_name),
    INDEX idx_slot_lookup (facility_name, booking_date, time_slot, status)
);

-- Sample bookings (delete these lines if you want an empty table)
INSERT INTO bookings
(username, facility_name, booking_date, time_slot, purpose)
VALUES
('avishkar', 'Basketball Court', '2026-10-12', '4:00 PM - 5:00 PM', 'Practice'),
('avishkar', 'Football Ground',  '2026-10-13', '8:00 AM - 9:00 AM', 'Training');


-- =========================================
-- CHECK THE DATABASE
-- =========================================

SELECT * FROM users;
SELECT * FROM facilities;
SELECT * FROM bookings;