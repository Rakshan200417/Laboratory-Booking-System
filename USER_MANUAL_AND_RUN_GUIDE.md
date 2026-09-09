# University Laboratory Booking & Management System
## Complete User Manual, Run Guide & Stakeholder Verification Document

---

## 1. System Overview & Architecture

The **University Laboratory Booking & Management System** is a desktop & web-capable application built with strict **Backend/Frontend folder separation**, **C++17 Qt 6 Widgets**, and a **Python/PySide6 Desktop Application Suite**.

### Folder Organization:
```
lab_booking_system/
├── backend/                  # Database schema, C++ OOP domain classes, Python backend engine
│   ├── db/schema.sql         # SQLite Schema & seed data
│   ├── include/ & src/       # C++ Header & Implementation files (User, Student, BookingManager, etc.)
│   └── app/                  # Python SQLite connection manager & BookingManager logic
├── frontend/                 # UI Layer (C++ Qt windows & PySide6 Desktop GUI)
│   ├── include/ & src/       # C++ Qt UI Window headers & implementations
│   └── desktop/main.py       # PySide6 Desktop GUI application entry point
├── LabBookingSystem.pro      # Qt Creator project file
└── README.md                 # System Overview & Instructions
```

---

## 2. How to Run the Application

You can launch and test the system using any of the following methods:

### Method A: PySide6 Desktop GUI Application (Recommended)
Run the following command in terminal or PowerShell:
```bash
python frontend/desktop/main.py
```
*Features native Windows Qt 6 GUI styling with modern dark theme and a **Stakeholder Role Dropdown**.*

### Method B: C++ Qt Creator Project
1. Launch **Qt Creator**.
2. Open `LabBookingSystem.pro`.
3. Click **Build & Run** (`Ctrl + R`).

### Method C: Web Application Server
1. Start the HTTP backend server:
   ```bash
   python backend/app/server.py
   ```
2. Open your web browser at: `http://localhost:5000`

---

## 3. Stakeholder Login Credentials & Roles Summary

Use the **Select Stakeholder Role** dropdown on the login screen to instantly select any role:

| Stakeholder Role | University E-ID | Password | Profile Displayed | Key Permissions |
|---|---|---|---|---|
| **Administrator** | `ADMIN001` | `admin123` | Dept: Nano Science \| System Admin | Manage Approvals Queue, Equipment Inventory, Reports |
| **Student** | `249109` | `pass123` | Index: 249109 \| BSc Nano Science \| Year 2 | View Labs, Check Slot Availability, Request Lab Session |
| **Lecturer** | `LEC001` | `pass123` | Emp ID: EMP001 \| Senior Lecturer \| Nano Science | Reserve Labs for Class Practicals & Research |

---

## 4. Stakeholder Testing & User Manual

### A. Testing as a Student (`249109` / `pass123`)

1. **Login**:
   - Open the app -> Select **`Student (Undergraduate / Postgraduate)`** from the dropdown -> Click **Login to Stakeholder Portal**.
2. **Verify Student Profile**:
   - Look at the top header bar. Verify it displays:
     `Welcome, Student A` `[ Student ]` `Index No: 249109 | BSc Nano Science | Year 2`.
3. **Test Double-Booking Slot Checker**:
   - Click **Laboratories Directory** tab.
   - Select `Nano Materials Lab`, Date `10/09/2026` (`dd/MM/yyyy`), From `10:00`, To `12:00`.
   - Click **Check Slot**.
   - **Expected Result**: Displays **`UNAVAILABLE: Conflict detected! Lab is ALREADY BOOKED for this slot.`** (Because an approved booking already exists for this slot).
   - Change time slot to From `14:00`, To `16:00` -> Click **Check Slot**.
   - **Expected Result**: Displays **`AVAILABLE: Lab is free for the selected date and time slot.`**
