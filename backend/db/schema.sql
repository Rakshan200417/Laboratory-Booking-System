-- =====================================================================
-- University Laboratory Booking and Management System
-- SQLite schema generated from Group 13 ER diagram
-- =====================================================================

PRAGMA foreign_keys = ON;

-- ---------- CORE (must-have for the demo) ----------

CREATE TABLE IF NOT EXISTS ROLES (
    role_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name   TEXT UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS DEPARTMENTS (
    department_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT UNIQUE NOT NULL,
    faculty         TEXT,
    description     TEXT,
    status          TEXT
);

CREATE TABLE IF NOT EXISTS USERS (
    user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id     INTEGER NOT NULL,
    e_id        TEXT UNIQUE NOT NULL,      -- University E-ID
    name        TEXT NOT NULL,
    email       TEXT UNIQUE,
    phone       TEXT,
    department  TEXT,
    password    TEXT NOT NULL DEFAULT 'changeme',  -- plain for demo only; hash in real use
    status      TEXT DEFAULT 'Active',
    created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES ROLES(role_id)
);

CREATE TABLE IF NOT EXISTS STUDENTS (
    student_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER UNIQUE NOT NULL,
    year_of_study INTEGER,
    index_number TEXT,
    program      TEXT,
    batch        TEXT,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

CREATE TABLE IF NOT EXISTS LECTURERS (
    lecturer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER UNIQUE NOT NULL,
    employee_id   TEXT UNIQUE,
    designation   TEXT,
    department    TEXT,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

CREATE TABLE IF NOT EXISTS LABORATORIES (
    laboratory_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    laboratory_name TEXT UNIQUE NOT NULL,
    laboratory_code TEXT UNIQUE NOT NULL,
    location        TEXT,
    capacity        INTEGER,
    description     TEXT,
    status          TEXT DEFAULT 'Available'   -- Available / Unavailable / Maintenance
);

CREATE TABLE IF NOT EXISTS LAB_EQUIPMENT (
    equipment_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    laboratory_id      INTEGER NOT NULL,
    equipment_name     TEXT NOT NULL,
    quantity_total     INTEGER NOT NULL,
    quantity_available INTEGER NOT NULL,
    condition          TEXT,
    status             TEXT DEFAULT 'Available',  -- Available / Unavailable / Maintenance
    description        TEXT,
    FOREIGN KEY (laboratory_id) REFERENCES LABORATORIES(laboratory_id)
);

CREATE TABLE IF NOT EXISTS TIME_SLOTS (
    time_slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_name    TEXT NOT NULL,
    start_time   TEXT NOT NULL,
    end_time     TEXT NOT NULL,
    description  TEXT
);

CREATE TABLE IF NOT EXISTS BOOKINGS (
    booking_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    laboratory_id INTEGER NOT NULL,
    time_slot_id  INTEGER,               -- nullable
    purpose       TEXT,
    booking_date  TEXT NOT NULL,          -- 'YYYY-MM-DD'
    start_time    TEXT NOT NULL,          -- 'HH:MM'
    end_time      TEXT NOT NULL,          -- 'HH:MM'
    status        TEXT DEFAULT 'Pending', -- Pending / Approved / Rejected / Cancelled / Completed
    created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at    TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (laboratory_id) REFERENCES LABORATORIES(laboratory_id),
    FOREIGN KEY (time_slot_id) REFERENCES TIME_SLOTS(time_slot_id)
);

CREATE TABLE IF NOT EXISTS APPROVALS (
    approval_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id   INTEGER NOT NULL,
    approved_by  INTEGER NOT NULL,       -- user_id of admin/staff
    decision     TEXT,                   -- Approved / Rejected
    remarks      TEXT,
    approved_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES BOOKINGS(booking_id),
    FOREIGN KEY (approved_by) REFERENCES USERS(user_id)
);

-- ---------- STRETCH ----------

CREATE TABLE IF NOT EXISTS BOOKING_DETAILS (
    booking_detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id        INTEGER NOT NULL,
    equipment_id       INTEGER NOT NULL,
    quantity           INTEGER NOT NULL,
    remarks             TEXT,
    FOREIGN KEY (booking_id) REFERENCES BOOKINGS(booking_id),
    FOREIGN KEY (equipment_id) REFERENCES LAB_EQUIPMENT(equipment_id)
);

CREATE TABLE IF NOT EXISTS CANCELLATIONS (
    cancellation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id      INTEGER NOT NULL,
    cancelled_by    INTEGER NOT NULL,
    reason          TEXT,
    cancelled_at    TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES BOOKINGS(booking_id),
    FOREIGN KEY (cancelled_by) REFERENCES USERS(user_id)
);

CREATE TABLE IF NOT EXISTS NOTIFICATIONS (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    booking_id      INTEGER,
    message         TEXT,
    type            TEXT,
    is_read         INTEGER DEFAULT 0,
    created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (booking_id) REFERENCES BOOKINGS(booking_id)
);

CREATE TABLE IF NOT EXISTS AUDIT_LOG (
    audit_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    action_type     TEXT NOT NULL,
    entity_name     TEXT,
    record_id       INTEGER,
    old_value       TEXT,
    new_value       TEXT,
    action_timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

CREATE TABLE IF NOT EXISTS STORAGE_LOCATIONS (
    location_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    location_name TEXT NOT NULL,
    building      TEXT,
    floor         TEXT,
    room          TEXT,
    description   TEXT,
    status        TEXT
);

CREATE TABLE IF NOT EXISTS REPORT_LOGS (
    report_log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    report_type   TEXT,
    parameters    TEXT,
    generated_at  TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

-- ---------- SEED DATA ----------

INSERT OR IGNORE INTO ROLES (role_id, role_name, description) VALUES
(1, 'Administrator', 'Laboratory staff who manage the system'),
(2, 'Student', 'University student'),
(3, 'Lecturer', 'University lecturer');

INSERT OR IGNORE INTO USERS (user_id, role_id, e_id, name, email, phone, department, password, status) VALUES
(1, 1, 'ADMIN001', 'Admin', 'admin@uni.lk', '0770000000', 'Nano Science', 'admin123', 'Active'),
(2, 2, '249109', 'Student A', 'studenta@uni.lk', '0771111111', 'Nano Science', 'pass123', 'Active'),
(3, 3, 'LEC001', 'Dr. Perera', 'perera@uni.lk', '0772222222', 'Nano Science', 'pass123', 'Active');

INSERT OR IGNORE INTO STUDENTS (student_id, user_id, year_of_study, index_number, program, batch) VALUES
(1, 2, 2, '249109', 'BSc Nano Science', '2024');

INSERT OR IGNORE INTO LECTURERS (lecturer_id, user_id, employee_id, designation, department) VALUES
(1, 3, 'EMP001', 'Senior Lecturer', 'Nano Science');

INSERT OR IGNORE INTO LABORATORIES (laboratory_id, laboratory_name, laboratory_code, location, capacity, description, status) VALUES
(1, 'Nano Materials Lab', 'LAB-01', 'Technology Building', 30, 'Nano materials research lab', 'Available'),
(2, 'Chemistry Lab', 'LAB-02', 'Science Building', 25, 'General chemistry lab', 'Available'),
(3, 'Physics Lab', 'LAB-03', 'Science Building', 20, 'Physics practical lab', 'Under Maintenance');

INSERT OR IGNORE INTO LAB_EQUIPMENT (equipment_id, laboratory_id, equipment_name, quantity_total, quantity_available, condition, status) VALUES
(1, 1, 'Microscope', 5, 5, 'Good', 'Available'),
(2, 1, 'Centrifuge', 2, 2, 'Good', 'Available'),
(3, 1, 'Spectrophotometer', 1, 1, 'Good', 'Available'),
(4, 1, 'Analytical Balance', 3, 3, 'Good', 'Available');

INSERT OR IGNORE INTO BOOKINGS (booking_id, user_id, laboratory_id, purpose, booking_date, start_time, end_time, status) VALUES
(1, 2, 1, 'Research', '2026-09-10', '10:00', '12:00', 'Approved');
