#include "DashboardWindow.h"
#include "LaboratoryListWindow.h"
#include "BookingWindow.h"
#include "ApprovalWindow.h"
#include "EquipmentWindow.h"
#include "ReportsWindow.h"
#include "LoginWindow.h"
#include "DatabaseManager.h"
#include <QSqlQuery>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGridLayout>
#include <QGroupBox>
#include <QHeaderView>
#include <QMessageBox>

DashboardWindow::DashboardWindow(int userId, const QString &eId, const QString &name, const QString &role, QWidget *parent)
    : QMainWindow(parent), userId(userId), eId(eId), userName(name), userRole(role) {
    setupUi();
    loadStatistics();
    loadRecentActivity();
}

void DashboardWindow::setupUi() {
    setWindowTitle("Lab Booking System - Dashboard (" + userRole + ")");
    resize(850, 600);

    QWidget *central = new QWidget(this);
    setCentralWidget(central);

    QVBoxLayout *mainLayout = new QVBoxLayout(central);
    mainLayout->setContentsMargins(20, 20, 20, 20);

    // Header Layout
    QHBoxLayout *headerLayout = new QHBoxLayout();
    userWelcomeLabel = new QLabel("Welcome, " + userName + " (" + eId + ")", this);
    QFont welcomeFont = userWelcomeLabel->font();
    welcomeFont.setPointSize(14);
    welcomeFont.setBold(true);
    userWelcomeLabel->setFont(welcomeFont);

    roleBadgeLabel = new QLabel("[" + userRole + "]", this);
    roleBadgeLabel->setStyleSheet("font-weight: bold; color: #2196F3; font-size: 14px;");

    logoutButton = new QPushButton("Logout", this);

    headerLayout->addWidget(userWelcomeLabel);
    headerLayout->addWidget(roleBadgeLabel);
    headerLayout->addStretch();
    headerLayout->addWidget(logoutButton);

    // Stats Grid
    QGridLayout *statsGrid = new QGridLayout();

    auto createStatCard = [](const QString &title, QLabel *&valLabel, const QString &bgColor) {
        QGroupBox *card = new QGroupBox(title);
        card->setStyleSheet("QGroupBox { font-weight: bold; }");
        QVBoxLayout *l = new QVBoxLayout(card);
        valLabel = new QLabel("0");
        QFont f = valLabel->font();
        f.setPointSize(20);
        f.setBold(true);
        valLabel->setFont(f);
        valLabel->setAlignment(Qt::AlignCenter);
        l->addWidget(valLabel);
        return card;
    };

    statsGrid->addWidget(createStatCard("Laboratories", statLabsLabel, "#E3F2FD"), 0, 0);
    statsGrid->addWidget(createStatCard("Total Bookings", statBookingsLabel, "#E8F5E9"), 0, 1);
    statsGrid->addWidget(createStatCard("Pending Approvals", statPendingLabel, "#FFF3E0"), 0, 2);
    statsGrid->addWidget(createStatCard("Lab Equipment", statEquipmentLabel, "#F3E5F5"), 0, 3);

    // Navigation Action Buttons
    QHBoxLayout *navLayout = new QHBoxLayout();
    labsButton = new QPushButton("View Laboratories", this);
    myBookingsButton = new QPushButton("Book / My Bookings", this);
    approvalsButton = new QPushButton("Manage Approvals", this);
    equipmentButton = new QPushButton("Equipment Inventory", this);
    reportsButton = new QPushButton("System Reports", this);

    // Disable admin features for non-admins
    if (userRole != "Administrator") {
        approvalsButton->setEnabled(false);
        approvalsButton->setToolTip("Requires Administrator privileges");
    }

    navLayout->addWidget(labsButton);
    navLayout->addWidget(myBookingsButton);
    navLayout->addWidget(approvalsButton);
    navLayout->addWidget(equipmentButton);
    navLayout->addWidget(reportsButton);

    // Recent Activity Table
    QGroupBox *tableBox = new QGroupBox("Recent System Activity / Bookings", this);
    QVBoxLayout *tableLayout = new QVBoxLayout(tableBox);
    recentActivityTable = new QTableWidget(this);
    recentActivityTable->setColumnCount(6);
    recentActivityTable->setHorizontalHeaderLabels({"Booking ID", "Laboratory", "User", "Date", "Time Slot", "Status"});
    recentActivityTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    recentActivityTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    tableLayout->addWidget(recentActivityTable);

    mainLayout->addLayout(headerLayout);
    mainLayout->addSpacing(10);
    mainLayout->addLayout(statsGrid);
    mainLayout->addSpacing(10);
    mainLayout->addLayout(navLayout);
    mainLayout->addSpacing(10);
    mainLayout->addWidget(tableBox);

    // Connections
    connect(labsButton, &QPushButton::clicked, this, &DashboardWindow::openLabsWindow);
    connect(myBookingsButton, &QPushButton::clicked, this, &DashboardWindow::openBookingsWindow);
    connect(approvalsButton, &QPushButton::clicked, this, &DashboardWindow::openApprovalsWindow);
    connect(equipmentButton, &QPushButton::clicked, this, &DashboardWindow::openEquipmentWindow);
    connect(reportsButton, &QPushButton::clicked, this, &DashboardWindow::openReportsWindow);
    connect(logoutButton, &QPushButton::clicked, this, &DashboardWindow::handleLogout);
}

