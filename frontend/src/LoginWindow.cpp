#include "LoginWindow.h"
#include "DashboardWindow.h"
#include "DatabaseManager.h"
#include <QSqlQuery>
#include <QSqlError>
#include <QMessageBox>
#include <QGroupBox>
#include <QFormLayout>
#include <QHBoxLayout>

LoginWindow::LoginWindow(QWidget *parent) : QMainWindow(parent) {
    setupUi();
}

void LoginWindow::setupUi() {
    setWindowTitle("University Laboratory Booking System - Login");
    resize(420, 320);

    QWidget *central = new QWidget(this);
    setCentralWidget(central);

    QVBoxLayout *mainLayout = new QVBoxLayout(central);
    mainLayout->setContentsMargins(30, 30, 30, 30);

    QLabel *titleLabel = new QLabel("University Lab Booking System", this);
    QFont titleFont = titleLabel->font();
    titleFont.setPointSize(14);
    titleFont.setBold(true);
    titleLabel->setFont(titleFont);
    titleLabel->setAlignment(Qt::AlignCenter);

    QLabel *subTitle = new QLabel("Group 13 - Nano Science Department", this);
    subTitle->setAlignment(Qt::AlignCenter);

    QGroupBox *box = new QGroupBox("User Authentication", this);
    QFormLayout *formLayout = new QFormLayout(box);

    eIdEdit = new QLineEdit(this);
    eIdEdit->setPlaceholderText("e.g. ADMIN001, 249109, LEC001");
    eIdEdit->setText("ADMIN001");

    passwordEdit = new QLineEdit(this);
    passwordEdit->setEchoMode(QLineEdit::Password);
    passwordEdit->setText("admin123");

    formLayout->addRow("University E-ID:", eIdEdit);
    formLayout->addRow("Password:", passwordEdit);

    QHBoxLayout *btnLayout = new QHBoxLayout();
    loginButton = new QPushButton("Login", this);
    loginButton->setDefault(true);
    exitButton = new QPushButton("Exit", this);

    btnLayout->addWidget(loginButton);
    btnLayout->addWidget(exitButton);

    statusLabel = new QLabel("", this);
    statusLabel->setStyleSheet("color: red;");
    statusLabel->setAlignment(Qt::AlignCenter);

    mainLayout->addWidget(titleLabel);
    mainLayout->addWidget(subTitle);
    mainLayout->addSpacing(15);
    mainLayout->addWidget(box);
    mainLayout->addLayout(btnLayout);
    mainLayout->addWidget(statusLabel);

    connect(loginButton, &QPushButton::clicked, this, &LoginWindow::handleLogin);
    connect(exitButton, &QPushButton::clicked, this, &LoginWindow::close);
}

void LoginWindow::handleLogin() {
    QString eid = eIdEdit->text().trimmed();
    QString pwd = passwordEdit->text().trimmed();

    if (eid.isEmpty() || pwd.isEmpty()) {
        statusLabel->setText("Please enter both E-ID and Password.");
        return;
    }

    QSqlQuery query(DatabaseManager::getInstance()->getDb());
    query.prepare(
        "SELECT u.user_id, u.e_id, u.name, r.role_name, u.password, u.status "
        "FROM USERS u JOIN ROLES r ON u.role_id = r.role_id "
        "WHERE u.e_id = :eid"
    );
    query.bindValue(":eid", eid);

    if (!query.exec()) {
        QMessageBox::critical(this, "Database Error", query.lastError().text());
        return;
    }

    if (query.next()) {
        int userId = query.value(0).toInt();
        QString userEid = query.value(1).toString();
        QString name = query.value(2).toString();
        QString role = query.value(3).toString();
        QString dbPwd = query.value(4).toString();
        QString status = query.value(5).toString();

        if (status != "Active") {
            statusLabel->setText("Account is inactive. Please contact administrator.");
            return;
        }

        if (pwd != dbPwd) {
            statusLabel->setText("Invalid password. Please try again.");
            return;
        }

        // Authentication Success -> Open Dashboard
        DashboardWindow *dash = new DashboardWindow(userId, userEid, name, role);
        dash->show();
        this->close();
    } else {
        statusLabel->setText("User E-ID not found in system.");
    }
}
