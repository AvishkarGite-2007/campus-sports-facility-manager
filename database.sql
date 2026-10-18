-- =========================================
-- Campus Sports Booking - database setup
-- Tables: users, facilities, bookings, teams, fixtures
-- WARNING: this script drops and recreates all five tables,
-- so any existing data in them will be lost.
-- =========================================

CREATE DATABASE IF NOT EXISTS campus_sports;
USE campus_sports;

DROP TABLE IF EXISTS fixtures;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS facilities;
DROP TABLE IF EXISTS users;


-- =========================================
-- 1. USERS TABLE
-- Passwords are stored as SHA-256 hashes, not plain text.
-- The user named 'admin' can schedule fixtures and enter results.
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
-- booking_date is a real DATE column so sorting and
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
-- 4. TEAMS TABLE
-- =========================================

CREATE TABLE teams (
    team_id INT PRIMARY KEY AUTO_INCREMENT,
    team_name VARCHAR(60) NOT NULL UNIQUE,
    sport VARCHAR(30) NOT NULL
);

INSERT INTO teams (team_name, sport)
VALUES
('CSE Warriors',     'Football'),
('ECE Strikers',     'Football'),
('Mech Titans',      'Football'),
('Civil Rangers',    'Football'),
('CSE Challengers',  'Cricket'),
('ECE Royals',       'Cricket'),
('Mech Super Kings', 'Cricket'),
('CSE Hoopers',      'Basketball'),
('ECE Dunkers',      'Basketball'),
('Mech Ballers',     'Basketball');


-- =========================================
-- 5. FIXTURES TABLE (team matches)
-- A fixture also blocks its ground for that date and time slot,
-- so nobody can book the same slot.
-- team1_score / team2_score stay NULL until the admin enters a result.
-- status is 'Scheduled' or 'Completed'.
-- =========================================

CREATE TABLE fixtures (
    fixture_id INT AUTO_INCREMENT PRIMARY KEY,
    sport VARCHAR(30) NOT NULL,
    team1 VARCHAR(60) NOT NULL,
    team2 VARCHAR(60) NOT NULL,
    facility_name VARCHAR(100) NOT NULL,
    fixture_date DATE NOT NULL,
    time_slot VARCHAR(50) NOT NULL,
    team1_score INT NULL,
    team2_score INT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Scheduled',
    FOREIGN KEY (team1) REFERENCES teams(team_name),
    FOREIGN KEY (team2) REFERENCES teams(team_name),
    FOREIGN KEY (facility_name) REFERENCES facilities(facility_name),
    CHECK (team1 <> team2),
    INDEX idx_fixture_slot (facility_name, fixture_date, time_slot, status)
);

-- Sample fixtures: some already played, some coming up
INSERT INTO fixtures
(sport, team1, team2, facility_name, fixture_date, time_slot, team1_score, team2_score, status)
VALUES
('Football',   'CSE Warriors',    'ECE Strikers',     'Football Ground',  '2026-10-05', '4:00 PM - 5:00 PM',   2,   1,   'Completed'),
('Football',   'Mech Titans',     'Civil Rangers',    'Football Ground',  '2026-10-06', '4:00 PM - 5:00 PM',   0,   0,   'Completed'),
('Football',   'CSE Warriors',    'Mech Titans',      'Football Ground',  '2026-10-09', '4:00 PM - 5:00 PM',   3,   1,   'Completed'),
('Football',   'ECE Strikers',    'Civil Rangers',    'Football Ground',  '2026-10-10', '4:00 PM - 5:00 PM',   2,   2,   'Completed'),
('Cricket',    'CSE Challengers', 'ECE Royals',       'Cricket Ground',   '2026-10-07', '10:00 AM - 11:00 AM', 145, 132, 'Completed'),
('Basketball', 'CSE Hoopers',     'ECE Dunkers',      'Basketball Court', '2026-10-08', '6:00 PM - 7:00 PM',   58,  52,  'Completed'),
('Football',   'ECE Strikers',    'Mech Titans',      'Football Ground',  '2026-10-21', '4:00 PM - 5:00 PM',   NULL, NULL, 'Scheduled'),
('Cricket',    'ECE Royals',      'Mech Super Kings', 'Cricket Ground',   '2026-10-22', '8:00 AM - 9:00 AM',   NULL, NULL, 'Scheduled'),
('Football',   'CSE Warriors',    'Civil Rangers',    'Football Ground',  '2026-10-23', '6:00 PM - 7:00 PM',   NULL, NULL, 'Scheduled'),
('Basketball', 'Mech Ballers',    'CSE Hoopers',      'Basketball Court', '2026-10-24', '4:00 PM - 5:00 PM',   NULL, NULL, 'Scheduled');


-- =========================================
-- CHECK THE DATABASE
-- =========================================

SELECT * FROM users;
SELECT * FROM facilities;
SELECT * FROM bookings;
SELECT * FROM teams;
SELECT * FROM fixtures;
