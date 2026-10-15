CREATE DATABASE IF NOT EXISTS campus_events;
USE campus_events;

CREATE TABLE IF NOT EXISTS events(
  event_id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(100) NOT NULL,
  location VARCHAR(100) NOT NULL,
  start_datetime DATETIME NOT NULL,
  capacity INT NOT NULL CHECK (capacity > 0)
);

CREATE TABLE IF NOT EXISTS participants (
  participant_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS registrations(
  registration_id INT AUTO_INCREMENT PRIMARY KEY,
  event_id INT NOT NULL,
  location VARCHAR(100) NOT NULL,
  start_datetime NOT NULL,
  capacity INT NOT NULL CHECK (capacity > 0)
);

CREATE TABLE IF NOT EXISTS participants (
  participant_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS registrations (
  registration_id INT AUTO_INCREMENT PRIMARY KEY,
  event_id INT NOT NULL,
  participant_id INT NOT NULL
  registration_datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE RESTRICT,
  FOREIGN KEY (participant_id) REFERENCES participants(participant_id),
  UNIQUE (event_id, participant_id)
);

-- Seed information below
INSERT INTO participants (name, email) VALUES
  ('John Doe', 'jdoe101@mtroyal.ca'),
  ('Jane Doe', 'jdoe212@mtroyal.ca'),
  ('Tony Stark', 'tstar130@mtroyal.ca'),
  ('Peter Parker', 'Ppark471@mtroyal.ca'),
  ('Charlie Brown', 'cbrow301@mtroyal.ca');

INSERT INTO events (title, location, start_datetime, capacity) VALUES
  ('Pottery Workshop', 'Art Studio', '2026-11-01 14:00:00', 10),
  ('Board Game Night', 'Wyckham House', '2026-11-05 18:00:00', 20),
  ('Photography Walk', 'East Gate', '2026-11-10 09:00:00', 15);

INSERT INTO registrations (event_id, participant_id) VALUES
  (1, 1),
  (1, 2),
  (2, 3);
