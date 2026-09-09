import sys
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add backend root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.db import DatabaseManager
from backend.app.booking_manager import BookingManager

# Initialize Database & Booking Manager
db_mgr = DatabaseManager()
db_mgr.run_schema("backend/db/schema.sql")
booking_mgr = BookingManager()

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>University Laboratory Booking System</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --accent-blue: #0284c7;
            --accent-green: #22c55e;
            --accent-red: #ef4444;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #334155;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-main); padding: 20px; line-height: 1.5; }
        .header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 15px; border-bottom: 1px solid var(--border-color); margin-bottom: 20px; }
        .header h1 { font-size: 1.5rem; color: #38bdf8; }
        .user-badge { font-weight: bold; background: #0369a1; padding: 4px 12px; border-radius: 20px; font-size: 0.9rem; margin-left: 10px; }
        .nav-tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .nav-btn { background: var(--card-bg); border: 1px solid var(--border-color); color: var(--text-main); padding: 10px 16px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: all 0.2s; }
        .nav-btn:hover, .nav-btn.active { background: var(--accent-blue); border-color: var(--accent-blue); }
        .container { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; min-height: 450px; }
        .card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .stat-card { background: #0f172a; border: 1px solid var(--border-color); padding: 15px; border-radius: 8px; text-align: center; }
        .stat-card h3 { font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 5px; }
        .stat-card .val { font-size: 1.8rem; font-weight: bold; color: #38bdf8; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid var(--border-color); font-size: 0.9rem; }
        th { background: #0f172a; color: #38bdf8; }
        tr:hover { background: rgba(56, 189, 248, 0.05); }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #38bdf8; font-size: 0.9rem; }
        input, select, textarea { width: 100%; padding: 10px; background: #0f172a; border: 1px solid var(--border-color); border-radius: 6px; color: white; }
        .btn { background: var(--accent-blue); color: white; border: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; cursor: pointer; }
        .btn:hover { opacity: 0.9; }
        .btn-success { background: var(--accent-green); }
        .btn-danger { background: var(--accent-red); }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
        .badge-Pending { background: #f59e0b; color: black; }
        .badge-Approved { background: #22c55e; color: black; }
        .badge-Rejected { background: #ef4444; color: white; }
        .auth-container { max-width: 400px; margin: 80px auto; background: var(--card-bg); padding: 30px; border-radius: 12px; border: 1px solid var(--border-color); }
        .alert { padding: 10px; border-radius: 6px; margin-top: 10px; font-weight: bold; text-align: center; }
        .alert-success { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }
        .alert-danger { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
    </style>
</head>
<body>
    <div id="loginView" class="auth-container">
        <h2 style="text-align: center; color: #38bdf8; margin-bottom: 5px;">University Lab System</h2>
        <p style="text-align: center; color: var(--text-muted); font-size: 0.85rem; margin-bottom: 20px;">Nano Science Dept — Group 13</p>
        <div class="form-group">
            <label>University E-ID</label>
            <input type="text" id="loginEid" value="ADMIN001">
        </div>
        <div class="form-group">
            <label>Password</label>
            <input type="password" id="loginPwd" value="admin123">
        </div>
        <button class="btn" style="width: 100%;" onclick="handleLogin()">Login to Dashboard</button>
        <div style="margin-top: 15px; font-size: 0.8rem; color: var(--text-muted);">
            <strong>Quick Demo Accounts:</strong><br>
            • Admin: <a href="#" onclick="setLogin('ADMIN001','admin123')" style="color:#38bdf8;">ADMIN001</a> |
            • Student: <a href="#" onclick="setLogin('249109','pass123')" style="color:#38bdf8;">249109</a> |
            • Lecturer: <a href="#" onclick="setLogin('LEC001','pass123')" style="color:#38bdf8;">LEC001</a>
        </div>
        <div id="loginMsg"></div>
    </div>

    <div id="appView" style="display: none;">
        <div class="header">
            <div>
                <h1 style="display: inline-block;">University Laboratory Booking Portal</h1>
                <span id="userRoleBadge" class="user-badge">Administrator</span>
            </div>
            <div>
                <span id="userNameLbl" style="font-weight: bold; margin-right: 15px;"></span>
                <button class="btn btn-danger" onclick="logout()">Logout</button>
            </div>
        </div>

        <div class="nav-tabs">
            <button class="nav-btn active" onclick="switchTab('dash')">Dashboard</button>
            <button class="nav-btn" onclick="switchTab('labs')">Laboratories</button>
            <button class="nav-btn" onclick="switchTab('booking')">Book Laboratory</button>
            <button id="approvalsTabBtn" class="nav-btn" onclick="switchTab('approvals')">Manage Approvals</button>
            <button class="nav-btn" onclick="switchTab('equipment')">Equipment</button>
            <button class="nav-btn" onclick="switchTab('reports')">System Reports</button>
        </div>

        <div class="container">
            <div id="tabDash">
                <div class="card-grid">
                    <div class="stat-card"><h3>Laboratories</h3><div id="statLabs" class="val">0</div></div>
                    <div class="stat-card"><h3>Total Bookings</h3><div id="statBookings" class="val">0</div></div>
                    <div class="stat-card"><h3>Pending Approvals</h3><div id="statPending" class="val">0</div></div>
                    <div class="stat-card"><h3>Lab Equipment</h3><div id="statEquip" class="val">0</div></div>
                </div>
                <h3 style="color: #38bdf8; margin-bottom: 10px;">Recent Activity & Bookings</h3>
                <table>
                    <thead><tr><th>ID</th><th>Laboratory</th><th>Requester</th><th>Date</th><th>Slot</th><th>Status</th></tr></thead>
                    <tbody id="dashTableBody"></tbody>
                </table>
            </div>

            <div id="tabLabs" style="display: none;">
                <h3 style="color: #38bdf8; margin-bottom: 10px;">Laboratories Directory</h3>
                <table>
                    <thead><tr><th>ID</th><th>Name</th><th>Code</th><th>Location</th><th>Capacity</th><th>Status</th></tr></thead>
                    <tbody id="labsTableBody"></tbody>
                </table>
                <div style="margin-top: 25px; background: #0f172a; padding: 15px; border-radius: 8px;">
                    <h4 style="color: #38bdf8; margin-bottom: 10px;">Real-Time Slot Availability Checker</h4>
                    <div style="display: flex; gap: 10px; align-items: flex-end;">
                        <div style="flex: 1;"><label>Lab</label><select id="chkLabSelect"></select></div>
                        <div style="flex: 1;"><label>Date</label><input type="date" id="chkDate" value="2026-09-10"></div>
                        <div style="flex: 1;"><label>Start</label><input type="time" id="chkStart" value="10:00"></div>
                        <div style="flex: 1;"><label>End</label><input type="time" id="chkEnd" value="12:00"></div>
                        <button class="btn" onclick="checkSlotAvailability()">Check Slot</button>
                    </div>
                    <div id="chkResultMsg"></div>
                </div>
            </div>

            <div id="tabBooking" style="display: none;">
                <h3 style="color: #38bdf8; margin-bottom: 10px;">Create Laboratory Booking</h3>
                <div style="display: flex; gap: 20px;">
                    <div style="flex: 1; background: #0f172a; padding: 15px; border-radius: 8px;">
                        <div class="form-group"><label>Laboratory</label><select id="bkLabSelect"></select></div>
                        <div class="form-group"><label>Booking Date</label><input type="date" id="bkDate" value="2026-09-11"></div>
                        <div class="form-group"><label>Start Time</label><input type="time" id="bkStart" value="09:00"></div>
                        <div class="form-group"><label>End Time</label><input type="time" id="bkEnd" value="11:00"></div>
                        <div class="form-group"><label>Purpose</label><input type="text" id="bkPurpose" value="Nano Research Project"></div>
                        <button class="btn" style="width: 100%;" onclick="submitBooking()">Submit Request</button>
                        <div id="bkMsg"></div>
                    </div>
                    <div style="flex: 2;">
                        <h4 style="color: #38bdf8; margin-bottom: 10px;">Your Booking History</h4>
                        <table>
                            <thead><tr><th>ID</th><th>Laboratory</th><th>Date</th><th>Start</th><th>End</th><th>Status</th></tr></thead>
                            <tbody id="myBookingsBody"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div id="tabApprovals" style="display: none;">
                <h3 style="color: #38bdf8; margin-bottom: 10px;">Administrator Approvals Queue</h3>
                <table>
                    <thead><tr><th>ID</th><th>Requester</th><th>Dept</th><th>Laboratory</th><th>Date</th><th>Slot</th><th>Purpose</th><th>Action</th></tr></thead>
                    <tbody id="approvalsTableBody"></tbody>
                </table>
            </div>

            <div id="tabEquipment" style="display: none;">
                <h3 style="color: #38bdf8; margin-bottom: 10px;">Laboratory Equipment Inventory</h3>
                <table>
                    <thead><tr><th>ID</th><th>Laboratory</th><th>Equipment Name</th><th>Total Qty</th><th>Avail Qty</th><th>Condition</th><th>Status</th></tr></thead>
                    <tbody id="equipTableBody"></tbody>
                </table>
            </div>

            <div id="tabReports" style="display: none;">
                <h3 style="color: #38bdf8; margin-bottom: 10px;">System Reports & Analytics</h3>
                <div style="margin-bottom: 10px; display: flex; align-items: center; gap: 10px;">
                    <label style="margin: 0;">Status Filter:</label>
                    <select id="repFilter" style="width: 200px;" onchange="loadReports()">
                        <option value="All">All Statuses</option>
                        <option value="Approved">Approved</option>
                        <option value="Pending">Pending</option>
                        <option value="Rejected">Rejected</option>
                    </select>
                </div>
                <table>
                    <thead><tr><th>ID</th><th>Requester</th><th>Role</th><th>Laboratory</th><th>Date</th><th>Slot</th><th>Status</th></tr></thead>
                    <tbody id="reportsTableBody"></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let currentUser = null;

        function setLogin(e, p) {
            document.getElementById('loginEid').value = e;
            document.getElementById('loginPwd').value = p;
            handleLogin();
        }

        async function handleLogin() {
            const eid = document.getElementById('loginEid').value;
            const pwd = document.getElementById('loginPwd').value;
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({e_id: eid, password: pwd})
            });
            const data = await res.json();
            if (data.success) {
                currentUser = data.user;
                document.getElementById('loginView').style.display = 'none';
                document.getElementById('appView').style.display = 'block';
                document.getElementById('userNameLbl').innerText = currentUser.name;
                document.getElementById('userRoleBadge').innerText = currentUser.role_name;

                if (currentUser.role_name !== 'Administrator') {
                    document.getElementById('approvalsTabBtn').style.display = 'none';
                } else {
                    document.getElementById('approvalsTabBtn').style.display = 'inline-block';
                }

                switchTab('dash');
            } else {
                document.getElementById('loginMsg').innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            }
        }

        function logout() {
            currentUser = null;
            document.getElementById('loginView').style.display = 'block';
            document.getElementById('appView').style.display = 'none';
        }

        function switchTab(tab) {
            ['dash', 'labs', 'booking', 'approvals', 'equipment', 'reports'].forEach(t => {
                document.getElementById('tab' + t.charAt(0).toUpperCase() + t.slice(1)).style.display = (t === tab) ? 'block' : 'none';
            });
            if (tab === 'dash') loadDash();
            else if (tab === 'labs') loadLabs();
            else if (tab === 'booking') loadBooking();
            else if (tab === 'approvals') loadApprovals();
            else if (tab === 'equipment') loadEquipment();
            else if (tab === 'reports') loadReports();
        }

        async function loadDash() {
            const res = await fetch('/api/dashboard');
            const data = await res.json();
            document.getElementById('statLabs').innerText = data.stats.labs;
            document.getElementById('statBookings').innerText = data.stats.bookings;
            document.getElementById('statPending').innerText = data.stats.pending;
            document.getElementById('statEquip').innerText = data.stats.equipment;

            let html = '';
            data.recent.forEach(r => {
                html += `<tr><td>${r.booking_id}</td><td>${r.laboratory_name}</td><td>${r.user_name}</td><td>${r.booking_date}</td><td>${r.slot}</td><td><span class="badge badge-${r.status}">${r.status}</span></td></tr>`;
            });
            document.getElementById('dashTableBody').innerHTML = html;
        }

        async function loadLabs() {
            const res = await fetch('/api/laboratories');
            const labs = await res.json();
            let html = '', opts = '';
            labs.forEach(l => {
                html += `<tr><td>${l.laboratory_id}</td><td>${l.laboratory_name}</td><td>${l.laboratory_code}</td><td>${l.location}</td><td>${l.capacity}</td><td>${l.status}</td></tr>`;
                opts += `<option value="${l.laboratory_id}">${l.laboratory_name}</option>`;
            });
            document.getElementById('labsTableBody').innerHTML = html;
            document.getElementById('chkLabSelect').innerHTML = opts;
            document.getElementById('bkLabSelect').innerHTML = opts;
        }

        async function checkSlotAvailability() {
            const lid = document.getElementById('chkLabSelect').value;
            const d = document.getElementById('chkDate').value;
            const s = document.getElementById('chkStart').value;
            const e = document.getElementById('chkEnd').value;
            const res = await fetch('/api/check-availability', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({laboratory_id: lid, date: d, start_time: s, end_time: e})
            });
            const data = await res.json();
            const msg = document.getElementById('chkResultMsg');
            if (data.available) {
                msg.innerHTML = `<div class="alert alert-success">AVAILABLE: Laboratory is free for this slot.</div>`;
            } else {
                msg.innerHTML = `<div class="alert alert-danger">UNAVAILABLE (CONFLICT): Laboratory is ALREADY BOOKED!</div>`;
            }
        }

        async function loadBooking() {
            loadLabs();
            const res = await fetch('/api/user-bookings?user_id=' + currentUser.user_id);
            const bookings = await res.json();
            let html = '';
            bookings.forEach(b => {
                html += `<tr><td>${b.booking_id}</td><td>${b.laboratory_name}</td><td>${b.booking_date}</td><td>${b.start_time}</td><td>${b.end_time}</td><td><span class="badge badge-${b.status}">${b.status}</span></td></tr>`;
            });
            document.getElementById('myBookingsBody').innerHTML = html;
        }

        async function submitBooking() {
            const lid = document.getElementById('bkLabSelect').value;
            const d = document.getElementById('bkDate').value;
            const s = document.getElementById('bkStart').value;
            const e = document.getElementById('bkEnd').value;
            const p = document.getElementById('bkPurpose').value;

            const res = await fetch('/api/create-booking', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user_id: currentUser.user_id, laboratory_id: lid, purpose: p, date: d, start_time: s, end_time: e})
            });
            const data = await res.json();
            const msg = document.getElementById('bkMsg');
            if (data.success) {
                msg.innerHTML = `<div class="alert alert-success">Booking #${data.booking_id} submitted successfully!</div>`;
                loadBooking();
            } else {
                msg.innerHTML = `<div class="alert alert-danger">DOUBLE-BOOKING PREVENTED: Slot is already occupied!</div>`;
            }
        }

        async function loadApprovals() {
            const res = await fetch('/api/pending-approvals');
            const pending = await res.json();
            let html = '';
            pending.forEach(p => {
                html += `<tr><td>${p.booking_id}</td><td>${p.user_name}</td><td>${p.department}</td><td>${p.laboratory_name}</td><td>${p.booking_date}</td><td>${p.start_time} - ${p.end_time}</td><td>${p.purpose}</td>
                <td><button class="btn btn-success" style="padding: 4px 8px;" onclick="approveBooking(${p.booking_id})">Approve</button> <button class="btn btn-danger" style="padding: 4px 8px;" onclick="rejectBooking(${p.booking_id})">Reject</button></td></tr>`;
            });
            document.getElementById('approvalsTableBody').innerHTML = html;
        }

        async function approveBooking(bid) {
            await fetch('/api/approve-booking', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({booking_id: bid, approved_by: currentUser.user_id, remarks: 'Approved via Web'})
            });
            loadApprovals();
        }

        async function rejectBooking(bid) {
            await fetch('/api/reject-booking', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({booking_id: bid, approved_by: currentUser.user_id, remarks: 'Rejected via Web'})
            });
            loadApprovals();
        }

        async function loadEquipment() {
            const res = await fetch('/api/equipment');
            const equip = await res.json();
            let html = '';
            equip.forEach(e => {
                html += `<tr><td>${e.equipment_id}</td><td>${e.laboratory_name}</td><td>${e.equipment_name}</td><td>${e.quantity_total}</td><td>${e.quantity_available}</td><td>${e.condition}</td><td>${e.status}</td></tr>`;
            });
            document.getElementById('equipTableBody').innerHTML = html;
        }

        async function loadReports() {
            const st = document.getElementById('repFilter').value;
            const res = await fetch('/api/reports?status=' + st);
            const data = await res.json();
            let html = '';
            data.forEach(r => {
                html += `<tr><td>${r.booking_id}</td><td>${r.user_name}</td><td>${r.role_name}</td><td>${r.laboratory_name}</td><td>${r.booking_date}</td><td>${r.slot}</td><td><span class="badge badge-${r.status}">${r.status}</span></td></tr>`;
            });
            document.getElementById('reportsTableBody').innerHTML = html;
        }
    </script>
</body>
</html>
"""

class RequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _send_html(self, html):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == '/' or path == '/index.html':
            self._send_html(HTML_CONTENT)
        elif path == '/api/dashboard':
            stats = booking_mgr.get_dashboard_stats()
            recent = booking_mgr.get_recent_activity(10)
            self._send_json({'stats': stats, 'recent': recent})
        elif path == '/api/laboratories':
            labs = booking_mgr.get_laboratories()
            self._send_json(labs)
        elif path == '/api/user-bookings':
            uid = int(qs.get('user_id', [0])[0])
            bookings = booking_mgr.get_user_bookings(uid)
            self._send_json(bookings)
        elif path == '/api/pending-approvals':
            pending = booking_mgr.get_pending_bookings()
            self._send_json(pending)
        elif path == '/api/equipment':
            equip = booking_mgr.get_lab_equipment()
            self._send_json(equip)
        elif path == '/api/reports':
            st = qs.get('status', ['All'])[0]
            reports = booking_mgr.get_reports_data(st)
            self._send_json(reports)
        else:
            self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body_bytes = self.rfile.read(content_length) if content_length > 0 else b'{}'
        data = json.loads(body_bytes.decode('utf-8')) if body_bytes else {}

        if self.path == '/api/login':
            user, err = booking_mgr.authenticate_user(data.get('e_id'), data.get('password'))
            if user:
                self._send_json({'success': True, 'user': user})
            else:
                self._send_json({'success': False, 'error': err}, status=401)
        elif self.path == '/api/check-availability':
            lid = int(data.get('laboratory_id', 0))
            d = data.get('date')
            s = data.get('start_time')
            e = data.get('end_time')
            avail = booking_mgr.is_laboratory_available(lid, d, s, e)
            self._send_json({'available': avail})
        elif self.path == '/api/create-booking':
            uid = int(data.get('user_id'))
            lid = int(data.get('laboratory_id'))
            p = data.get('purpose')
            d = data.get('date')
            s = data.get('start_time')
            e = data.get('end_time')
            bid = booking_mgr.create_booking(uid, lid, p, d, s, e)
            if bid:
                self._send_json({'success': True, 'booking_id': bid})
            else:
                self._send_json({'success': False, 'error': 'Double booking conflict'}, status=409)
        elif self.path == '/api/approve-booking':
            bid = int(data.get('booking_id'))
            uid = int(data.get('approved_by'))
            rem = data.get('remarks', '')
            ok = booking_mgr.approve_booking(bid, uid, rem)
            self._send_json({'success': ok})
        elif self.path == '/api/reject-booking':
            bid = int(data.get('booking_id'))
            uid = int(data.get('approved_by'))
            rem = data.get('remarks', '')
            ok = booking_mgr.reject_booking(bid, uid, rem)
            self._send_json({'success': ok})

if __name__ == '__main__':
    port = 5000
    server = HTTPServer(('localhost', port), RequestHandler)
    print(f"Backend Server running at http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server.")
        server.server_close()
