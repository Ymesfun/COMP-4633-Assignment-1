USE campus_events;
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
