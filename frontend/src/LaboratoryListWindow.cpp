#include "LaboratoryListWindow.h"
#include "BookingWindow.h"
#include "BookingManager.h"
#include "DatabaseManager.h"
#include <QSqlQuery>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGroupBox>
#include <QHeaderView>
#include <QMessageBox>
#include <QDate>

LaboratoryListWindow::LaboratoryListWindow(int userId, const QString &role, QWidget *parent)
    : QMainWindow(parent), currentUserId(userId), currentUserRole(role) {
    setupUi();
    loadLaboratories();
}

void LaboratoryListWindow::setupUi() {
    setWindowTitle("Laboratories Directory & Slot Availability");
    resize(750, 500);

    QWidget *central = new QWidget(this);
    setCentralWidget(central);

    QVBoxLayout *mainLayout = new QVBoxLayout(central);
    mainLayout->setContentsMargins(15, 15, 15, 15);

    // Labs Table
    labsTable = new QTableWidget(this);
    labsTable->setColumnCount(6);
    labsTable->setHorizontalHeaderLabels({"ID", "Laboratory Name", "Code", "Location", "Capacity", "Status"});
    labsTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    labsTable->setSelectionBehavior(QAbstractItemView::SelectRows);
    labsTable->setEditTriggers(QAbstractItemView::NoEditTriggers);

    // Availability Checker Box
    QGroupBox *checkGroup = new QGroupBox("Real-Time Double-Booking Checker Tool", this);
    QHBoxLayout *checkLayout = new QHBoxLayout(checkGroup);

    labComboBox = new QComboBox(this);
    dateEdit = new QDateEdit(QDate::currentDate(), this);
    dateEdit->setDisplayFormat("dd/MM/yyyy");
    dateEdit->setCalendarPopup(true);

    startTimeEdit = new QTimeEdit(QTime(9, 0), this);
    endTimeEdit = new QTimeEdit(QTime(11, 0), this);

    checkAvailabilityBtn = new QPushButton("Check Slot", this);
    bookLabBtn = new QPushButton("Book Selected Slot", this);

    checkLayout->addWidget(new QLabel("Lab:"));
    checkLayout->addWidget(labComboBox);
    checkLayout->addWidget(new QLabel("Date:"));
    checkLayout->addWidget(dateEdit);
    checkLayout->addWidget(new QLabel("From:"));
    checkLayout->addWidget(startTimeEdit);
    checkLayout->addWidget(new QLabel("To:"));
    checkLayout->addWidget(endTimeEdit);
    checkLayout->addWidget(checkAvailabilityBtn);
    checkLayout->addWidget(bookLabBtn);

    availabilityResultLabel = new QLabel("", this);
    availabilityResultLabel->setAlignment(Qt::AlignCenter);
    QFont f = availabilityResultLabel->font();
    f.setBold(true);
    availabilityResultLabel->setFont(f);

    mainLayout->addWidget(labsTable);
    mainLayout->addWidget(checkGroup);
    mainLayout->addWidget(availabilityResultLabel);

    connect(checkAvailabilityBtn, &QPushButton::clicked, this, &LaboratoryListWindow::handleCheckAvailability);
    connect(bookLabBtn, &QPushButton::clicked, this, &LaboratoryListWindow::handleBookLab);
}

void LaboratoryListWindow::loadLaboratories() {
    labsTable->setRowCount(0);
    labComboBox->clear();

    QSqlQuery q(DatabaseManager::getInstance()->getDb());
    if (q.exec("SELECT laboratory_id, laboratory_name, laboratory_code, location, capacity, status FROM LABORATORIES")) {
        int row = 0;
        while (q.next()) {
            labsTable->insertRow(row);
            int labId = q.value(0).toInt();
            QString labName = q.value(1).toString();

            labsTable->setItem(row, 0, new QTableWidgetItem(QString::number(labId)));
            labsTable->setItem(row, 1, new QTableWidgetItem(labName));
            labsTable->setItem(row, 2, new QTableWidgetItem(q.value(2).toString()));
            labsTable->setItem(row, 3, new QTableWidgetItem(q.value(3).toString()));
            labsTable->setItem(row, 4, new QTableWidgetItem(q.value(4).toString()));
            labsTable->setItem(row, 5, new QTableWidgetItem(q.value(5).toString()));

            labComboBox->addItem(labName, labId);
            row++;
        }
    }
}

void LaboratoryListWindow::handleCheckAvailability() {
    int labId = labComboBox->currentData().toInt();
    QString dateStr = dateEdit->date().toString("yyyy-MM-dd");
    QString startStr = startTimeEdit->time().toString("hh:mm");
    QString endStr = endTimeEdit->time().toString("hh:mm");

    BookingManager bm;
    bool available = bm.isLaboratoryAvailable(labId, dateStr, startStr, endStr);

    if (available) {
        availabilityResultLabel->setStyleSheet("color: green;");
        availabilityResultLabel->setText("AVAILABLE: Lab is free for the selected date and time slot.");
    } else {
        availabilityResultLabel->setStyleSheet("color: red;");
        availabilityResultLabel->setText("UNAVAILABLE (CONFLICT): Lab is ALREADY BOOKED for this time slot!");
    }
}

void LaboratoryListWindow::handleBookLab() {
    int labId = labComboBox->currentData().toInt();
    auto win = new BookingWindow(currentUserId, currentUserRole, labId, this);
    win->show();
}
