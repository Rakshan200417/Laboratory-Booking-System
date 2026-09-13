import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lab_booking.db"))

def seed():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")

    # 1. ROLES
    roles = [
        (1, 'Administrator', 'Laboratory staff who manage the system'),
        (2, 'Student', 'University student'),
        (3, 'Lecturer', 'University lecturer'),
        (4, 'Faculty', 'University faculty member'),
        (5, 'Lab Technician', 'Laboratory technician'),
        (6, 'Graduate Student', 'Graduate research student')
    ]
    for r in roles:
        cursor.execute("INSERT OR REPLACE INTO ROLES (role_id, role_name, description) VALUES (?, ?, ?)", r)

    # 2. Laboratories
    labs = [
        (1, 'Chemistry Lab A', 'LAB-CH-A', 'Science Building, Room 301', 30, 'Organic and inorganic chemistry lab', 'Available'),
        (2, 'Physics Lab B', 'LAB-PH-B', 'Science Building, Room 305', 25, 'Optics and laser calibration lab', 'In Use'),
        (3, 'Chemistry Lab B', 'LAB-CH-B', 'Science Building, Room 303', 30, 'Polymer and analytical chemistry lab', 'Maintenance'),
        (4, 'Electronics Lab', 'LAB-EE-1', 'Engineering Hall, Room 102', 20, 'Circuit design and testing lab', 'Available'),
        (5, 'Biology Lab C', 'LAB-BIO-C', 'Life Sciences, Room 204', 28, 'Cell culturing and microscopy lab', 'Available'),
        (6, 'Mechanical Lab', 'LAB-ME-1', 'Engineering Hall, Room 105', 24, 'CNC machining and prototyping lab', 'In Use'),
        (7, 'Physics Lab A', 'LAB-PH-A', 'Science Building, Room 201', 35, 'General physics seminar and demo lab', 'Available')
    ]
    for l in labs:
        cursor.execute("""
            INSERT OR REPLACE INTO LABORATORIES (laboratory_id, laboratory_name, laboratory_code, location, capacity, description, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, l)

    # 3. Users
    users = [
        (1, 1, 'ADMIN001', 'Admin User', 'admin@university.edu', '0770000000', 'Computer Science', 'admin123', 'Active'),
        (2, 4, 'U-882103', 'Dr. Sarah Chen', 's.chen@university.edu', '0771112233', 'Chemistry', 'pass123', 'Active'),
        (3, 4, 'U-554201', 'Prof. James Wilson', 'j.wilson@university.edu', '0772223344', 'Physics', 'pass123', 'Active'),
        (4, 4, 'U-332910', 'Dr. Maria Garcia', 'm.garcia@university.edu', '0773334455', 'Biology', 'pass123', 'Active'),
        (5, 5, 'U-112930', 'Dr. Robert Kim', 'r.kim@university.edu', '0774445566', 'Electronics', 'pass123', 'Active'),
        (6, 1, 'U-440210', 'Alan Turing', 'a.turing@university.edu', '0775556677', 'Computer Science', 'pass123', 'Active'),
        (7, 6, 'U-772049', 'Emily Watson', 'e.watson@student.edu', '0776667788', 'Chemistry', 'pass123', 'Active'),
        (8, 5, 'U-229410', 'Marcus Aurelius', 'm.aurelius@university.edu', '0777778899', 'Mechanical', 'pass123', 'Inactive'),
        (9, 6, 'U-992104', 'Clara Oswald', 'c.oswald@student.edu', '0778889900', 'Biology', 'pass123', 'Active'),
        (10, 2, '249109', 'Student A', 'studenta@uni.lk', '0771111111', 'Nano Science', 'pass123', 'Active'),
        (11, 3, 'LEC001', 'Dr. Perera', 'perera@uni.lk', '0772222222', 'Nano Science', 'pass123', 'Active')
    ]
    for u in users:
        cursor.execute("""
            INSERT OR REPLACE INTO USERS (user_id, role_id, e_id, name, email, phone, department, password, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, u)

    # 4. Equipment
    equipment = [
        (1, 1, 'Gas Chromatograph Mass Spectrometer', 1, 1, 'Good', 'Available', 'Spectrometry|2024-10-12'),
        (2, 4, 'Digital Phosphor Oscilloscope 100MHz', 4, 3, 'Calibrated', 'In Use', 'Measurement|2024-11-05'),
        (3, 5, 'Refrigerated High-Speed Centrifuge', 2, 0, 'Requires Maintenance', 'Maintenance', 'Separation|2024-09-18'),
        (4, 5, 'Fluorescence Phase Microscope', 3, 3, 'Good', 'Available', 'Imaging|2024-10-20'),
        (5, 3, 'Spectrophotometer UV-Vis', 2, 2, 'Good', 'Available', 'Spectrometry|2024-08-14'),
        (6, 2, 'Precision Temperature Test Chamber', 1, 1, 'Good', 'In Use', 'Environmental|2024-11-12')
    ]
    for eq in equipment:
        cursor.execute("""
            INSERT OR REPLACE INTO LAB_EQUIPMENT (equipment_id, laboratory_id, equipment_name, quantity_total, quantity_available, condition, status, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, eq)

    # 5. Bookings
    bookings = [
        (1, 2, 1, 'Organic Synthesis', '2024-10-24', '09:00', '11:00', 'Confirmed'),
        (2, 3, 2, 'Laser Calibration', '2024-10-24', '10:00', '12:00', 'Confirmed'),
        (3, 4, 5, 'Cell Culturing', '2024-10-24', '13:00', '15:00', 'Pending'),
        (4, 5, 4, 'Circuit Assembly', '2024-10-24', '14:00', '16:00', 'Confirmed'),
        (5, 7, 3, 'Polymer Testing', '2024-10-25', '15:00', '17:00', 'Pending'),
        (6, 5, 6, 'CNC Machining', '2024-10-25', '10:00', '12:00', 'Rejected'),
        (7, 3, 7, 'Optics Seminar', '2024-10-23', '14:00', '16:00', 'Completed')
    ]
    for b in bookings:
        cursor.execute("""
            INSERT OR REPLACE INTO BOOKINGS (booking_id, user_id, laboratory_id, purpose, booking_date, start_time, end_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, b)

    conn.commit()
    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.close()
    print("Database successfully synchronized with mockup data!")

if __name__ == "__main__":
    seed()