4. **Submit a Lab Booking Request**:
   - Click **Booking Portal** tab.
   - Form Title will show: **Submit Student Individual / Assignment Lab Session Request**.
   - Select Course: `NS2001 - Practical Nanotechnology`.
   - Select Lab: `Chemistry Lab`.
   - Select Date: `15/09/2026` (Notice the date format is strictly **`dd/MM/yyyy`**).
   - Select Time: `09:00` to `11:00`.
   - Enter Purpose: `Spectroscopy Project Assignment`.
   - Click **Submit Booking Request**.
   - **Expected Result**: Success alert box **`Booking #2 submitted successfully and is pending approval.`** appears, and the request appears in **My Booking Requests History** with status `Pending`.

---

### B. Testing as a Lecturer (`LEC001` / `pass123`)

1. **Login**:
   - Click **Logout** -> Select **`Lecturer (Academic Staff)`** from the dropdown -> Click **Login**.
2. **Verify Lecturer Profile**:
   - Header bar displays: `Welcome, Dr. Perera` `[ Lecturer / Academic Staff ]` `Employee ID: EMP001 | Senior Lecturer | Nano Science`.
3. **Reserve Class Practical Lab**:
   - Click **Booking Portal** tab.
   - Form Title will show: **Reserve Laboratory for Class Practical / Research**.
   - Select Course Code: `NS3010 - High Resolution Spectroscopy`.
   - Select Lab: `Nano Materials Lab`.
   - Select Date: `16/09/2026` (`dd/MM/yyyy`), Time: `10:00` to `12:00`.
   - Enter Purpose: `Class Practical Session for 25 Students`.
   - Click **Submit Booking Request**.
   - **Expected Result**: Booking request submitted with status `Pending`.
4. **Verify Nav Permissions**:
   - Notice that the **Manage Approvals** tab is hidden (preventing students/lecturers from approving their own bookings).

---

### C. Testing as an Administrator (`ADMIN001` / `admin123`)

1. **Login**:
   - Click **Logout** -> Select **`Administrator (Admin)`** from the dropdown -> Click **Login**.
2. **Verify Administrator Profile**:
   - Header bar displays: `Welcome, Admin` `[ Administrator ]` `Dept: Nano Science | System Admin Privileges`.
3. **Verify Dashboard Metrics**:
   - Dashboard card #3 displays **Pending Approvals Queue** badge (e.g. `2` pending requests).
4. **Approve / Reject Requests in Approvals Queue**:
   - Click **Manage Approvals** tab.
   - You will see the pending booking requests submitted by Student A and Dr. Perera.
   - Select a row in the table -> Type remarks: `Approved by Lab Admin for Nano Science Practical` -> Click **Approve Booking**.
   - **Expected Result**: Information popup **`Booking approved`** appears, and the booking disappears from the pending queue.
5. **Equipment Inventory Management**:
   - Click **Equipment Inventory** tab.
   - View inventory items (`Microscope`, `Centrifuge`, `Spectrophotometer`, `Analytical Balance`).
6. **System Analytics & Reports**:
   - Click **System Reports** tab.
   - Change Status Filter dropdown from `All` to `Approved` or `Pending`.
   - **Expected Result**: Table updates dynamically displaying filtered report logs.

---

## 5. Double-Booking Prevention Verification Rules

The core algorithm enforces that **no two bookings for the same laboratory overlap on the same date**.

$$\text{Conflict Condition: } (\text{Existing Start} < \text{New End}) \quad \text{AND} \quad (\text{Existing End} > \text{New Start})$$

### Test Matrix:
| Lab | Date (`dd/MM/yyyy`) | Slot Tested | Existing Booking | Expected Result |
|---|---|---|---|---|
| Nano Materials Lab | `10/09/2026` | `10:00 - 12:00` | `10:00 - 12:00` (Approved) | **UNAVAILABLE (Blocked)** |
| Nano Materials Lab | `10/09/2026` | `11:00 - 13:00` | `10:00 - 12:00` (Approved) | **UNAVAILABLE (Blocked)** |
| Nano Materials Lab | `10/09/2026` | `14:00 - 16:00` | None | **AVAILABLE (Allowed)** |
