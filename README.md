# University Laboratory Booking and Management System — Group 13

Desktop application built with **Qt 6 (Widgets) + C++17 + SQLite** and a **Python/PySide6 desktop suite**.

## Directory Structure (Backend & Frontend Separated)

```
lab_booking_system/
│
├── backend/
│   ├── db/
│   │   └── schema.sql                  # Database schema & seed data
│   ├── include/                        # C++ Header files (OOP Domain & Database Manager)
│   │   ├── User.h
│   │   ├── Student.h
│   │   ├── Lecturer.h
│   │   ├── Administrator.h
│   │   ├── Laboratory.h
│   │   ├── Equipment.h
│   │   ├── Booking.h
│   │   ├── DatabaseManager.h
│   │   └── BookingManager.h
│   ├── src/                            # C++ Source files (OOP Implementation)
│   │   ├── User.cpp
│   │   ├── Student.cpp
│   │   ├── Lecturer.cpp
│   │   ├── Administrator.cpp
│   │   ├── Laboratory.cpp
│   │   ├── Equipment.cpp
│   │   ├── Booking.cpp
│   │   ├── DatabaseManager.cpp
│   │   └── BookingManager.cpp
│   └── app/                            # Backend Python SQLite & Business Logic engine
│       ├── db.py                       # Database connection & schema loader
│       ├── models.py                   # Python OOP models
│       └── booking_manager.py          # Double-booking prevention & approval logic
│
├── frontend/
│   ├── include/                        # C++ Qt UI Window headers
│   │   ├── LoginWindow.h
│   │   ├── DashboardWindow.h
│   │   ├── LaboratoryListWindow.h
│   │   ├── BookingWindow.h
│   │   ├── ApprovalWindow.h
│   │   ├── EquipmentWindow.h
│   │   └── ReportsWindow.h
│   ├── src/                            # C++ Qt UI Window implementations
│   │   ├── main.cpp
│   │   ├── LoginWindow.cpp
│   │   ├── DashboardWindow.cpp
│   │   ├── LaboratoryListWindow.cpp
│   │   ├── BookingWindow.cpp
│   │   ├── ApprovalWindow.cpp
│   │   ├── EquipmentWindow.cpp
│   │   └── ReportsWindow.cpp
│   └── desktop/                        # PySide6 / Tkinter Desktop UI application
│       └── main.py                     # Desktop application entry point
│
├── LabBookingSystem.pro                # Qt Creator project file
└── README.md                           # Documentation
```

---

## Key System Features

1. **OOP Architecture**:
   - **Inheritance & Polymorphism**: `User` base class inherited by `Student`, `Lecturer`, `Administrator` with overridden `getRoleName()` and `describe()`.
   - **Encapsulation**: Private state fields accessed strictly via getters and setters.
   - **Abstraction**: `DatabaseManager` hides raw SQLite queries from the UI layer.
2. **Double-Booking Prevention**:
   - Implemented in `BookingManager::isLaboratoryAvailable()` and `BookingManager::createBooking()`.
   - Rejects overlapping time slot requests automatically (`start_time < new.end AND end_time > new.start`).
3. **Role-Based Authentication & Dashboard**:
   - Pre-loaded Accounts:
     - **Administrator**: E-ID `ADMIN001` / Password `admin123`
     - **Student**: E-ID `249109` / Password `pass123`
     - **Lecturer**: E-ID `LEC001` / Password `pass123`
   - Admin-only access to pending approval queues and equipment modification.
4. **Approval & Cancellation Workflow**:
   - Pending booking queue for administrators with mandatory/optional remarks.
5. **Equipment Inventory & Reports**:
   - Real-time stock tracking for lab equipment and status report logs.

---

## How to Build & Run

### Method 1: Qt Creator (C++)
1. Open `LabBookingSystem.pro` in **Qt Creator**.
2. Click **Build & Run** (`Ctrl + R`).
3. The project compiles C++ headers/sources from `backend/` and UI screens from `frontend/`.

### Method 2: Runnable Desktop Suite (Python / PySide6 / Tkinter)
To run and test the complete application UI directly on Windows:
```bash
python frontend/desktop/main.py
```

---

## Team & Responsibilities
| Member | Role | Owns |
|---|---|---|
| Team Lead / Integration | Project wiring, build setup, testing |
| Loganathan K. | UI/UX | Login, Dashboard, Laboratory, Booking UI screens |
| Thirushan Y. | Database | SQLite Schema (`backend/db/schema.sql`), queries |
| Sinooshan M. | OOP / Booking logic | Core domain classes, `BookingManager` double-booking engine |
