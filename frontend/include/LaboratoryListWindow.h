#ifndef LABORATORYLISTWINDOW_H
#define LABORATORYLISTWINDOW_H

#include <QMainWindow>
#include <QTableWidget>
#include <QDateEdit>
#include <QTimeEdit>
#include <QPushButton>
#include <QLabel>
#include <QComboBox>

class LaboratoryListWindow : public QMainWindow {
    Q_OBJECT

private:
    int currentUserId;
    QString currentUserRole;

    QTableWidget *labsTable;
    QComboBox *labComboBox;
    QDateEdit *dateEdit;
    QTimeEdit *startTimeEdit;
    QTimeEdit *endTimeEdit;
    QPushButton *checkAvailabilityBtn;
    QPushButton *bookLabBtn;
    QLabel *availabilityResultLabel;

    void setupUi();
    void loadLaboratories();

private slots:
    void handleCheckAvailability();
    void handleBookLab();

public:
    explicit LaboratoryListWindow(int userId, const QString &role, QWidget *parent = nullptr);
    ~LaboratoryListWindow() override = default;
};

#endif // LABORATORYLISTWINDOW_H