void DashboardWindow::loadStatistics() {
    QSqlQuery q(DatabaseManager::getInstance()->getDb());

    if (q.exec("SELECT COUNT(*) FROM LABORATORIES") && q.next())
        statLabsLabel->setText(q.value(0).toString());

    if (q.exec("SELECT COUNT(*) FROM BOOKINGS") && q.next())
        statBookingsLabel->setText(q.value(0).toString());

    if (q.exec("SELECT COUNT(*) FROM BOOKINGS WHERE status = 'Pending'") && q.next())
        statPendingLabel->setText(q.value(0).toString());

    if (q.exec("SELECT COUNT(*) FROM LAB_EQUIPMENT") && q.next())
        statEquipmentLabel->setText(q.value(0).toString());
}

void DashboardWindow::loadRecentActivity() {
    recentActivityTable->setRowCount(0);
    QSqlQuery q(DatabaseManager::getInstance()->getDb());
    q.prepare(
        "SELECT b.booking_id, l.laboratory_name, u.name, b.booking_date, "
        "b.start_time || ' - ' || b.end_time, b.status "
        "FROM BOOKINGS b "
        "JOIN LABORATORIES l ON b.laboratory_id = l.laboratory_id "
        "JOIN USERS u ON b.user_id = u.user_id "
        "ORDER BY b.booking_id DESC LIMIT 10"
    );

    if (q.exec()) {
        int row = 0;
        while (q.next()) {
            recentActivityTable->insertRow(row);
            for (int col = 0; col < 6; ++col) {
                recentActivityTable->setItem(row, col, new QTableWidgetItem(q.value(col).toString()));
            }
            row++;
        }
    }
}

void DashboardWindow::openLabsWindow() {
    auto win = new LaboratoryListWindow(userId, userRole, this);
    win->show();
}

void DashboardWindow::openBookingsWindow() {
    auto win = new BookingWindow(userId, userRole, -1, this);
    win->show();
}

void DashboardWindow::openApprovalsWindow() {
    auto win = new ApprovalWindow(userId, this);
    win->show();
}

void DashboardWindow::openEquipmentWindow() {
    auto win = new EquipmentWindow(userId, userRole, this);
    win->show();
}

void DashboardWindow::openReportsWindow() {
    auto win = new ReportsWindow(this);
    win->show();
}

void DashboardWindow::handleLogout() {
    auto login = new LoginWindow();
    login->show();
    this->close();
}
