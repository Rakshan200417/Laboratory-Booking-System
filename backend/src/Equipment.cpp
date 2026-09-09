#include "Equipment.h"

Equipment::Equipment(int equipmentId, int laboratoryId, std::string name,
                      int quantityTotal, int quantityAvailable,
                      std::string condition, std::string status)
    : equipmentId(equipmentId), laboratoryId(laboratoryId), name(std::move(name)),
      quantityTotal(quantityTotal), quantityAvailable(quantityAvailable),
      condition(std::move(condition)), status(std::move(status)) {}

int Equipment::getEquipmentId() const { return equipmentId; }
int Equipment::getLaboratoryId() const { return laboratoryId; }
std::string Equipment::getName() const { return name; }
int Equipment::getQuantityTotal() const { return quantityTotal; }
int Equipment::getQuantityAvailable() const { return quantityAvailable; }
std::string Equipment::getCondition() const { return condition; }
std::string Equipment::getStatus() const { return status; }

bool Equipment::reserve(int quantity) {
    if (quantity <= 0 || quantity > quantityAvailable) return false;
    quantityAvailable -= quantity;
    return true;
}

void Equipment::release(int quantity) {
    quantityAvailable += quantity;
    if (quantityAvailable > quantityTotal) quantityAvailable = quantityTotal;
}
