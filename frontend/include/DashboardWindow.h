#ifndef DASHBOARDWINDOW_H
#define DASHBOARDWINDOW_H

#include <QMainWindow>
#include <QLabel>
#include <QPushButton>
#include <QTableWidget>

class DashboardWindow : public QMainWindow {
    Q_OBJECT

private:
    int userId;
    QString eId;
    QString userName;
    QString userRole;

    QLabel *userWelcomeLabel;
    QLabel *roleBadgeLabel;
    QLabel *statLabsLabel;
    QLabel *statBookingsLabel;
    QLabel *statPendingLabel;
    QLabel *statEquipmentLabel;

    QPushButton *labsButton;
    QPushButton *myBookingsButton;
    QPushButton *approvalsButton;
    QPushButton *equipmentButton;
    QPushButton *reportsButton;
    QPushButton *logoutButton;

    QTableWidget *recentActivityTable;

    void setupUi();
    void loadStatistics();
    void loadRecentActivity();

private slots:
    void openLabsWindow();
    void openBookingsWindow();
    void openApprovalsWindow();
    void openEquipmentWindow();
    void openReportsWindow();
    void handleLogout();

public:
    explicit DashboardWindow(int userId, const QString &eId, const QString &name, const QString &role, QWidget *parent = nullptr);
    ~DashboardWindow() override = default;
};

#endif // DASHBOARDWINDOW_H
