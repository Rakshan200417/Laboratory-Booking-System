from .db import DatabaseManager

class BookingManager:
    def __init__(self):
        self.db = DatabaseManager()

    def authenticate_user(self, e_id, password):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT u.user_id, u.e_id, u.name, u.email, u.phone, u.department, u.password, u.status, r.role_name,
                   s.index_number, s.program, s.year_of_study, s.batch,
                   l.employee_id, l.designation
            FROM USERS u
            JOIN ROLES r ON u.role_id = r.role_id
            LEFT JOIN STUDENTS s ON u.user_id = s.user_id
            LEFT JOIN LECTURERS l ON u.user_id = l.user_id
            WHERE u.e_id = ?
        """
        cursor.execute(query, (e_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            if row['status'] != 'Active':
                return None, "Account is inactive."
            if row['password'] == password:
                return dict(row), None
            else:
                return None, "Invalid password."
        return None, "User E-ID not found."

    def is_laboratory_available(self, laboratory_id, date, start_time, end_time):
        """
        Double-booking prevention rule:
        existing.start < new.end AND existing.end > new.start
        Excludes Rejected and Cancelled bookings.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT COUNT(*) FROM BOOKINGS
            WHERE laboratory_id = ?
            AND booking_date = ?
            AND status NOT IN ('Rejected', 'Cancelled')
            AND start_time < ?
            AND end_time > ?
        """
        cursor.execute(query, (laboratory_id, date, end_time, start_time))
        count = cursor.fetchone()[0]
        conn.close()
        return count == 0

    def create_booking(self, user_id, laboratory_id, purpose, date, start_time, end_time):
        if not self.is_laboratory_available(laboratory_id, date, start_time, end_time):
            return None # Reject due to double booking conflict

        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO BOOKINGS (user_id, laboratory_id, purpose, booking_date, start_time, end_time, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Pending')
        """
        cursor.execute(query, (user_id, laboratory_id, purpose, date, start_time, end_time))
        booking_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return booking_id

    def approve_booking(self, booking_id, approved_by_user_id, remarks=""):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE BOOKINGS SET status = 'Approved', updated_at = CURRENT_TIMESTAMP WHERE booking_id = ?", (booking_id,))
        cursor.execute(
            "INSERT INTO APPROVALS (booking_id, approved_by, decision, remarks) VALUES (?, ?, 'Approved', ?)",
            (booking_id, approved_by_user_id, remarks)
        )
        conn.commit()
        conn.close()
        return True

    def reject_booking(self, booking_id, approved_by_user_id, remarks=""):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE BOOKINGS SET status = 'Rejected', updated_at = CURRENT_TIMESTAMP WHERE booking_id = ?", (booking_id,))
        cursor.execute(
            "INSERT INTO APPROVALS (booking_id, approved_by, decision, remarks) VALUES (?, ?, 'Rejected', ?)",
            (booking_id, approved_by_user_id, remarks)
        )
        conn.commit()
        conn.close()
        return True

    def cancel_booking(self, booking_id, cancelled_by_user_id, reason=""):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE BOOKINGS SET status = 'Cancelled', updated_at = CURRENT_TIMESTAMP WHERE booking_id = ?", (booking_id,))
        cursor.execute(
            "INSERT INTO CANCELLATIONS (booking_id, cancelled_by, reason) VALUES (?, ?, ?)",
            (booking_id, cancelled_by_user_id, reason)
        )
        conn.commit()
        conn.close()
        return True

    def get_laboratories(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM LABORATORIES")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def get_user_bookings(self, user_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT b.booking_id, l.laboratory_name, b.booking_date, b.start_time, b.end_time, b.purpose, b.status
            FROM BOOKINGS b JOIN LABORATORIES l ON b.laboratory_id = l.laboratory_id
            WHERE b.user_id = ? ORDER BY b.booking_id DESC
        """
        cursor.execute(query, (user_id,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def get_pending_bookings(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT b.booking_id, u.name as user_name, u.department, l.laboratory_name, b.booking_date,
                   b.start_time, b.end_time, b.purpose
            FROM BOOKINGS b
            JOIN USERS u ON b.user_id = u.user_id
            JOIN LABORATORIES l ON b.laboratory_id = l.laboratory_id
            WHERE b.status = 'Pending' ORDER BY b.booking_id ASC
        """
        cursor.execute(query)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def get_lab_equipment(self, lab_id=None):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        if lab_id:
            query = """
                SELECT e.*, l.laboratory_name FROM LAB_EQUIPMENT e
                JOIN LABORATORIES l ON e.laboratory_id = l.laboratory_id
                WHERE e.laboratory_id = ? ORDER BY e.equipment_id ASC
            """
            cursor.execute(query, (lab_id,))
        else:
            query = """
                SELECT e.*, l.laboratory_name FROM LAB_EQUIPMENT e
                JOIN LABORATORIES l ON e.laboratory_id = l.laboratory_id
                ORDER BY e.equipment_id ASC
            """
            cursor.execute(query)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def add_equipment(self, lab_id, name, total_qty, avail_qty, condition):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO LAB_EQUIPMENT (laboratory_id, equipment_name, quantity_total, quantity_available, condition, status) VALUES (?, ?, ?, ?, ?, 'Available')",
            (lab_id, name, total_qty, avail_qty, condition)
        )
        conn.commit()
        conn.close()
        return True

    def get_dashboard_stats(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        stats = {}
        cursor.execute("SELECT COUNT(*) FROM LABORATORIES")
        stats['labs'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM BOOKINGS")
        stats['bookings'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM BOOKINGS WHERE status = 'Pending'")
        stats['pending'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM LAB_EQUIPMENT")
        stats['equipment'] = cursor.fetchone()[0]
        conn.close()
        return stats

    def get_recent_activity(self, limit=10):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        query = """
            SELECT b.booking_id, l.laboratory_name, u.name as user_name, b.booking_date,
                   b.start_time || ' - ' || b.end_time as slot, b.status
            FROM BOOKINGS b
            JOIN LABORATORIES l ON b.laboratory_id = l.laboratory_id
            JOIN USERS u ON b.user_id = u.user_id
            ORDER BY b.booking_id DESC LIMIT ?
        """
        cursor.execute(query, (limit,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def get_reports_data(self, status=None):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        if status and status != 'All':
            query = """
                SELECT b.booking_id, u.name as user_name, r.role_name, l.laboratory_name,
                       b.booking_date, b.start_time || ' - ' || b.end_time as slot, b.status
                FROM BOOKINGS b
                JOIN USERS u ON b.user_id = u.user_id
                JOIN ROLES r ON u.role_id = r.role_id
                JOIN LABORATORIES l ON b.laboratory_id = l.laboratory_id
                WHERE b.status = ? ORDER BY b.booking_id DESC
            """
            cursor.execute(query, (status,))
        else:
            query = """
                SELECT b.booking_id, u.name as user_name, r.role_name, l.laboratory_name,
                       b.booking_date, b.start_time || ' - ' || b.end_time as slot, b.status
                FROM BOOKINGS b
                JOIN USERS u ON b.user_id = u.user_id
                JOIN ROLES r ON u.role_id = r.role_id
                JOIN LABORATORIES l ON b.laboratory_id = l.laboratory_id
                ORDER BY b.booking_id DESC
            """
            cursor.execute(query)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows
