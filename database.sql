-- Campus Sports Booking - Database Setup

CREATE DATABASE IF NOT EXISTS campus_sports;
USE campus_sports;

-- 1. USERS TABLE
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
INSERT INTO users (username, password)
VALUES
('admin', SHA2('1234', 256)),
('avishkar', SHA2('12345', 256)),
('student1', SHA2('student123', 256));

-- 2. FACILITIES TABLE
CREATE TABLE facilities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    facility_name VARCHAR(100) NOT NULL UNIQUE,
    facility_type VARCHAR(50)
);
INSERT INTO facilities (facility_name, facility_type)
VALUES
('Football Ground', 'Outdoor'),
('Cricket Ground', 'Outdoor'),
('Basketball Court', 'Outdoor'),
('Badminton Court', 'Indoor'),
('Volleyball Court', 'Outdoor'),
('Table Tennis', 'Indoor');

-- 3. BOOKINGS TABLE
-- Stores booking and fixture information

CREATE TABLE bookings (
    booking_id INT PRIMARY KEY AUTO_INCREMENT,
    -- User and facility details
    username VARCHAR(50) NOT NULL,
    facility_name VARCHAR(100) NOT NULL,
    -- Booking details
    booking_date DATE NOT NULL,
    time_slot VARCHAR(50) NOT NULL,
    purpose VARCHAR(100) NOT NULL,
    -- Fixture details
    sport VARCHAR(30),
    team1 VARCHAR(60),
    team2 VARCHAR(60),
    fixture_date DATE,
    team1_score INT DEFAULT NULL,
    team2_score INT DEFAULT NULL,
    fixture_status VARCHAR(20) DEFAULT NULL,
    -- Booking status
    status VARCHAR(20) NOT NULL DEFAULT 'Confirmed',
    -- Foreign keys
    FOREIGN KEY (username)
        REFERENCES users(username),
    FOREIGN KEY (facility_name)
        REFERENCES facilities(facility_name),
    -- Validation
    CHECK (team1 IS NULL OR team2 IS NULL OR team1 <> team2),
    CHECK (team1_score IS NULL OR team1_score >= 0),
    CHECK (team2_score IS NULL OR team2_score >= 0),
    -- Search index
    INDEX idx_slot_lookup
        (facility_name, booking_date, time_slot, status)
);


-- 4. SAMPLE BOOKINGS AND FIXTURES

INSERT INTO bookings
(
    username,
    facility_name,
    booking_date,
    time_slot,
    purpose,
    sport,
    team1,
    team2,
    fixture_date,
    team1_score,
    team2_score,
    fixture_status,
    status
)
VALUES

-- Regular practice booking
(
    'avishkar',
    'Basketball Court',
    '2026-11-01',
    '4:00 PM - 5:00 PM',
    'Practice',
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    'Confirmed'
),

-- Football fixture
(
    'avishkar',
    'Football Ground',
    '2026-11-02',
    '4:00 PM - 5:00 PM',
    'Football Match',
    'Football',
    'CSE Warriors',
    'ECE Strikers',
    '2026-11-02',
    NULL,
    NULL,
    'Scheduled',
    'Confirmed'
),

-- Cricket fixture
(
    'student1',
    'Cricket Ground',
    '2026-11-03',
    '10:00 AM - 11:00 AM',
    'Cricket Match',
    'Cricket',
    'CSE Challengers',
    'ECE Royals',
    '2026-11-03',
    NULL,
    NULL,
    'Scheduled',
    'Confirmed'
),

-- Completed football fixture
(
    'avishkar',
    'Football Ground',
    '2026-10-05',
    '4:00 PM - 5:00 PM',
    'Football Match',
    'Football',
    'CSE Warriors',
    'ECE Strikers',
    '2026-10-05',
    2,
    1,
    'Completed',
    'Confirmed'
),

-- Completed cricket fixture
(
    'student1',
    'Cricket Ground',
    '2026-10-07',
    '10:00 AM - 11:00 AM',
    'Cricket Match',
    'Cricket',
    'CSE Challengers',
    'ECE Royals',
    '2026-10-07',
    145,
    132,
    'Completed',
    'Confirmed'
);


-- 5. DISPLAY ALL TABLES

SHOW TABLES;

SELECT * FROM users;
SELECT * FROM facilities;
SELECT * FROM bookings;


-- 6. DISPLAY BOOKING AND FIXTURE DETAILS

SELECT
    booking_id,
    username,
    facility_name,
    booking_date,
    time_slot,
    purpose,
    sport,
    team1,
    team2,
    fixture_date,
    team1_score,
    team2_score,
    fixture_status,
    status
FROM bookings;
