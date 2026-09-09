#include "ApprovalWindow.h"
#include "BookingManager.h"
#include "DatabaseManager.h"
#include <QSqlQuery>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGroupBox>
#include <QHeaderView>
#include <QMessageBox>

ApprovalWindow::ApprovalWindow(int adminUserId, QWidget *parent)
    : QMainWindow(parent), adminUserId(adminUserId) {
    setupUi();
    loadPendingBookings();
}

void ApprovalWindow::setupUi() {
    setWindowTitle("Administrator - Booking Approvals Queue");
    resize(800, 500);

    QWidget *central = new QWidget(this);
    setCentralWidget(central);

    QVBoxLayout *mainLayout = new QVBoxLayout(central);
    mainLayout->setContentsMargins(15, 15, 15, 15);

    QGroupBox *box = new QGroupBox("Pending Laboratory Booking Requests", this);
    QVBoxLayout *boxLayout = new QVBoxLayout(box);

    pendingTable = new QTableWidget(this);
    pendingTable->setColumnCount(7);
    pendingTable->setHorizontalHeaderLabels({"Booking ID", "Requester", "Department", "Laboratory", "Date", "Time Slot", "Purpose"});
    pendingTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    pendingTable->setSelectionBehavior(QAbstractItemView::SelectRows);
    pendingTable->setEditTriggers(QAbstractItemView::NoEditTriggers);

    boxLayout->addWidget(pendingTable);

    QHBoxLayout *actionLayout = new QHBoxLayout();
    remarksEdit = new QLineEdit(this);
    remarksEdit->setPlaceholderText("Enter approval/rejection remarks or reasons...");

    approveBtn = new QPushButton("Approve Booking", this);
    approveBtn->setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 6px;");

    rejectBtn = new QPushButton("Reject Booking", this);
    rejectBtn->setStyleSheet("background-color: #F44336; color: white; font-weight: bold; padding: 6px;");

    refreshBtn = new QPushButton("Refresh Queue", this);

    actionLayout->addWidget(remarksEdit);
    actionLayout->addWidget(approveBtn);
    actionLayout->addWidget(rejectBtn);
    actionLayout->addWidget(refreshBtn);

    mainLayout->addWidget(box);
    mainLayout->addLayout(actionLayout);

    connect(approveBtn, &QPushButton::clicked, this, &ApprovalWindow::handleApprove);
    connect(rejectBtn, &QPushButton::clicked, this, &ApprovalWindow::handleReject);
    connect(refreshBtn, &QPushButton::clicked, this, &ApprovalWindow::loadPendingBookings);
}

void ApprovalWindow::loadPendingBookings() {
    pendingTable->setRowCount(0);
    QSqlQuery q(DatabaseManager::getInstance()->getDb());
    q.prepare(
        "SELECT b.booking_id, u.name, u.department, l.laboratory_name, b.booking_date, "
        "b.start_time || ' - ' || b.end_time, b.purpose "
        "FROM BOOKINGS b "
        "JOIN USERS u ON b.user_id = u.user_id "
        "JOIN LABORATORIES l ON b.laboratory_id = l.laboratory_id "
        "WHERE b.status = 'Pending' ORDER BY b.booking_id ASC"
    );

    if (q.exec()) {
        int row = 0;
        while (q.next()) {
            pendingTable->insertRow(row);
            for (int col = 0; col < 7; ++col) {
                pendingTable->setItem(row, col, new QTableWidgetItem(q.value(col).toString()));
            }
            row++;
        }
    }
}

void ApprovalWindow::handleApprove() {
    int row = pendingTable->currentRow();
    if (row < 0) {
        QMessageBox::warning(this, "Selection Required", "Please select a pending booking from the table.");
        return;
    }

    int bookingId = pendingTable->item(row, 0)->text().toInt();
    QString remarks = remarksEdit->text().trimmed();

    BookingManager bm;
    if (bm.approveBooking(bookingId, adminUserId, remarks)) {
        QMessageBox::information(this, "Booking Approved", QString("Booking #%1 has been approved.").arg(bookingId));
        remarksEdit->clear();
        loadPendingBookings();
    } else {
        QMessageBox::critical(this, "Error", "Failed to approve booking.");
    }
}

void ApprovalWindow::handleReject() {
    int row = pendingTable->currentRow();
    if (row < 0) {
        QMessageBox::warning(this, "Selection Required", "Please select a pending booking from the table.");
        return;
    }

    int bookingId = pendingTable->item(row, 0)->text().toInt();
    QString remarks = remarksEdit->text().trimmed();

    BookingManager bm;
    if (bm.rejectBooking(bookingId, adminUserId, remarks)) {
        QMessageBox::information(this, "Booking Rejected", QString("Booking #%1 has been rejected.").arg(bookingId));
        remarksEdit->clear();
        loadPendingBookings();
    } else {
        QMessageBox::critical(this, "Error", "Failed to reject booking.");
    }
}
