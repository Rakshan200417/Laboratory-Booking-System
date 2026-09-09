#include "Administrator.h"

Administrator::Administrator(int userId, std::string eId, std::string name, std::string email,
                              std::string phone, std::string department)
    : User(userId, std::move(eId), std::move(name), std::move(email), std::move(phone), std::move(department)) {}
