-- SQL schema for bookings
-- This creates a table suitable for storing the booking data from the form.

CREATE TABLE bookings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  appointment_date TEXT NOT NULL,
  phone TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Example: insert a booking
-- INSERT INTO bookings (name, email, appointment_date, phone) VALUES ('Alice', 'alice@example.com', '2025-10-20', '1234567890');

-- Query all bookings
-- SELECT * FROM bookings ORDER BY created_at DESC;
