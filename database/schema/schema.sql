-- =============================================================================
-- AI-Based Hostel Food Intelligence & Management System
-- Phase 2 — Complete MySQL Database Schema
-- =============================================================================
-- Database : hostel_food_db
-- Engine   : InnoDB
-- Charset  : utf8mb4
-- =============================================================================

CREATE DATABASE IF NOT EXISTS hostel_food_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE hostel_food_db;

-- Disable FK checks during initial creation (re-enabled at end)
SET FOREIGN_KEY_CHECKS = 0;

-- =============================================================================
-- MODULE: Authentication & Student Information
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Table: users
-- Purpose: Login accounts for admin and student roles (JWT authentication)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INT             NOT NULL AUTO_INCREMENT,
    roll_no         VARCHAR(20)     NULL,
    email           VARCHAR(120)    NOT NULL,
    password_hash   VARCHAR(255)    NOT NULL,
    role            ENUM('admin', 'student') NOT NULL DEFAULT 'student',
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    last_login_at   DATETIME        NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_users_email (email),
    UNIQUE KEY uq_users_roll_no (roll_no),
    INDEX idx_users_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Authentication accounts for admin and students';

-- -----------------------------------------------------------------------------
-- Table: students
-- Purpose: Student profiles, room allocation, contact information
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
    id              INT             NOT NULL AUTO_INCREMENT,
    user_id         INT             NULL,
    roll_no         VARCHAR(20)     NOT NULL,
    name            VARCHAR(100)    NOT NULL,
    department      VARCHAR(100)    NOT NULL,
    year            TINYINT         NOT NULL CHECK (year BETWEEN 1 AND 5),
    gender          ENUM('Male', 'Female', 'Other') NOT NULL,
    phone_number    VARCHAR(15)     NULL,
    parent_contact  VARCHAR(15)     NULL,
    room_number     VARCHAR(20)     NULL,
    hostel_block    VARCHAR(50)     NULL,
    is_active       TINYINT(1)      NOT NULL DEFAULT 1,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_students_roll_no (roll_no),
    UNIQUE KEY uq_students_user_id (user_id),
    INDEX idx_students_department (department),
    INDEX idx_students_hostel_block (hostel_block),
    INDEX idx_students_room (hostel_block, room_number),

    CONSTRAINT fk_students_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Student master records and room allocation';

