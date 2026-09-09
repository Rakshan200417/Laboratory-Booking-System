#ifndef EQUIPMENT_H
#define EQUIPMENT_H

#include <string>

class Equipment {
private:
    int equipmentId;
    int laboratoryId;
    std::string name;
    int quantityTotal;
    int quantityAvailable;
    std::string condition;
    std::string status; // Available / Unavailable / Maintenance

public:
    Equipment(int equipmentId, int laboratoryId, std::string name,
              int quantityTotal, int quantityAvailable,
              std::string condition, std::string status = "Available");

    int getEquipmentId() const;
    int getLaboratoryId() const;
    std::string getName() const;
    int getQuantityTotal() const;
    int getQuantityAvailable() const;
    std::string getCondition() const;
    std::string getStatus() const;

    bool reserve(int quantity);   // decreases quantityAvailable if enough stock
    void release(int quantity);   // returns stock after cancellation
};

#endif // EQUIPMENT_H
