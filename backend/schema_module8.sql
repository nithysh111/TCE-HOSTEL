-- Module 8: Fee & Fine Management System Schema

CREATE TABLE IF NOT EXISTS hostel_fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fee_id VARCHAR(30) NOT NULL UNIQUE,
    roll_no VARCHAR(20) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    hostel_block VARCHAR(50),
    room_number VARCHAR(20),
    fee_amount DECIMAL(10, 2) NOT NULL,
    due_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_hostel_fees_roll_no ON hostel_fees(roll_no);
CREATE INDEX IF NOT EXISTS idx_hostel_fees_status ON hostel_fees(status);

CREATE TABLE IF NOT EXISTS fines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fine_id VARCHAR(30) NOT NULL UNIQUE,
    roll_no VARCHAR(20) NOT NULL,
    student_name VARCHAR(100) NOT NULL,
    fine_amount DECIMAL(10, 2) NOT NULL,
    fine_reason VARCHAR(100) NOT NULL,
    fine_description TEXT,
    issued_date DATE NOT NULL,
    due_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    created_by VARCHAR(120) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_fines_roll_no ON fines(roll_no);
CREATE INDEX IF NOT EXISTS idx_fines_status ON fines(status);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id VARCHAR(30) NOT NULL UNIQUE,
    roll_no VARCHAR(20) NOT NULL,
    fee_id INTEGER REFERENCES hostel_fees(id),
    fine_id INTEGER REFERENCES fines(id),
    razorpay_order_id VARCHAR(100) NOT NULL UNIQUE,
    razorpay_payment_id VARCHAR(100) UNIQUE,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    transaction_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_payments_roll_no ON payments(roll_no);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(20) NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_notifications_roll_no ON notifications(roll_no);

CREATE TABLE IF NOT EXISTS fine_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fine_id VARCHAR(30) NOT NULL,
    action VARCHAR(50) NOT NULL,
    changed_by VARCHAR(120) NOT NULL,
    old_data TEXT,
    new_data TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_fine_audit_fine_id ON fine_audit_logs(fine_id);
