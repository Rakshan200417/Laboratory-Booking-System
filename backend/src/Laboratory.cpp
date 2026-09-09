#include "Laboratory.h"

Laboratory::Laboratory(int laboratoryId, std::string name, std::string code, std::string location,
                        int capacity, std::string description, std::string status)
    : laboratoryId(laboratoryId), name(std::move(name)), code(std::move(code)),
      location(std::move(location)), capacity(capacity),
      description(std::move(description)), status(std::move(status)) {}

int Laboratory::getLaboratoryId() const { return laboratoryId; }
std::string Laboratory::getName() const { return name; }
std::string Laboratory::getCode() const { return code; }
std::string Laboratory::getLocation() const { return location; }
int Laboratory::getCapacity() const { return capacity; }
std::string Laboratory::getDescription() const { return description; }
std::string Laboratory::getStatus() const { return status; }

void Laboratory::setStatus(const std::string &s) { status = s; }
