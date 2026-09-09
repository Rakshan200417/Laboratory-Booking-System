#ifndef BOOKINGWINDOW_H
#define BOOKINGWINDOW_H

#include <QMainWindow>
#include <QComboBox>
#include <QDateEdit>
#include <QTimeEdit>
#include <QTextEdit>
#include <QPushButton>
#include <QLabel>
#include <QTableWidget>

class BookingWindow : public QMainWindow {
    Q_OBJECT

private:
    int userId;
    QString userRole;
    int preselectedLabId;

    QComboBox *labSelectCombo;
    QDateEdit *datePicker;
    QTimeEdit *startTimePicker;
    QTimeEdit *endTimePicker;
    QTextEdit *purposeTextEdit;
    QPushButton *submitBookingBtn;
    QPushButton *cancelBtn;
    QLabel *statusFeedbackLabel;

    QTableWidget *myBookingsTable;

    void setupUi();
    void loadLabs();
    void loadMyBookings();

private slots:
    void handleSubmitBooking();
    void handleCancelBooking();

public:
    explicit BookingWindow(int userId, const QString &role, int labId = -1, QWidget *parent = nullptr);
    ~BookingWindow() override = default;
};

#endif // BOOKINGWINDOW_H
