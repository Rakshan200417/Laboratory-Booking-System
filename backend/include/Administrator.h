#ifndef ADMINISTRATOR_H
#define ADMINISTRATOR_H

#include "User.h"

class Administrator : public User {
public:
    Administrator(int userId, std::string eId, std::string name, std::string email,
                    std::string phone, std::string department);

    std::string getRoleName() const override { return "Administrator"; }

    // Administrator-specific actions call into BookingManager in practice;
    // kept here only as intent markers for the OOP write-up.
    bool canApproveBookings() const { return true; }
};

#endif // ADMINISTRATOR_H
