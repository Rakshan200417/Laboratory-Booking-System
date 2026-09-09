QT += core gui widgets sql
CONFIG += c++17

TARGET = LabBookingSystem
TEMPLATE = app

INCLUDEPATH += \
    backend/include \
    frontend/include

SOURCES += \
    frontend/src/main.cpp \
    frontend/src/LoginWindow.cpp \
    frontend/src/DashboardWindow.cpp \
    frontend/src/LaboratoryListWindow.cpp \
    frontend/src/BookingWindow.cpp \
    frontend/src/ApprovalWindow.cpp \
    frontend/src/EquipmentWindow.cpp \
    frontend/src/ReportsWindow.cpp \
    backend/src/DatabaseManager.cpp \
    backend/src/BookingManager.cpp \
    backend/src/User.cpp \
    backend/src/Student.cpp \
    backend/src/Lecturer.cpp \
    backend/src/Administrator.cpp \
    backend/src/Laboratory.cpp \
    backend/src/Equipment.cpp \
    backend/src/Booking.cpp

HEADERS += \
    frontend/include/LoginWindow.h \
    frontend/include/DashboardWindow.h \
    frontend/include/LaboratoryListWindow.h \
    frontend/include/BookingWindow.h \
    frontend/include/ApprovalWindow.h \
    frontend/include/EquipmentWindow.h \
    frontend/include/ReportsWindow.h \
    backend/include/DatabaseManager.h \
    backend/include/BookingManager.h \
    backend/include/User.h \
    backend/include/Student.h \
    backend/include/Lecturer.h \
    backend/include/Administrator.h \
    backend/include/Laboratory.h \
    backend/include/Equipment.h \
    backend/include/Booking.h
