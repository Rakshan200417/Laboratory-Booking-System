import http.server
import socketserver
import json
import sqlite3
import os
import urllib.parse
from datetime import datetime
import base64

PORT = 5000
WEB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "frontend", "web"))
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "lab_booking.db"))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

class LabReserveHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def _send_json(self, data, status=200):
        response = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path.startswith("/api/"):
            self.handle_api_get(path, query)
        else:
            if path == "/" or not os.path.exists(os.path.join(WEB_DIR, path.lstrip("/"))):
                self.path = "/index.html"
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"
        try:
            body_data = json.loads(post_body.decode("utf-8")) if post_body else {}
        except Exception:
            body_data = {}

        if path.startswith("/api/"):
            self.handle_api_post(path, body_data)
        else:
            self.send_error(404, "Not Found")

    def handle_api_get(self, path, query):
        conn = get_db()
        cursor = conn.cursor()

        try:
            # 1. Health & Manual DB Verification
            if path == "/api/health":
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [r[0] for r in cursor.fetchall() if not r[0].startswith("sqlite_")]
                table_counts = {}
                for t in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {t}")
                    table_counts[t] = cursor.fetchone()[0]

                self._send_json({
                    "status": "connected",
                    "database_file": DB_PATH,
                    "database_size_bytes": os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0,
                    "tables": table_counts
                })

            # 2. Stats (Tailored to Role)
            elif path == "/api/stats":
                role = query.get("role", ["Administrator"])[0]
                user_id = query.get("user_id", ["1"])[0]

                cursor.execute("SELECT COUNT(*) FROM LABORATORIES")
                total_labs = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM LABORATORIES WHERE status = 'Available'")
                avail_labs = cursor.fetchone()[0]

                if role in ("Administrator", "Lab Technician"):
                    cursor.execute("SELECT COUNT(*) FROM BOOKINGS WHERE status = 'Pending'")
                    pending = cursor.fetchone()[0]

                    cursor.execute("SELECT COUNT(*) FROM BOOKINGS WHERE status IN ('Confirmed', 'Approved')")
                    confirmed = cursor.fetchone()[0]

                    cursor.execute("SELECT COUNT(*) FROM BOOKINGS")
                    total_bookings = cursor.fetchone()[0]

                    self._send_json({
                        "role": role,
                        "card1_label": "Total Laboratories",
                        "card1_value": total_labs,
                        "card1_sub": "University facilities",
                        "card2_label": "Available Now",
                        "card2_value": avail_labs,
                        "card2_sub": "Ready for reservation",
                        "card3_label": "Today's Bookings",
                        "card3_value": total_bookings,
                        "card3_sub": "Scheduled bookings",
                        "card4_label": "Pending Requests",
                        "card4_value": pending,
                        "card4_sub": "Awaiting admin approval"
                    })
                elif role in ("Faculty", "Lecturer"):
                    cursor.execute("SELECT COUNT(*) FROM BOOKINGS WHERE user_id = ?", (user_id,))
                    my_bookings = cursor.fetchone()[0]

                    cursor.execute("SELECT COUNT(*) FROM BOOKINGS WHERE user_id = ? AND status IN ('Confirmed', 'Approved')", (user_id,))
                    my_confirmed = cursor.fetchone()[0]

                    cursor.execute("SELECT COUNT(*) FROM BOOKINGS WHERE user_id = ? AND status = 'Pending'", (user_id,))
                    my_pending = cursor.fetchone()[0]

                    self._send_json({
                        "role": role,
                        "card1_label": "My Reservations",
                        "card1_value": my_bookings,
                        "card1_sub": "Total bookings submitted",
                        "card2_label": "Confirmed Sessions",
                        "card2_value": my_confirmed,
                        "card2_sub": "Ready for research/teaching",
                        "card3_label": "Available Labs",
                        "card3_value": avail_labs,
                        "card3_sub": "Open for reservation",
                        "card4_label": "Pending Approvals",
                        "card4_value": my_pending,
                        "card4_sub": "Under administrative review"
                    })
                else: # Student
                    cursor.execute("SELECT COUNT(*) FROM BOOKINGS WHERE user_id = ?", (user_id,))
                    my_requests = cursor.fetchone()[0]

                    cursor.execute("SELECT COUNT(*) FROM BOOKINGS WHERE user_id = ? AND status IN ('Confirmed', 'Approved')", (user_id,))
                    my_approved = cursor.fetchone()[0]

                    cursor.execute("SELECT COUNT(*) FROM BOOKINGS WHERE user_id = ? AND status = 'Pending'", (user_id,))
                    my_pending = cursor.fetchone()[0]

                    self._send_json({
                        "role": role,
                        "card1_label": "My Requests",
                        "card1_value": my_requests,
                        "card1_sub": "Total student submissions",
                        "card2_label": "Approved Sessions",
                        "card2_value": my_approved,
                        "card2_sub": "Ready for attendance",
                        "card3_label": "Available Labs",
                        "card3_value": avail_labs,
                        "card3_sub": "Open campus facilities",
                        "card4_label": "Awaiting Approval",
                        "card4_value": my_pending,
                        "card4_sub": "Pending staff decision"
                    })

            # 3. Laboratories (Read)
            elif path == "/api/laboratories":
                cursor.execute("""
                    SELECT l.laboratory_id, l.laboratory_name, l.laboratory_code, l.location,
                           l.capacity, l.description, l.status, l.image_url,
                           (SELECT COUNT(*) FROM LAB_EQUIPMENT e WHERE e.laboratory_id = l.laboratory_id) as equipment_count,
                           (SELECT b.purpose || ' (' || b.booking_date || ')' 
                            FROM BOOKINGS b 
                            WHERE b.laboratory_id = l.laboratory_id 
                            ORDER BY b.booking_id DESC LIMIT 1) as last_booking_info
                    FROM LABORATORIES l
                    ORDER BY l.laboratory_id ASC
                """)
                rows = cursor.fetchall()
                labs = []
                for r in rows:
                    item = dict(r)
                    if not item['last_booking_info']:
                        item['last_booking'] = "No recent reservations"
                    else:
                        item['last_booking'] = f"Recent: {item['last_booking_info']}"
                    labs.append(item)
                self._send_json(labs)

            # 4. Users (Read)
            elif path == "/api/users":
                cursor.execute("""
                    SELECT u.user_id, u.role_id, u.e_id, u.name, u.email, u.phone, u.department, u.status, r.role_name
                    FROM USERS u
                    JOIN ROLES r ON u.role_id = r.role_id
                    ORDER BY u.user_id ASC
                """)
                users = [dict(r) for r in cursor.fetchall()]
                self._send_json(users)

            # 5. Equipment (Read)
            elif path == "/api/equipment":
                cursor.execute("""
                    SELECT e.equipment_id, e.laboratory_id, e.equipment_name, e.quantity_total, e.quantity_available,
                           e.condition, e.status, e.category, e.last_calibration, l.laboratory_name
                    FROM LAB_EQUIPMENT e
                    JOIN LABORATORIES l ON e.laboratory_id = l.laboratory_id
                    ORDER BY e.equipment_id ASC
                """)
                rows = cursor.fetchall()
                equip = []
                for r in rows:
                    item = dict(r)
                    item['id_code'] = f"EQ-00{item['equipment_id']}"
                    if not item.get('category'):
                        item['category'] = 'Measurement'
                    if not item.get('last_calibration'):
                        item['last_calibration'] = '2024-10-15'
                    equip.append(item)
                self._send_json(equip)

            # 6. Bookings (Read, role filtered)
            elif path == "/api/bookings":
                tab = query.get("tab", ["all"])[0].lower()
                role = query.get("role", ["Administrator"])[0]
                user_id = query.get("user_id", [""])[0]

                sql = """
                    SELECT b.booking_id, b.user_id, b.laboratory_id, b.purpose, b.booking_date, b.start_time, b.end_time, b.status,
                           l.laboratory_name, u.name as requested_by, u.e_id
                    FROM BOOKINGS b
                    JOIN LABORATORIES l ON b.laboratory_id = l.laboratory_id
                    JOIN USERS u ON b.user_id = u.user_id
                    WHERE 1=1
                """
                params = []

                # Role separation: If Student or Faculty, only see their own bookings!
                if role in ("Student", "Graduate Student", "Faculty", "Lecturer") and user_id:
                    sql += " AND b.user_id = ?"
                    params.append(int(user_id))

                if tab == "pending":
                    sql += " AND b.status = 'Pending'"
                elif tab == "confirmed":
                    sql += " AND b.status IN ('Confirmed', 'Approved')"
                elif tab == "completed":
                    sql += " AND b.status = 'Completed'"
                elif tab == "cancelled":
                    sql += " AND b.status IN ('Cancelled', 'Rejected')"

                sql += " ORDER BY b.booking_id DESC"
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                bookings = []
                for r in rows:
                    item = dict(r)
                    item['code'] = f"#BK-2024-00{item['booking_id']}"
                    item['time_slot'] = f"{item['start_time']}–{item['end_time']}"
                    if item['status'] == 'Approved':
                        item['status'] = 'Confirmed'
                    bookings.append(item)
                self._send_json(bookings)

            # 7. Availability Timetable (Queried directly from SQLite BOOKINGS)
            elif path == "/api/availability":
                lab_name = query.get("lab", ["Chemistry Lab A"])[0]
                cursor.execute("SELECT laboratory_id FROM LABORATORIES WHERE laboratory_name = ?", (lab_name,))
                lab_row = cursor.fetchone()
                lab_id = lab_row[0] if lab_row else 1

                # Days mapping for Nov 18 – Nov 22, 2024
                days_map = [
                    {"key": "mon", "date": "2024-11-18", "label": "Mon 11/18"},
                    {"key": "tue", "date": "2024-11-19", "label": "Tue 11/19"},
                    {"key": "wed", "date": "2024-11-20", "label": "Wed 11/20"},
                    {"key": "thu", "date": "2024-11-21", "label": "Thu 11/21"},
                    {"key": "fri", "date": "2024-11-22", "label": "Fri 11/22"}
                ]

                time_slots = [
                    "08:00 – 10:00",
                    "10:00 – 12:00",
                    "12:00 – 14:00",
                    "14:00 – 16:00",
                    "16:00 – 17:00"
                ]

                # Query real bookings from SQLite for this laboratory
                cursor.execute("""
                    SELECT b.booking_id, b.booking_date, b.start_time, b.end_time, b.purpose, b.status, u.name as user_name
                    FROM BOOKINGS b
                    JOIN USERS u ON b.user_id = u.user_id
                    WHERE b.laboratory_id = ? AND b.status NOT IN ('Cancelled', 'Rejected')
                """, (lab_id,))
                booking_rows = cursor.fetchall()

                events = []
                for b in booking_rows:
                    b_date = b['booking_date']
                    day_item = next((d for d in days_map if d['date'] == b_date), None)
                    if day_item:
                        slot_str = f"{b['start_time']} – {b['end_time']}"
                        b_status = b['status']
                        evt_type = "confirmed"
                        if b_status == "Pending":
                            evt_type = "pending"
                        elif b_status == "Maintenance":
                            evt_type = "maintenance"

                        events.append({
                            "booking_id": b['booking_id'],
                            "day": day_item['key'],
                            "slot": slot_str,
                            "title": b['purpose'],
                            "subtitle": b['user_name'],
                            "status": b_status,
                            "type": evt_type
                        })

                self._send_json({
                    "laboratory_name": lab_name,
                    "week_label": "Nov 18 – Nov 22, 2024",
                    "days": days_map,
                    "time_slots": time_slots,
                    "events": events
                })

            else:
                self._send_json({"error": "Unknown API endpoint"}, 404)
        finally:
            conn.close()

    def handle_api_post(self, path, data):
        conn = get_db()
        cursor = conn.cursor()

        try:
            # AUTH: Login
            if path == "/api/auth/login":
                e_id = data.get("e_id", "").strip()
                password = data.get("password", "").strip()

                cursor.execute("""
                    SELECT u.user_id, u.e_id, u.name, u.email, u.status, u.department, r.role_name
                    FROM USERS u
                    JOIN ROLES r ON u.role_id = r.role_id
                    WHERE u.e_id = ? AND u.password = ?
                """, (e_id, password))
                user = cursor.fetchone()

                if user:
                    if user['status'] != 'Active':
                        self._send_json({"success": False, "message": "Account is marked as Inactive."}, 403)
                    else:
                        self._send_json({"success": True, "user": dict(user)})
                else:
                    self._send_json({"success": False, "message": "Invalid University ID or Password."}, 401)

            # BOOKING: Create (Double-Booking Prevention Guard)
            elif path == "/api/bookings/create":
                lab_id = data.get("laboratory_id", 1)
                user_id = data.get("user_id", 1)
                purpose = data.get("purpose", "Laboratory Research")
                date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
                start_time = data.get("start_time", "10:00")
                end_time = data.get("end_time", "12:00")

                # Double booking prevention check
                cursor.execute("""
                    SELECT COUNT(*) FROM BOOKINGS
                    WHERE laboratory_id = ? AND booking_date = ?
                    AND status NOT IN ('Rejected', 'Cancelled')
                    AND start_time < ? AND end_time > ?
                """, (lab_id, date, end_time, start_time))
                conflict = cursor.fetchone()[0]

                if conflict > 0:
                    self._send_json({
                        "success": False, 
                        "message": f"Double-Booking Conflict! Lab is already reserved on {date} between {start_time} and {end_time}."
                    }, 400)
                    return

                cursor.execute("""
                    INSERT INTO BOOKINGS (user_id, laboratory_id, purpose, booking_date, start_time, end_time, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'Pending')
                """, (user_id, lab_id, purpose, date, start_time, end_time))
                b_id = cursor.lastrowid
                conn.commit()
                self._send_json({"success": True, "booking_id": b_id, "message": "Booking submitted successfully!"})

            # BOOKING: Approve (Admin only)
            elif path.startswith("/api/bookings/") and path.endswith("/approve"):
                b_id = int(path.split("/")[3])
                cursor.execute("UPDATE BOOKINGS SET status = 'Confirmed', updated_at = CURRENT_TIMESTAMP WHERE booking_id = ?", (b_id,))
                cursor.execute("INSERT OR REPLACE INTO APPROVALS (booking_id, approved_by, decision, remarks) VALUES (?, 1, 'Approved', 'Approved by Admin')", (b_id,))
                conn.commit()
                self._send_json({"success": True, "status": "Confirmed", "message": f"Booking #BK-2024-00{b_id} Approved!"})

            # BOOKING: Reject (Admin only)
            elif path.startswith("/api/bookings/") and path.endswith("/reject"):
                b_id = int(path.split("/")[3])
                cursor.execute("UPDATE BOOKINGS SET status = 'Rejected', updated_at = CURRENT_TIMESTAMP WHERE booking_id = ?", (b_id,))
                cursor.execute("INSERT OR REPLACE INTO APPROVALS (booking_id, approved_by, decision, remarks) VALUES (?, 1, 'Rejected', 'Rejected by Admin')", (b_id,))
                conn.commit()
                self._send_json({"success": True, "status": "Rejected", "message": f"Booking #BK-2024-00{b_id} Rejected."})

            # BOOKING: Cancel (User can cancel own booking)
            elif path.startswith("/api/bookings/") and path.endswith("/cancel"):
                b_id = int(path.split("/")[3])
                cursor.execute("UPDATE BOOKINGS SET status = 'Cancelled', updated_at = CURRENT_TIMESTAMP WHERE booking_id = ?", (b_id,))
                conn.commit()
                self._send_json({"success": True, "status": "Cancelled", "message": f"Booking #BK-2024-00{b_id} has been cancelled."})

            # LABORATORIES: Create
            elif path == "/api/laboratories/create":
                name = data.get("name")
                code = data.get("code") or f"LAB-{name[:3].upper()}"
                loc = data.get("location", "Science Building")
                cap = int(data.get("capacity", 25))
                desc = data.get("description", "Laboratory facility")
                status = data.get("status", "Available")
                
                img_data = data.get("image_data")
                img_name = data.get("image_name")
                img = data.get("image_url", "")
                
                if img_data and img_name:
                    if "," in img_data:
                        img_data = img_data.split(",")[1]
                    try:
                        decoded = base64.b64decode(img_data)
                        safe_name = "".join([c for c in img_name if c.isalnum() or c=='.' or c=='_']).rstrip()
                        filepath = os.path.join(WEB_DIR, "assets", "images", safe_name)
                        with open(filepath, "wb") as f:
                            f.write(decoded)
                        img = f"assets/images/{safe_name}"
                    except Exception as e:
                        print("Error saving image:", e)

                cursor.execute("""
                    INSERT INTO LABORATORIES (laboratory_name, laboratory_code, location, capacity, description, status, image_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, code, loc, cap, desc, status, img))
                conn.commit()
                self._send_json({"success": True, "laboratory_id": cursor.lastrowid})

            # LABORATORIES: Update
            elif path == "/api/laboratories/update":
                lab_id = int(data.get("laboratory_id"))
                name = data.get("name")
                loc = data.get("location")
                cap = int(data.get("capacity", 25))
                status = data.get("status", "Available")
                
                img_data = data.get("image_data")
                img_name = data.get("image_name")
                
                # Fetch existing image to fallback on
                cursor.execute("SELECT image_url FROM LABORATORIES WHERE laboratory_id = ?", (lab_id,))
                row = cursor.fetchone()
                existing_img = row["image_url"] if row else ""
                
                img = data.get("image_url", existing_img)
                
                if img_data and img_name:
                    if "," in img_data:
                        img_data = img_data.split(",")[1]
                    try:
                        decoded = base64.b64decode(img_data)
                        safe_name = "".join([c for c in img_name if c.isalnum() or c=='.' or c=='_']).rstrip()
                        filepath = os.path.join(WEB_DIR, "assets", "images", safe_name)
                        with open(filepath, "wb") as f:
                            f.write(decoded)
                        img = f"assets/images/{safe_name}"
                    except Exception as e:
                        print("Error saving image:", e)

                cursor.execute("""
                    UPDATE LABORATORIES
                    SET laboratory_name = ?, location = ?, capacity = ?, status = ?, image_url = ?
                    WHERE laboratory_id = ?
                """, (name, loc, cap, status, img, lab_id))
                conn.commit()
                self._send_json({"success": True, "message": f"Laboratory {name} updated!"})

            # LABORATORIES: Delete
            elif path == "/api/laboratories/delete":
                lab_id = int(data.get("laboratory_id"))
                cursor.execute("DELETE FROM LABORATORIES WHERE laboratory_id = ?", (lab_id,))
                conn.commit()
                self._send_json({"success": True, "message": "Laboratory deleted from database."})

            # USERS: Create
            elif path == "/api/users/create":
                name = data.get("name")
                e_id = data.get("e_id")
                email = data.get("email")
                dept = data.get("department", "Chemistry")
                role_id = int(data.get("role_id", 4))
                password = data.get("password", "pass123")

                cursor.execute("""
                    INSERT INTO USERS (role_id, e_id, name, email, department, password, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'Active')
                """, (role_id, e_id, name, email, dept, password))
                conn.commit()
                self._send_json({"success": True, "user_id": cursor.lastrowid})

            # USERS: Update
            elif path == "/api/users/update":
                user_id = int(data.get("user_id"))
                name = data.get("name")
                email = data.get("email")
                dept = data.get("department")
                role_id = int(data.get("role_id"))
                status = data.get("status", "Active")

                cursor.execute("""
                    UPDATE USERS
                    SET name = ?, email = ?, department = ?, role_id = ?, status = ?
                    WHERE user_id = ?
                """, (name, email, dept, role_id, status, user_id))
                conn.commit()
                self._send_json({"success": True, "message": f"User {name} updated!"})

            # USERS: Delete
            elif path == "/api/users/delete":
                user_id = int(data.get("user_id"))
                if user_id == 1:
                    self._send_json({"success": False, "message": "Cannot delete root administrator!"}, 400)
                    return
                cursor.execute("DELETE FROM USERS WHERE user_id = ?", (user_id,))
                conn.commit()
                self._send_json({"success": True, "message": "User deleted from database."})

            # EQUIPMENT: Create
            elif path == "/api/equipment/create":
                name = data.get("name")
                lab_id = int(data.get("laboratory_id", 1))
                qty = int(data.get("quantity", 1))
                cat = data.get("category", "Measurement")
                status = data.get("status", "Available")
                cal = data.get("last_calibration", datetime.now().strftime("%Y-%m-%d"))

                cursor.execute("""
                    INSERT INTO LAB_EQUIPMENT (laboratory_id, equipment_name, quantity_total, quantity_available, condition, status, category, last_calibration)
                    VALUES (?, ?, ?, ?, 'Good', ?, ?, ?)
                """, (lab_id, name, qty, qty, status, cat, cal))
                conn.commit()
                self._send_json({"success": True, "equipment_id": cursor.lastrowid})

            # EQUIPMENT: Update
            elif path == "/api/equipment/update":
                eq_id = int(data.get("equipment_id"))
                name = data.get("name")
                cat = data.get("category")
                status = data.get("status")
                cal = data.get("last_calibration")

                cursor.execute("""
                    UPDATE LAB_EQUIPMENT
                    SET equipment_name = ?, category = ?, status = ?, last_calibration = ?
                    WHERE equipment_id = ?
                """, (name, cat, status, cal, eq_id))
                conn.commit()
                self._send_json({"success": True, "message": f"Equipment {name} updated!"})

            # EQUIPMENT: Delete
            elif path == "/api/equipment/delete":
                eq_id = int(data.get("equipment_id"))
                cursor.execute("DELETE FROM LAB_EQUIPMENT WHERE equipment_id = ?", (eq_id,))
                conn.commit()
                self._send_json({"success": True, "message": "Equipment deleted from database."})

            else:
                self._send_json({"error": "Unknown POST action"}, 404)
        finally:
            conn.close()

def run(port=PORT):
    os.makedirs(WEB_DIR, exist_ok=True)
    # Enable SO_REUSEADDR to avoid address already in use errors
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), LabReserveHandler) as httpd:
        print(f"================================================================")
        print(f" LabReserve Live Server at: http://localhost:{port}")
        print(f" SQLite Database connected: {DB_PATH}")
        print(f"================================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    run()
