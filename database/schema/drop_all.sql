-- =============================================================================
-- Drop all tables (use with caution — destroys all data)
-- Run: mysql -u root -p hostel_food_db < database/schema/drop_all.sql
-- =============================================================================

USE hostel_food_db;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS food_wastage;
DROP TABLE IF EXISTS meal_attendance;
DROP TABLE IF EXISTS food_predictions;
DROP TABLE IF EXISTS holidays;
DROP TABLE IF EXISTS announcements;
DROP TABLE IF EXISTS complaints;
DROP TABLE IF EXISTS food_menus;
DROP TABLE IF EXISTS leave_requests;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;
