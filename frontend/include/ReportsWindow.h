#ifndef REPORTSWINDOW_H
#define REPORTSWINDOW_H

#include <QMainWindow>
#include <QTableWidget>
#include <QComboBox>
#include <QLabel>
#include <QPushButton>

class ReportsWindow : public QMainWindow {
    Q_OBJECT

private:
    QTableWidget *reportsTable;
    QComboBox *statusFilterCombo;
    QLabel *totalBookingsVal;
    QLabel *approvedVal;
    QLabel *rejectedVal;
    QLabel *pendingVal;
    QPushButton *exportPdfBtn;

    void setupUi();
    void loadReports();

private slots:
    void applyFilter();

public:
    explicit ReportsWindow(QWidget *parent = nullptr);
    ~ReportsWindow() override = default;
};

#endif // REPORTSWINDOW_H
