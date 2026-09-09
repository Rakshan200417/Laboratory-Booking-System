#include "Lecturer.h"

Lecturer::Lecturer(int userId, std::string eId, std::string name, std::string email,
                    std::string phone, std::string department,
                    std::string employeeId, std::string designation)
    : User(userId, std::move(eId), std::move(name), std::move(email), std::move(phone), std::move(department)),
      employeeId(std::move(employeeId)), designation(std::move(designation)) {}

std::string Lecturer::getEmployeeId() const { return employeeId; }
std::string Lecturer::getDesignation() const { return designation; }
