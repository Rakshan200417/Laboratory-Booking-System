#ifndef APPROVALWINDOW_H
#define APPROVALWINDOW_H

#include <QMainWindow>
#include <QTableWidget>
#include <QLineEdit>
#include <QPushButton>

class ApprovalWindow : public QMainWindow {
    Q_OBJECT

private:
    int adminUserId;
    QTableWidget *pendingTable;
    QLineEdit *remarksEdit;
    QPushButton *approveBtn;
    QPushButton *rejectBtn;
    QPushButton *refreshBtn;

    void setupUi();
    void loadPendingBookings();

private slots:
    void handleApprove();
    void handleReject();

public:
    explicit ApprovalWindow(int adminUserId, QWidget *parent = nullptr);
    ~ApprovalWindow() override = default;
};

#endif // APPROVALWINDOW_H
