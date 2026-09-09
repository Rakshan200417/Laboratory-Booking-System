#ifndef EQUIPMENTWINDOW_H
#define EQUIPMENTWINDOW_H

#include <QMainWindow>
#include <QTableWidget>
#include <QComboBox>
#include <QLineEdit>
#include <QSpinBox>
#include <QPushButton>

class EquipmentWindow : public QMainWindow {
    Q_OBJECT

private:
    int userId;
    QString userRole;

    QTableWidget *equipmentTable;
    QComboBox *labFilterCombo;
    QLineEdit *nameEdit;
    QSpinBox *totalQtySpin;
    QSpinBox *availQtySpin;
    QLineEdit *conditionEdit;
    QPushButton *addEquipmentBtn;
    QPushButton *refreshBtn;

    void setupUi();
    void loadEquipment();

private slots:
    void handleAddEquipment();
    void filterByLab(int index);

public:
    explicit EquipmentWindow(int userId, const QString &role, QWidget *parent = nullptr);
    ~EquipmentWindow() override = default;
};

#endif // EQUIPMENTWINDOW_H
