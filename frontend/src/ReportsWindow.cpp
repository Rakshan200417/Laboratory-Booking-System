#include "ReportsWindow.h"
#include "DatabaseManager.h"
#include <QSqlQuery>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGroupBox>
#include <QHeaderView>
#include <QMessageBox>

ReportsWindow::ReportsWindow(QWidget *parent) : QMainWindow(parent) {
    setupUi();
    loadReports();
}

void ReportsWindow::setupUi() {
    setWindowTitle("Laboratory System - Analytics & Reports");
    resize(800, 550);

    QWidget *central = new QWidget(this);
    setCentralWidget(central);

    QVBoxLayout *mainLayout = new QVBoxLayout(central);
    mainLayout->setContentsMargins(15, 15, 15, 15);

    // Summary Metric Bar
    QHBoxLayout *metricsLayout = new QHBoxLayout();
    auto createMetricWidget = [](const QString &title, QLabel *&valLabel) {
        QGroupBox *box = new QGroupBox(title);
        QVBoxLayout *l = new QVBoxLayout(box);
        valLabel = new QLabel("0");
        QFont f = valLabel->font();
        f.setPointSize(16);
        f.setBold(true);
        valLabel->setFont(f);
        valLabel->setAlignment(Qt::AlignCenter);
        l->addWidget(valLabel);
        return box;
    };

    metricsLayout->addWidget(createMetricWidget("Total Requests", totalBookingsVal));
    metricsLayout->addWidget(createMetricWidget("Approved", approvedVal));
    metricsLayout->addWidget(createMetricWidget("Rejected", rejectedVal));
    metricsLayout->addWidget(createMetricWidget("Pending", pendingVal));

    // Filter Bar
    QHBoxLayout *filterLayout = new QHBoxLayout();
    statusFilterCombo = new QComboBox(this);
    statusFilterCombo->addItem("All Statuses", "All");
    statusFilterCombo->addItem("Approved Only", "Approved");
    statusFilterCombo->addItem("Pending Only", "Pending");
    statusFilterCombo->addItem("Rejected Only", "Rejected");

    exportPdfBtn = new QPushButton("Refresh Report", this);

    filterLayout->addWidget(new QLabel("Filter by Booking Status:"));
    filterLayout->addWidget(statusFilterCombo);
    filterLayout->addStretch();
    filterLayout->addWidget(exportPdfBtn);

    // Reports Table
    reportsTable = new QTableWidget(this);
    reportsTable->setColumnCount(7);
    reportsTable->setHorizontalHeaderLabels({"ID", "Requester", "Role", "Laboratory", "Date", "Slot", "Status"});
    reportsTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    reportsTable->setEditTriggers(QAbstractItemView::NoEditTriggers);

    mainLayout->addLayout(metricsLayout);
    mainLayout->addSpacing(10);
    mainLayout->addLayout(filterLayout);
    mainLayout->addWidget(reportsTable);

    connect(statusFilterCombo, QOverload<int>::of(&QComboBox::currentIndexChanged), this, &ReportsWindow::applyFilter);
    connect(exportPdfBtn, &QPushButton::clicked, this, &ReportsWindow::loadReports);
}

void ReportsWindow::loadReports() {
    reportsTable->setRowCount(0);

    QSqlQuery qMetrics(DatabaseManager::getInstance()->getDb());
    if (qMetrics.exec("SELECT COUNT(*), "
                      "SUM(CASE WHEN status='Approved' THEN 1 ELSE 0 END), "
                      "SUM(CASE WHEN status='Rejected' THEN 1 ELSE 0 END), "
                      "SUM(CASE WHEN status='Pending' THEN 1 ELSE 0 END) FROM BOOKINGS") && qMetrics.next()) {
        totalBookingsVal->setText(qMetrics.value(0).toString());
        approvedVal->setText(qMetrics.value(1).toString());
        rejectedVal->setText(qMetrics.value(2).toString());
        pendingVal->setText(qMetrics.value(3).toString());
    }

    applyFilter();
}

void ReportsWindow::applyFilter() {
    reportsTable->setRowCount(0);
    QString status = statusFilterCombo->currentData().toString();

    QSqlQuery q(DatabaseManager::getInstance()->getDb());
    QString sql = "SELECT b.booking_id, u.name, r.role_name, l.laboratory_name, b.booking_date, "
                  "b.start_time || ' - ' || b.end_time, b.status "
                  "FROM BOOKINGS b "
                  "JOIN USERS u ON b.user_id = u.user_id "
                  "JOIN ROLES r ON u.role_id = r.role_id "
                  "JOIN LABORATORIES l ON b.laboratory_id = l.laboratory_id ";

    if (status != "All") {
        sql += "WHERE b.status = :status ";
    }
    sql += "ORDER BY b.booking_id DESC";

    q.prepare(sql);
    if (status != "All") q.bindValue(":status", status);

    if (q.exec()) {
        int row = 0;
        while (q.next()) {
            reportsTable->insertRow(row);
            for (int col = 0; col < 7; ++col) {
                reportsTable->setItem(row, col, new QTableWidgetItem(q.value(col).toString()));
            }
            row++;
        }
    }
}
