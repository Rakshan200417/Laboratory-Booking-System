#ifndef LECTURER_H
#define LECTURER_H

#include "User.h"

class Lecturer : public User {
private:
    std::string employeeId;
    std::string designation;

public:
    Lecturer(int userId, std::string eId, std::string name, std::string email,
              std::string phone, std::string department,
              std::string employeeId, std::string designation);

    std::string getEmployeeId() const;
    std::string getDesignation() const;

    std::string getRoleName() const override { return "Lecturer"; }
};

#endif // LECTURER_H
