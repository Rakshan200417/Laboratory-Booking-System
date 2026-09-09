import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QDateEdit, QTimeEdit, QTextEdit,
    QGroupBox, QMessageBox, QHeaderView, QFrame, QSplitter, QStackedWidget
)
from PySide6.QtCore import Qt, QDate, QTime
from PySide6.QtGui import QFont, QIcon, QColor

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.db import DatabaseManager
from backend.app.booking_manager import BookingManager

# Modern CSS Stylesheet for PySide6 Desktop GUI
PYSIDE_STYLE = """
QMainWindow {
    background-color: #0f172a;
}
QWidget {
    color: #f8fafc;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QGroupBox {
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 12px;
    font-weight: bold;
    color: #38bdf8;
    background-color: #1e293b;
    padding: 12px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
}
QLineEdit, QComboBox, QDateEdit, QTimeEdit, QTextEdit {
    background-color: #0f172a;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 6px 10px;
    color: #f8fafc;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, QTextEdit:focus {
    border: 1px solid #38bdf8;
}
QPushButton {
    background-color: #0284c7;
    color: #ffffff;
    font-weight: bold;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
}
QPushButton:hover {
    background-color: #0369a1;
}
QPushButton:disabled {
    background-color: #334155;
    color: #94a3b8;
}
QTableWidget {
    background-color: #0f172a;
    gridline-color: #334155;
    border: 1px solid #334155;
    border-radius: 6px;
}
QHeaderView::section {
    background-color: #1e293b;
    color: #38bdf8;
    font-weight: bold;
    padding: 6px;
    border: 1px solid #334155;
}
QTableWidgetItem {
    padding: 6px;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("University Laboratory Booking & Management System — Stakeholder Portal")
        self.resize(980, 700)
        self.setStyleSheet(PYSIDE_STYLE)

        # Initialize Backend Connection
        self.db_mgr = DatabaseManager()
        self.db_mgr.run_schema("backend/db/schema.sql")
        self.booking_mgr = BookingManager()

        self.current_user = None

        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        self.init_screens()
        self.show_login()

    def init_screens(self):
        # 1. Login Screen Widget
        self.login_widget = QWidget()
        self.setup_login_ui()
        self.stacked_widget.addWidget(self.login_widget)

        # 2. Main App Dashboard Container Widget
        self.app_widget = QWidget()
        self.setup_app_ui()
        self.stacked_widget.addWidget(self.app_widget)

    # ---------------- LOGIN SCREEN ----------------
    def setup_login_ui(self):
        layout = QVBoxLayout(self.login_widget)
        layout.setAlignment(Qt.AlignCenter)

        card = QGroupBox("University Laboratory Booking System", self.login_widget)
        card.setFixedSize(480, 470)

        card_layout = QVBoxLayout(card)

        sub = QLabel("Nano Science Department — Stakeholder Authentication", card)
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color: #94a3b8; font-style: italic;")

        # Stakeholder Dropdown ComboBox (Above University E-ID)
        role_label = QLabel("Select Stakeholder Role:", card)
        role_label.setStyleSheet("color: #38bdf8; font-weight: bold;")
        
        self.role_combo = QComboBox(card)
        self.role_combo.addItem("Administrator (Admin)", "ADMIN001")
        self.role_combo.addItem("Student (Undergraduate / Postgraduate)", "249109")
        self.role_combo.addItem("Lecturer (Academic Staff)", "LEC001")
        self.role_combo.currentIndexChanged.connect(self.handle_role_dropdown_change)

        self.eid_edit = QLineEdit(card)
        self.eid_edit.setPlaceholderText("University E-ID (e.g. ADMIN001, 249109, LEC001)")
        self.eid_edit.setText("ADMIN001")

        self.pwd_edit = QLineEdit(card)
        self.pwd_edit.setEchoMode(QLineEdit.Password)
        self.pwd_edit.setPlaceholderText("Password")
        self.pwd_edit.setText("admin123")

        login_btn = QPushButton("Login to Stakeholder Portal", card)
        login_btn.clicked.connect(self.handle_login)

        demo_label = QLabel("Quick Stakeholder Presets:", card)
        demo_label.setStyleSheet("color: #94a3b8; font-size: 11px; margin-top: 5px;")

        demo_layout = QHBoxLayout()
        btn_admin = QPushButton("Admin", card)
        btn_admin.setStyleSheet("background-color: #7c3aed; padding: 4px 8px; font-size: 11px;")
        btn_admin.clicked.connect(lambda: self.role_combo.setCurrentIndex(0))

        btn_student = QPushButton("Student", card)
        btn_student.setStyleSheet("background-color: #0284c7; padding: 4px 8px; font-size: 11px;")
        btn_student.clicked.connect(lambda: self.role_combo.setCurrentIndex(1))

        btn_lecturer = QPushButton("Lecturer", card)
        btn_lecturer.setStyleSheet("background-color: #059669; padding: 4px 8px; font-size: 11px;")
        btn_lecturer.clicked.connect(lambda: self.role_combo.setCurrentIndex(2))

        demo_layout.addWidget(btn_admin)
        demo_layout.addWidget(btn_student)
        demo_layout.addWidget(btn_lecturer)

        self.login_status = QLabel("", card)
        self.login_status.setStyleSheet("color: #f87171;")
        self.login_status.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(sub)
        card_layout.addSpacing(10)
        card_layout.addWidget(role_label)
        card_layout.addWidget(self.role_combo)
        card_layout.addSpacing(5)
        card_layout.addWidget(QLabel("University E-ID:"))
        card_layout.addWidget(self.eid_edit)
        card_layout.addWidget(QLabel("Password:"))
        card_layout.addWidget(self.pwd_edit)
        card_layout.addSpacing(10)
        card_layout.addWidget(login_btn)
        card_layout.addWidget(demo_label)
        card_layout.addLayout(demo_layout)
        card_layout.addWidget(self.login_status)

        layout.addWidget(card)

    def handle_role_dropdown_change(self, index):
        if index == 0:  # Administrator
            self.eid_edit.setText("ADMIN001")
            self.pwd_edit.setText("admin123")
        elif index == 1:  # Student
            self.eid_edit.setText("249109")
            self.pwd_edit.setText("pass123")
        elif index == 2:  # Lecturer
            self.eid_edit.setText("LEC001")
            self.pwd_edit.setText("pass123")

    def handle_login(self):
        eid = self.eid_edit.text().strip()
        pwd = self.pwd_edit.text().strip()

        user, err = self.booking_mgr.authenticate_user(eid, pwd)
        if user:
            self.current_user = user
            self.login_status.setText("")
            self.update_app_user_context()
            self.stacked_widget.setCurrentWidget(self.app_widget)
        else:
            self.login_status.setText(err or "Authentication failed.")

    def show_login(self):
        self.stacked_widget.setCurrentWidget(self.login_widget)

    # ---------------- MAIN DASHBOARD & NAV UI ----------------
    def setup_app_ui(self):
        main_layout = QVBoxLayout(self.app_widget)

        # Header Bar
        header = QHBoxLayout()
        self.user_info_lbl = QLabel("Welcome, User", self.app_widget)
        self.user_info_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #f8fafc;")

        self.role_badge = QLabel("[Role]", self.app_widget)
        self.role_badge.setStyleSheet("font-size: 13px; font-weight: bold; padding: 4px 10px; border-radius: 4px;")

        self.profile_details_lbl = QLabel("", self.app_widget)
        self.profile_details_lbl.setStyleSheet("color: #94a3b8; font-size: 12px; margin-left: 10px;")

        logout_btn = QPushButton("Logout", self.app_widget)
        logout_btn.setStyleSheet("background-color: #ef4444;")
        logout_btn.clicked.connect(self.show_login)

        header.addWidget(self.user_info_lbl)
        header.addWidget(self.role_badge)
        header.addWidget(self.profile_details_lbl)
        header.addStretch()
        header.addWidget(logout_btn)

        # Nav Buttons Bar
        nav_bar = QHBoxLayout()
        self.btn_dash = QPushButton("Dashboard", self.app_widget)
        self.btn_labs = QPushButton("Laboratories Directory", self.app_widget)
        self.btn_book = QPushButton("Booking Portal", self.app_widget)
        self.btn_approvals = QPushButton("Manage Approvals", self.app_widget)
        self.btn_equip = QPushButton("Equipment Inventory", self.app_widget)
        self.btn_reports = QPushButton("System Reports", self.app_widget)

        nav_bar.addWidget(self.btn_dash)
        nav_bar.addWidget(self.btn_labs)
        nav_bar.addWidget(self.btn_book)
        nav_bar.addWidget(self.btn_approvals)
        nav_bar.addWidget(self.btn_equip)
        nav_bar.addWidget(self.btn_reports)

        # Sub-views Stacked Widget
        self.sub_stacked = QStackedWidget(self.app_widget)

        # Build Sub views
        self.view_dash = QWidget()
        self.setup_dash_view()
        self.sub_stacked.addWidget(self.view_dash)

        self.view_labs = QWidget()
        self.setup_labs_view()
        self.sub_stacked.addWidget(self.view_labs)

        self.view_book = QWidget()
        self.setup_book_view()
        self.sub_stacked.addWidget(self.view_book)

        self.view_approvals = QWidget()
        self.setup_approvals_view()
        self.sub_stacked.addWidget(self.view_approvals)

        self.view_equip = QWidget()
        self.setup_equip_view()
        self.sub_stacked.addWidget(self.view_equip)

        self.view_reports = QWidget()
        self.setup_reports_view()
        self.sub_stacked.addWidget(self.view_reports)

        main_layout.addLayout(header)
        main_layout.addLayout(nav_bar)
        main_layout.addWidget(self.sub_stacked)

        # Connections
        self.btn_dash.clicked.connect(lambda: self.switch_view(0))
        self.btn_labs.clicked.connect(lambda: self.switch_view(1))
        self.btn_book.clicked.connect(lambda: self.switch_view(2))
        self.btn_approvals.clicked.connect(lambda: self.switch_view(3))
        self.btn_equip.clicked.connect(lambda: self.switch_view(4))
        self.btn_reports.clicked.connect(lambda: self.switch_view(5))

    def switch_view(self, index):
        self.sub_stacked.setCurrentIndex(index)
        if index == 0: self.refresh_dash()
        elif index == 1: self.refresh_labs()
        elif index == 2: self.refresh_book()
        elif index == 3: self.refresh_approvals()
        elif index == 4: self.refresh_equip()
        elif index == 5: self.refresh_reports()

    def update_app_user_context(self):
        if not self.current_user: return
        role = self.current_user['role_name']
        self.user_info_lbl.setText(f"Welcome, {self.current_user['name']}")

        # Role-Specific Styling & Attributes
        if role == 'Administrator':
            self.role_badge.setText("[ Administrator ]")
            self.role_badge.setStyleSheet("background-color: #7c3aed; color: white; font-weight: bold; padding: 4px 8px; border-radius: 4px;")
            self.profile_details_lbl.setText("Dept: Nano Science | System Admin Privileges")
            self.btn_approvals.setVisible(True)
            self.btn_book.setText("System Booking Portal")
        elif role == 'Lecturer':
            self.role_badge.setText("[ Lecturer / Academic Staff ]")
            self.role_badge.setStyleSheet("background-color: #059669; color: white; font-weight: bold; padding: 4px 8px; border-radius: 4px;")
            emp = self.current_user.get('employee_id') or 'EMP001'
            desig = self.current_user.get('designation') or 'Senior Lecturer'
            self.profile_details_lbl.setText(f"Employee ID: {emp} | {desig} | {self.current_user['department']}")
            self.btn_approvals.setVisible(False)
            self.btn_book.setText("Book Class Practical / Research Lab")
        elif role == 'Student':
            self.role_badge.setText("[ Student ]")
            self.role_badge.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold; padding: 4px 8px; border-radius: 4px;")
            idx_num = self.current_user.get('index_number') or '249109'
            prog = self.current_user.get('program') or 'BSc Nano Science'
            yr = self.current_user.get('year_of_study') or 2
            self.profile_details_lbl.setText(f"Index No: {idx_num} | {prog} | Year {yr}")
            self.btn_approvals.setVisible(False)
            self.btn_book.setText("Request Lab Session")

        self.switch_view(0)

    # --- DASHBOARD VIEW (TAILORED PER STAKEHOLDER) ---
    def setup_dash_view(self):
        l = QVBoxLayout(self.view_dash)

        self.card_box = QGroupBox("Key Stakeholder Metrics", self.view_dash)
        grid = QGridLayout(self.card_box)

        self.card_1 = self.create_card("Metric 1", "0")
        self.card_2 = self.create_card("Metric 2", "0")
        self.card_3 = self.create_card("Metric 3", "0")
        self.card_4 = self.create_card("Metric 4", "0")

        grid.addWidget(self.card_1[0], 0, 0)
        grid.addWidget(self.card_2[0], 0, 1)
        grid.addWidget(self.card_3[0], 0, 2)
        grid.addWidget(self.card_4[0], 0, 3)

        box = QGroupBox("Activity Overview & Bookings Log", self.view_dash)
        box_l = QVBoxLayout(box)
        self.dash_table = QTableWidget(box)
        self.dash_table.setColumnCount(6)
        self.dash_table.setHorizontalHeaderLabels(["ID", "Laboratory", "User", "Date", "Time Slot", "Status"])
        self.dash_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        box_l.addWidget(self.dash_table)

        l.addWidget(self.card_box)
        l.addWidget(box)

    def create_card(self, title, init_val):
        box = QGroupBox(title)
        box_l = QVBoxLayout(box)
        val_lbl = QLabel(init_val, box)
        val_lbl.setAlignment(Qt.AlignCenter)
        val_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #38bdf8;")
        box_l.addWidget(val_lbl)
        return box, val_lbl

    def refresh_dash(self):
        if not self.current_user: return
        role = self.current_user['role_name']
        stats = self.booking_mgr.get_dashboard_stats()

        if role == 'Administrator':
            self.card_box.setTitle("System Administration Health & Overview")
            self.card_1[0].setTitle("Active Laboratories")
            self.card_1[1].setText(str(stats['labs']))
            self.card_2[0].setTitle("Total System Bookings")
            self.card_2[1].setText(str(stats['bookings']))
            self.card_3[0].setTitle("Pending Approvals Queue")
            self.card_3[1].setText(str(stats['pending']))
            self.card_4[0].setTitle("Equipment Total")
            self.card_4[1].setText(str(stats['equipment']))
        elif role == 'Lecturer':
            self.card_box.setTitle("Lecturer Academic & Research Overview")
            my_bookings = self.booking_mgr.get_user_bookings(self.current_user['user_id'])
            appr_count = sum(1 for b in my_bookings if b['status'] == 'Approved')
            pend_count = sum(1 for b in my_bookings if b['status'] == 'Pending')

            self.card_1[0].setTitle("My Practicals & Research")
            self.card_1[1].setText(str(len(my_bookings)))
            self.card_2[0].setTitle("Approved Sessions")
            self.card_2[1].setText(str(appr_count))
            self.card_3[0].setTitle("Pending Approvals")
            self.card_3[1].setText(str(pend_count))
            self.card_4[0].setTitle("Available Laboratories")
            self.card_4[1].setText(str(stats['labs']))
        elif role == 'Student':
            self.card_box.setTitle("Student Academic Lab Portal")
            my_bookings = self.booking_mgr.get_user_bookings(self.current_user['user_id'])
            appr_count = sum(1 for b in my_bookings if b['status'] == 'Approved')
            pend_count = sum(1 for b in my_bookings if b['status'] == 'Pending')

            self.card_1[0].setTitle("My Lab Requests")
            self.card_1[1].setText(str(len(my_bookings)))
            self.card_2[0].setTitle("Confirmed Bookings")
            self.card_2[1].setText(str(appr_count))
            self.card_3[0].setTitle("Pending Approvals")
            self.card_3[1].setText(str(pend_count))
            self.card_4[0].setTitle("Available Laboratories")
            self.card_4[1].setText(str(stats['labs']))

        self.dash_table.setRowCount(0)
        for row, item in enumerate(self.booking_mgr.get_recent_activity(10)):
            self.dash_table.insertRow(row)
            self.dash_table.setItem(row, 0, QTableWidgetItem(str(item['booking_id'])))
            self.dash_table.setItem(row, 1, QTableWidgetItem(item['laboratory_name']))
            self.dash_table.setItem(row, 2, QTableWidgetItem(item['user_name']))
            self.dash_table.setItem(row, 3, QTableWidgetItem(item['booking_date']))
            self.dash_table.setItem(row, 4, QTableWidgetItem(item['slot']))
            self.dash_table.setItem(row, 5, QTableWidgetItem(item['status']))

    # --- LABS VIEW ---
    def setup_labs_view(self):
        l = QVBoxLayout(self.view_labs)

        self.labs_table = QTableWidget(self.view_labs)
        self.labs_table.setColumnCount(6)
        self.labs_table.setHorizontalHeaderLabels(["ID", "Laboratory Name", "Code", "Location", "Capacity", "Status"])
        self.labs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        chk_box = QGroupBox("Real-Time Double-Booking Slot Checker", self.view_labs)
        chk_l = QHBoxLayout(chk_box)

        self.chk_lab_cb = QComboBox()
        self.chk_date = QDateEdit(QDate.currentDate())
        self.chk_date.setDisplayFormat("dd/MM/yyyy")
        self.chk_date.setCalendarPopup(True)

        self.chk_start = QTimeEdit(QTime(9, 0))
        self.chk_end = QTimeEdit(QTime(11, 0))

        chk_btn = QPushButton("Check Slot")
        chk_btn.clicked.connect(self.do_check_slot)

        chk_l.addWidget(QLabel("Lab:"))
        chk_l.addWidget(self.chk_lab_cb)
        chk_l.addWidget(QLabel("Date:"))
        chk_l.addWidget(self.chk_date)
        chk_l.addWidget(QLabel("From:"))
        chk_l.addWidget(self.chk_start)
        chk_l.addWidget(QLabel("To:"))
        chk_l.addWidget(self.chk_end)
        chk_l.addWidget(chk_btn)

        self.chk_res_lbl = QLabel("", self.view_labs)
        self.chk_res_lbl.setAlignment(Qt.AlignCenter)
        self.chk_res_lbl.setStyleSheet("font-weight: bold; font-size: 14px;")

        l.addWidget(self.labs_table)
        l.addWidget(chk_box)
        l.addWidget(self.chk_res_lbl)

    def refresh_labs(self):
        self.labs_table.setRowCount(0)
        self.chk_lab_cb.clear()

        for row, item in enumerate(self.booking_mgr.get_laboratories()):
            self.labs_table.insertRow(row)
            self.labs_table.setItem(row, 0, QTableWidgetItem(str(item['laboratory_id'])))
            self.labs_table.setItem(row, 1, QTableWidgetItem(item['laboratory_name']))
            self.labs_table.setItem(row, 2, QTableWidgetItem(item['laboratory_code']))
            self.labs_table.setItem(row, 3, QTableWidgetItem(item['location']))
            self.labs_table.setItem(row, 4, QTableWidgetItem(str(item['capacity'])))
            self.labs_table.setItem(row, 5, QTableWidgetItem(item['status']))

            self.chk_lab_cb.addItem(item['laboratory_name'], item['laboratory_id'])

    def do_check_slot(self):
        lab_id = self.chk_lab_cb.currentData()
        d = self.chk_date.date().toString("yyyy-MM-dd")
        s = self.chk_start.time().toString("hh:mm")
        e = self.chk_end.time().toString("hh:mm")

        avail = self.booking_mgr.is_laboratory_available(lab_id, d, s, e)
        if avail:
            self.chk_res_lbl.setText("AVAILABLE: Lab is free for the selected date and time slot.")
            self.chk_res_lbl.setStyleSheet("color: #4ade80; font-size: 14px; font-weight: bold;")
        else:
            self.chk_res_lbl.setText("UNAVAILABLE: Conflict detected! Lab is ALREADY BOOKED for this slot.")
            self.chk_res_lbl.setStyleSheet("color: #f87171; font-size: 14px; font-weight: bold;")

    # --- BOOKING VIEW (TAILORED FOR STAKEHOLDER) ---
    def setup_book_view(self):
        l = QVBoxLayout(self.view_book)

        self.bk_form_box = QGroupBox("Submit New Laboratory Booking Request", self.view_book)
        grid = QGridLayout(self.bk_form_box)

        self.bk_module_cb = QComboBox()
        self.bk_module_cb.addItems([
            "NS2001 - Practical Nanotechnology",
            "NS2010 - Nano Materials Synthesis",
            "NS3010 - High Resolution Spectroscopy",
            "NS3020 - Electron Microscopy Practical",
            "General Research Experiment"
        ])

        self.bk_lab_cb = QComboBox()
        self.bk_date = QDateEdit(QDate.currentDate().addDays(1))
        self.bk_date.setDisplayFormat("dd/MM/yyyy")
        self.bk_date.setCalendarPopup(True)

        self.bk_start = QTimeEdit(QTime(10, 0))
        self.bk_end = QTimeEdit(QTime(12, 0))

        self.bk_purpose = QLineEdit()
        self.bk_purpose.setPlaceholderText("Describe research topic or practical activity details...")

        submit_btn = QPushButton("Submit Booking Request")
        submit_btn.clicked.connect(self.do_submit_booking)

        grid.addWidget(QLabel("Course / Activity:"), 0, 0)
        grid.addWidget(self.bk_module_cb, 0, 1)
        grid.addWidget(QLabel("Laboratory:"), 1, 0)
        grid.addWidget(self.bk_lab_cb, 1, 1)
        grid.addWidget(QLabel("Date:"), 2, 0)
        grid.addWidget(self.bk_date, 2, 1)
        grid.addWidget(QLabel("Start Time:"), 3, 0)
        grid.addWidget(self.bk_start, 3, 1)
        grid.addWidget(QLabel("End Time:"), 4, 0)
        grid.addWidget(self.bk_end, 4, 1)
        grid.addWidget(QLabel("Purpose / Remarks:"), 5, 0)
        grid.addWidget(self.bk_purpose, 5, 1)
        grid.addWidget(submit_btn, 6, 1)

        hist_box = QGroupBox("My Booking Requests History", self.view_book)
        hist_l = QVBoxLayout(hist_box)
        self.bk_hist_table = QTableWidget(hist_box)
        self.bk_hist_table.setColumnCount(6)
        self.bk_hist_table.setHorizontalHeaderLabels(["ID", "Laboratory", "Date", "Start", "End", "Status"])
        self.bk_hist_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        hist_l.addWidget(self.bk_hist_table)

        l.addWidget(self.bk_form_box)
        l.addWidget(hist_box)

    def refresh_book(self):
        if not self.current_user: return
        role = self.current_user['role_name']

        if role == 'Lecturer':
            self.bk_form_box.setTitle("Reserve Laboratory for Class Practical / Research")
        elif role == 'Student':
            self.bk_form_box.setTitle("Submit Student Individual / Assignment Lab Session Request")

        self.bk_lab_cb.clear()
        for item in self.booking_mgr.get_laboratories():
            if item['status'] == 'Available':
                self.bk_lab_cb.addItem(item['laboratory_name'], item['laboratory_id'])

        self.bk_hist_table.setRowCount(0)
        for row, item in enumerate(self.booking_mgr.get_user_bookings(self.current_user['user_id'])):
            self.bk_hist_table.insertRow(row)
            self.bk_hist_table.setItem(row, 0, QTableWidgetItem(str(item['booking_id'])))
            self.bk_hist_table.setItem(row, 1, QTableWidgetItem(item['laboratory_name']))
            self.bk_hist_table.setItem(row, 2, QTableWidgetItem(item['booking_date']))
            self.bk_hist_table.setItem(row, 3, QTableWidgetItem(item['start_time']))
            self.bk_hist_table.setItem(row, 4, QTableWidgetItem(item['end_time']))
            self.bk_hist_table.setItem(row, 5, QTableWidgetItem(item['status']))

    def do_submit_booking(self):
        lab_id = self.bk_lab_cb.currentData()
        d = self.bk_date.date().toString("yyyy-MM-dd")
        s = self.bk_start.time().toString("hh:mm")
        e = self.bk_end.time().toString("hh:mm")
        mod = self.bk_module_cb.currentText()
        p = self.bk_purpose.text().strip()

        full_purpose = f"[{mod}] {p}" if p else f"[{mod}]"

        bid = self.booking_mgr.create_booking(self.current_user['user_id'], lab_id, full_purpose, d, s, e)
        if bid:
            QMessageBox.information(self, "Booking Submitted", f"Booking #{bid} submitted successfully and is pending approval.")
            self.bk_purpose.clear()
            self.refresh_book()
        else:
            QMessageBox.critical(
                self, "Double Booking Prevented",
                "DOUBLE-BOOKING PREVENTED:\nThe selected laboratory is ALREADY booked for this date & time slot!\nPlease choose a different time slot."
            )

    # --- APPROVALS VIEW ---
    def setup_approvals_view(self):
        l = QVBoxLayout(self.view_approvals)

        box = QGroupBox("Pending Laboratory Booking Requests Queue", self.view_approvals)
        box_l = QVBoxLayout(box)

        self.appr_table = QTableWidget(box)
        self.appr_table.setColumnCount(7)
        self.appr_table.setHorizontalHeaderLabels(["ID", "Requester", "Dept", "Laboratory", "Date", "Slot", "Purpose"])
        self.appr_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        box_l.addWidget(self.appr_table)

        act_l = QHBoxLayout()
        self.appr_remarks = QLineEdit()
        self.appr_remarks.setPlaceholderText("Approval / Rejection remarks...")

        btn_appr = QPushButton("Approve Booking")
        btn_appr.setStyleSheet("background-color: #22c55e;")
        btn_appr.clicked.connect(self.do_approve)

        btn_rej = QPushButton("Reject Booking")
        btn_rej.setStyleSheet("background-color: #ef4444;")
        btn_rej.clicked.connect(self.do_reject)

        act_l.addWidget(self.appr_remarks)
        act_l.addWidget(btn_appr)
        act_l.addWidget(btn_rej)

        l.addWidget(box)
        l.addLayout(act_l)

    def refresh_approvals(self):
        self.appr_table.setRowCount(0)
        for row, item in enumerate(self.booking_mgr.get_pending_bookings()):
            self.appr_table.insertRow(row)
            self.appr_table.setItem(row, 0, QTableWidgetItem(str(item['booking_id'])))
            self.appr_table.setItem(row, 1, QTableWidgetItem(item['user_name']))
            self.appr_table.setItem(row, 2, QTableWidgetItem(item['department']))
            self.appr_table.setItem(row, 3, QTableWidgetItem(item['laboratory_name']))
            self.appr_table.setItem(row, 4, QTableWidgetItem(item['booking_date']))
            self.appr_table.setItem(row, 5, QTableWidgetItem(f"{item['start_time']} - {item['end_time']}"))
            self.appr_table.setItem(row, 6, QTableWidgetItem(item['purpose']))

    def do_approve(self):
        r = self.appr_table.currentRow()
        if r < 0:
            QMessageBox.warning(self, "Select Row", "Please select a booking from the table.")
            return
        bid = int(self.appr_table.item(r, 0).text())
        self.booking_mgr.approve_booking(bid, self.current_user['user_id'], self.appr_remarks.text())
        QMessageBox.information(self, "Approved", f"Booking #{bid} approved.")
        self.appr_remarks.clear()
        self.refresh_approvals()

    def do_reject(self):
        r = self.appr_table.currentRow()
        if r < 0:
            QMessageBox.warning(self, "Select Row", "Please select a booking from the table.")
            return
        bid = int(self.appr_table.item(r, 0).text())
        self.booking_mgr.reject_booking(bid, self.current_user['user_id'], self.appr_remarks.text())
        QMessageBox.information(self, "Rejected", f"Booking #{bid} rejected.")
        self.appr_remarks.clear()
        self.refresh_approvals()

    # --- EQUIPMENT VIEW ---
    def setup_equip_view(self):
        l = QVBoxLayout(self.view_equip)
        self.equip_table = QTableWidget(self.view_equip)
        self.equip_table.setColumnCount(7)
        self.equip_table.setHorizontalHeaderLabels(["ID", "Laboratory", "Equipment Name", "Total Qty", "Available Qty", "Condition", "Status"])
        self.equip_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        l.addWidget(self.equip_table)

    def refresh_equip(self):
        self.equip_table.setRowCount(0)
        for row, item in enumerate(self.booking_mgr.get_lab_equipment()):
            self.equip_table.insertRow(row)
            self.equip_table.setItem(row, 0, QTableWidgetItem(str(item['equipment_id'])))
            self.equip_table.setItem(row, 1, QTableWidgetItem(item['laboratory_name']))
            self.equip_table.setItem(row, 2, QTableWidgetItem(item['equipment_name']))
            self.equip_table.setItem(row, 3, QTableWidgetItem(str(item['quantity_total'])))
            self.equip_table.setItem(row, 4, QTableWidgetItem(str(item['quantity_available'])))
            self.equip_table.setItem(row, 5, QTableWidgetItem(item['condition']))
            self.equip_table.setItem(row, 6, QTableWidgetItem(item['status']))

    # --- REPORTS VIEW ---
    def setup_reports_view(self):
        l = QVBoxLayout(self.view_reports)

        filter_l = QHBoxLayout()
        self.rep_filter = QComboBox()
        self.rep_filter.addItems(["All", "Approved", "Pending", "Rejected"])
        self.rep_filter.currentIndexChanged.connect(self.refresh_reports)

        filter_l.addWidget(QLabel("Filter by Status:"))
        filter_l.addWidget(self.rep_filter)
        filter_l.addStretch()

        self.rep_table = QTableWidget(self.view_reports)
        self.rep_table.setColumnCount(7)
        self.rep_table.setHorizontalHeaderLabels(["ID", "Requester", "Role", "Laboratory", "Date", "Slot", "Status"])
        self.rep_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        l.addLayout(filter_l)
        l.addWidget(self.rep_table)

    def refresh_reports(self):
        st = self.rep_filter.currentText()
        self.rep_table.setRowCount(0)
        for row, item in enumerate(self.booking_mgr.get_reports_data(st)):
            self.rep_table.insertRow(row)
            self.rep_table.setItem(row, 0, QTableWidgetItem(str(item['booking_id'])))
            self.rep_table.setItem(row, 1, QTableWidgetItem(item['user_name']))
            self.rep_table.setItem(row, 2, QTableWidgetItem(item['role_name']))
            self.rep_table.setItem(row, 3, QTableWidgetItem(item['laboratory_name']))
            self.rep_table.setItem(row, 4, QTableWidgetItem(item['booking_date']))
            self.rep_table.setItem(row, 5, QTableWidgetItem(item['slot']))
            self.rep_table.setItem(row, 6, QTableWidgetItem(item['status']))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
