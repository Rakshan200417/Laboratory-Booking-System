#include "BookingWindow.h"
#include "BookingManager.h"
#include "DatabaseManager.h"
#include <QSqlQuery>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFormLayout>
#include <QGroupBox>
#include <QMessageBox>
#include <QHeaderView>
#include <QDate>

BookingWindow::BookingWindow(int userId, const QString &role, int labId, QWidget *parent)
    : QMainWindow(parent), userId(userId), userRole(role), preselectedLabId(labId) {
    setupUi();
    loadLabs();
    loadMyBookings();
}

void BookingWindow::setupUi() {
    setWindowTitle("Laboratory Booking Portal");
    resize(750, 550);

    QWidget *central = new QWidget(this);
    setCentralWidget(central);

    QVBoxLayout *mainLayout = new QVBoxLayout(central);
    mainLayout->setContentsMargins(15, 15, 15, 15);

    QGroupBox *formGroup = new QGroupBox("Create New Laboratory Booking", this);
    QFormLayout *formLayout = new QFormLayout(formGroup);

    labSelectCombo = new QComboBox(this);

    datePicker = new QDateEdit(QDate::currentDate().addDays(1), this);
    datePicker->setDisplayFormat("dd/MM/yyyy");
    datePicker->setCalendarPopup(true);

    startTimePicker = new QTimeEdit(QTime(10, 0), this);
    endTimePicker = new QTimeEdit(QTime(12, 0), this);

    purposeTextEdit = new QTextEdit(this);
    purposeTextEdit->setPlaceholderText("Describe the research activity or lab practical purpose...");
    purposeTextEdit->setMaximumHeight(60);

    submitBookingBtn = new QPushButton("Submit Booking Request", this);
    cancelBtn = new QPushButton("Close", this);

    QHBoxLayout *btnLayout = new QHBoxLayout();
    btnLayout->addWidget(submitBookingBtn);
    btnLayout->addWidget(cancelBtn);

    formLayout->addRow("Laboratory:", labSelectCombo);
    formLayout->addRow("Date:", datePicker);
    formLayout->addRow("Start Time:", startTimePicker);
    formLayout->addRow("End Time:", endTimePicker);
    formLayout->addRow("Purpose:", purposeTextEdit);
    formLayout->addRow("", btnLayout);

    statusFeedbackLabel = new QLabel("", this);
    statusFeedbackLabel->setAlignment(Qt::AlignCenter);

    QGroupBox *tableGroup = new QGroupBox("Your Submitted Bookings History", this);
    QVBoxLayout *tableLayout = new QVBoxLayout(tableGroup);

    myBookingsTable = new QTableWidget(this);
    myBookingsTable->setColumnCount(6);
    myBookingsTable->setHorizontalHeaderLabels({"Booking ID", "Laboratory", "Date", "Start", "End", "Status"});
    myBookingsTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    myBookingsTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    tableLayout->addWidget(myBookingsTable);

    mainLayout->addWidget(formGroup);
    mainLayout->addWidget(statusFeedbackLabel);
    mainLayout->addWidget(tableGroup);

    connect(submitBookingBtn, &QPushButton::clicked, this, &BookingWindow::handleSubmitBooking);
    connect(cancelBtn, &QPushButton::clicked, this, &BookingWindow::close);
}

void BookingWindow::loadLabs() {
    labSelectCombo->clear();
    QSqlQuery q(DatabaseManager::getInstance()->getDb());
    if (q.exec("SELECT laboratory_id, laboratory_name FROM LABORATORIES WHERE status = 'Available'")) {
        while (q.next()) {
            labSelectCombo->addItem(q.value(1).toString(), q.value(0).toInt());
        }
    }
    if (preselectedLabId != -1) {
        int idx = labSelectCombo->findData(preselectedLabId);
        if (idx != -1) labSelectCombo->setCurrentIndex(idx);
    }
}

void BookingWindow::loadMyBookings() {
    myBookingsTable->setRowCount(0);
    QSqlQuery q(DatabaseManager::getInstance()->getDb());
    q.prepare(
        "SELECT b.booking_id, l.laboratory_name, b.booking_date, b.start_time, b.end_time, b.status "
        "FROM BOOKINGS b JOIN LABORATORIES l ON b.laboratory_id = l.laboratory_id "
        "WHERE b.user_id = :uid ORDER BY b.booking_id DESC"
    );
    q.bindValue(":uid", userId);

    if (q.exec()) {
        int row = 0;
        while (q.next()) {
            myBookingsTable->insertRow(row);
            for (int col = 0; col < 6; ++col) {
                myBookingsTable->setItem(row, col, new QTableWidgetItem(q.value(col).toString()));
            }
            row++;
        }
    }
}

void BookingWindow::handleSubmitBooking() {
    int labId = labSelectCombo->currentData().toInt();
    QString dateStr = datePicker->date().toString("yyyy-MM-dd");
    QString startStr = startTimePicker->time().toString("hh:mm");
    QString endStr = endTimePicker->time().toString("hh:mm");
    QString purpose = purposeTextEdit->toPlainText().trimmed();

    if (purpose.isEmpty()) {
        QMessageBox::warning(this, "Validation Error", "Please provide a purpose for the lab booking.");
        return;
    }

    if (startStr >= endStr) {
        QMessageBox::warning(this, "Validation Error", "End time must be later than start time.");
        return;
    }

    BookingManager bm;
    int resultId = bm.createBooking(userId, labId, purpose, dateStr, startStr, endStr);

    if (resultId > 0) {
        QMessageBox::information(this, "Booking Created", QString("Booking request #%1 submitted successfully and is pending approval.").arg(resultId));
        purposeTextEdit->clear();
        loadMyBookings();
    } else {
        QMessageBox::critical(this, "Double Booking Prevented",
            "DOUBLE-BOOKING PREVENTED:\nThe selected laboratory is ALREADY booked for this date and time slot!\nPlease select a different time or date.");
    }
}

void BookingWindow::handleCancelBooking() {
    close();
}
