#include "EquipmentWindow.h"
#include "DatabaseManager.h"
#include <QSqlQuery>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QFormLayout>
#include <QGroupBox>
#include <QHeaderView>
#include <QMessageBox>

EquipmentWindow::EquipmentWindow(int userId, const QString &role, QWidget *parent)
    : QMainWindow(parent), userId(userId), userRole(role) {
    setupUi();
    loadEquipment();
}

void EquipmentWindow::setupUi() {
    setWindowTitle("Laboratory Equipment Management");
    resize(750, 500);

    QWidget *central = new QWidget(this);
    setCentralWidget(central);

    QVBoxLayout *mainLayout = new QVBoxLayout(central);
    mainLayout->setContentsMargins(15, 15, 15, 15);

    QGroupBox *filterGroup = new QGroupBox("Filter Equipment by Laboratory", this);
    QHBoxLayout *filterLayout = new QHBoxLayout(filterGroup);
    labFilterCombo = new QComboBox(this);
    labFilterCombo->addItem("All Laboratories", -1);

    QSqlQuery q(DatabaseManager::getInstance()->getDb());
    if (q.exec("SELECT laboratory_id, laboratory_name FROM LABORATORIES")) {
        while (q.next()) {
            labFilterCombo->addItem(q.value(1).toString(), q.value(0).toInt());
        }
    }

    filterLayout->addWidget(new QLabel("Laboratory:"));
    filterLayout->addWidget(labFilterCombo);
    filterLayout->addStretch();

    equipmentTable = new QTableWidget(this);
    equipmentTable->setColumnCount(7);
    equipmentTable->setHorizontalHeaderLabels({"ID", "Laboratory", "Equipment Name", "Total Qty", "Available Qty", "Condition", "Status"});
    equipmentTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    equipmentTable->setEditTriggers(QAbstractItemView::NoEditTriggers);

    QGroupBox *addGroup = new QGroupBox("Add New Equipment Item", this);
    QFormLayout *addLayout = new QFormLayout(addGroup);

    nameEdit = new QLineEdit(this);
    totalQtySpin = new QSpinBox(this);
    totalQtySpin->setRange(1, 100);
    totalQtySpin->setValue(1);

    availQtySpin = new QSpinBox(this);
    availQtySpin->setRange(0, 100);
    availQtySpin->setValue(1);

    conditionEdit = new QLineEdit(this);
    conditionEdit->setText("Good");

    addEquipmentBtn = new QPushButton("Add Equipment Item", this);

    addLayout->addRow("Equipment Name:", nameEdit);
    addLayout->addRow("Total Quantity:", totalQtySpin);
    addLayout->addRow("Available Quantity:", availQtySpin);
    addLayout->addRow("Condition:", conditionEdit);
    addLayout->addRow("", addEquipmentBtn);

    if (userRole != "Administrator") {
        addGroup->setEnabled(false);
        addGroup->setToolTip("Requires Administrator access to add equipment.");
    }

    mainLayout->addWidget(filterGroup);
    mainLayout->addWidget(equipmentTable);
    mainLayout->addWidget(addGroup);

    connect(addEquipmentBtn, &QPushButton::clicked, this, &EquipmentWindow::handleAddEquipment);
    connect(labFilterCombo, QOverload<int>::of(&QComboBox::currentIndexChanged), this, &EquipmentWindow::filterByLab);
}

void EquipmentWindow::loadEquipment() {
    equipmentTable->setRowCount(0);
    int selectedLabId = labFilterCombo->currentData().toInt();

    QSqlQuery q(DatabaseManager::getInstance()->getDb());
    QString sql = "SELECT e.equipment_id, l.laboratory_name, e.equipment_name, "
                  "e.quantity_total, e.quantity_available, e.condition, e.status "
                  "FROM LAB_EQUIPMENT e JOIN LABORATORIES l ON e.laboratory_id = l.laboratory_id ";

    if (selectedLabId != -1) {
        sql += "WHERE e.laboratory_id = :labId ";
    }
    sql += "ORDER BY e.equipment_id ASC";

    q.prepare(sql);
    if (selectedLabId != -1) q.bindValue(":labId", selectedLabId);

    if (q.exec()) {
        int row = 0;
        while (q.next()) {
            equipmentTable->insertRow(row);
            for (int col = 0; col < 7; ++col) {
                equipmentTable->setItem(row, col, new QTableWidgetItem(q.value(col).toString()));
            }
            row++;
        }
    }
}

void EquipmentWindow::filterByLab(int index) {
    Q_UNUSED(index);
    loadEquipment();
}

void EquipmentWindow::handleAddEquipment() {
    int labId = labFilterCombo->currentData().toInt();
    if (labId == -1) {
        QMessageBox::warning(this, "Select Lab", "Please select a specific laboratory to assign this equipment.");
        return;
    }

    QString name = nameEdit->text().trimmed();
    int total = totalQtySpin->value();
    int avail = availQtySpin->value();
    QString cond = conditionEdit->text().trimmed();

    if (name.isEmpty()) {
        QMessageBox::warning(this, "Validation Error", "Equipment name cannot be empty.");
        return;
    }

    QSqlQuery q(DatabaseManager::getInstance()->getDb());
    q.prepare("INSERT INTO LAB_EQUIPMENT (laboratory_id, equipment_name, quantity_total, quantity_available, condition, status) "
              "VALUES (:labId, :name, :total, :avail, :cond, 'Available')");
    q.bindValue(":labId", labId);
    q.bindValue(":name", name);
    q.bindValue(":total", total);
    q.bindValue(":avail", avail);
    q.bindValue(":cond", cond);

    if (q.exec()) {
        QMessageBox::information(this, "Success", "Equipment item added successfully.");
        nameEdit->clear();
        loadEquipment();
    } else {
        QMessageBox::critical(this, "Error", "Failed to insert equipment item.");
    }
}