-- =============================================================================
-- MODULE 1: Biometric Attendance Integration
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Table: attendance
-- Purpose: Entry/exit logs imported from biometric devices (CSV or API)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attendance (
    id              INT             NOT NULL AUTO_INCREMENT,
    roll_no         VARCHAR(20)     NOT NULL,
    entry_time      DATETIME        NULL,
    exit_time       DATETIME        NULL,
    attendance_date DATE            NOT NULL,
    status          ENUM('inside', 'outside', 'on_leave') NOT NULL DEFAULT 'outside',
    source          ENUM('biometric', 'manual', 'api') NOT NULL DEFAULT 'biometric',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_attendance_roll_date (roll_no, attendance_date),
    INDEX idx_attendance_date (attendance_date),
    INDEX idx_attendance_status (attendance_date, status),

    CONSTRAINT fk_attendance_student
        FOREIGN KEY (roll_no) REFERENCES students(roll_no)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Biometric attendance entry and exit logs';

-- =============================================================================
-- MODULE: Leave Management
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Table: leave_requests
-- Purpose: Student leave applications and holiday stay requests
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS leave_requests (
    id              INT             NOT NULL AUTO_INCREMENT,
    roll_no         VARCHAR(20)     NOT NULL,
    start_date      DATE            NOT NULL,
    end_date        DATE            NOT NULL,
    reason          TEXT            NULL,
    leave_type      ENUM('regular', 'holiday_stay') NOT NULL DEFAULT 'regular',
    status          ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
    reviewed_by     INT             NULL,
    reviewed_at     DATETIME        NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_leave_roll (roll_no),
    INDEX idx_leave_dates (start_date, end_date),
    INDEX idx_leave_status (status),
    INDEX idx_leave_active (status, start_date, end_date),

    CONSTRAINT fk_leave_student
        FOREIGN KEY (roll_no) REFERENCES students(roll_no)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_leave_reviewer
        FOREIGN KEY (reviewed_by) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_leave_date_range
        CHECK (end_date >= start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Student leave and holiday stay requests';

-- =============================================================================
-- MODULE 5: Food Menu Management
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Table: food_menus
-- Purpose: Daily menus, special meals, and festival menus
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS food_menus (
    id              INT             NOT NULL AUTO_INCREMENT,
    menu_date       DATE            NOT NULL,
    meal_type       ENUM('Breakfast', 'Lunch', 'Dinner') NOT NULL,
    menu_title      VARCHAR(200)    NOT NULL,
    menu_items      TEXT            NOT NULL,
    is_special      TINYINT(1)      NOT NULL DEFAULT 0,
    description     TEXT            NULL,
    image_path      VARCHAR(255)    NULL,
    created_by      INT             NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_menu_date_meal (menu_date, meal_type),
    INDEX idx_menu_date (menu_date),
    INDEX idx_menu_special (is_special, menu_date),

    CONSTRAINT fk_menu_creator
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Daily and special hostel food menus';

-- =============================================================================
-- MODULE 6: Complaint Management
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Table: complaints
-- Purpose: Student-submitted complaints with status tracking
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS complaints (
    id              INT             NOT NULL AUTO_INCREMENT,
    complaint_id    VARCHAR(20)     NOT NULL,
    roll_no         VARCHAR(20)     NOT NULL,
    category        ENUM(
                        'Electrical Issue',
                        'Room Cleaning',
                        'WiFi Issue',
                        'Food Quality Issue',
                        'Water Issue',
                        'Other'
                    )               NOT NULL,
    description     TEXT            NOT NULL,
    status          ENUM('Open', 'In Progress', 'Resolved') NOT NULL DEFAULT 'Open',
    resolved_by     INT             NULL,
    resolved_at     DATETIME        NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_complaint_id (complaint_id),
    INDEX idx_complaint_roll (roll_no),
    INDEX idx_complaint_status (status),
    INDEX idx_complaint_category (category),

    CONSTRAINT fk_complaint_student
        FOREIGN KEY (roll_no) REFERENCES students(roll_no)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_complaint_resolver
        FOREIGN KEY (resolved_by) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Student complaints and resolution tracking';

-- =============================================================================
-- MODULE 7: Announcements
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Table: announcements
-- Purpose: Hostel-wide notices published by management
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS announcements (
    id              INT             NOT NULL AUTO_INCREMENT,
    title           VARCHAR(200)    NOT NULL,
    description     TEXT            NOT NULL,
    priority        ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    expiry_date     DATE            NULL,
    created_by      INT             NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_announcement_priority (priority),
    INDEX idx_announcement_expiry (expiry_date),
    INDEX idx_announcement_active (expiry_date, created_at),

    CONSTRAINT fk_announcement_creator
        FOREIGN KEY (created_by) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Management announcements for students';

-- =============================================================================
-- MODULE 3: AI/ML Food Prediction & Wastage
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Table: holidays
-- Purpose: Academic/holiday calendar for ML feature (is_holiday flag)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS holidays (
    id              INT             NOT NULL AUTO_INCREMENT,
    holiday_date    DATE            NOT NULL,
    holiday_name    VARCHAR(150)    NOT NULL,
    description     VARCHAR(255)    NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_holiday_date (holiday_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Holiday calendar for food prediction features';

-- -----------------------------------------------------------------------------
-- Table: food_predictions
-- Purpose: ML model output — predicted meal attendance per day
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS food_predictions (
    id                  INT         NOT NULL AUTO_INCREMENT,
    prediction_date     DATE        NOT NULL,
    predicted_breakfast INT         NOT NULL,
    predicted_lunch     INT         NOT NULL,
    predicted_dinner    INT         NOT NULL,
    actual_breakfast    INT         NULL,
    actual_lunch        INT         NULL,
    actual_dinner       INT         NULL,
    total_students      INT         NULL,
    students_inside     INT         NULL,
    students_outside    INT         NULL,
    students_on_leave   INT         NULL,
    is_weekend          TINYINT(1)  NOT NULL DEFAULT 0,
    is_holiday          TINYINT(1)  NOT NULL DEFAULT 0,
    model_version       VARCHAR(50) NULL,
    created_at          DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_prediction_date (prediction_date),
    INDEX idx_prediction_date (prediction_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='AI-predicted and actual meal attendance counts';

-- -----------------------------------------------------------------------------
-- Table: meal_attendance
-- Purpose: Actual students who ate each meal (feeds ML actual_* columns)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS meal_attendance (
    id              INT             NOT NULL AUTO_INCREMENT,
    attendance_date DATE            NOT NULL,
    meal_type       ENUM('Breakfast', 'Lunch', 'Dinner') NOT NULL,
    student_count   INT             NOT NULL DEFAULT 0,
    recorded_by     INT             NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_meal_attendance_date_meal (attendance_date, meal_type),
    INDEX idx_meal_attendance_date (attendance_date),

    CONSTRAINT fk_meal_attendance_recorder
        FOREIGN KEY (recorded_by) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_meal_attendance_count
        CHECK (student_count >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Actual meal attendance counts recorded daily';

-- -----------------------------------------------------------------------------
-- Table: food_wastage
-- Purpose: Food preparation vs consumption vs wastage reports
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS food_wastage (
    id                  INT         NOT NULL AUTO_INCREMENT,
    report_date         DATE        NOT NULL,
    meal_type           ENUM('Breakfast', 'Lunch', 'Dinner') NOT NULL,
    prepared_quantity   INT         NOT NULL,
    consumed_quantity   INT         NOT NULL,
    wasted_quantity     INT         NOT NULL,
    notes               TEXT        NULL,
    recorded_by         INT         NULL,
    created_at          DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_wastage_date_meal (report_date, meal_type),
    INDEX idx_wastage_date (report_date),

    CONSTRAINT fk_wastage_recorder
        FOREIGN KEY (recorded_by) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_wastage_quantities
        CHECK (prepared_quantity >= 0 AND consumed_quantity >= 0 AND wasted_quantity >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Daily food wastage tracking per meal';

SET FOREIGN_KEY_CHECKS = 1;

-- =============================================================================
-- End of Schema
-- =============================================================================
