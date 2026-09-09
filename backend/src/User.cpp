#include "User.h"

User::User(int userId, std::string eId, std::string name, std::string email,
           std::string phone, std::string department, std::string status)
    : userId(userId), eId(std::move(eId)), name(std::move(name)),
      email(std::move(email)), phone(std::move(phone)),
      department(std::move(department)), status(std::move(status)) {}

int User::getUserId() const { return userId; }
std::string User::getEId() const { return eId; }
std::string User::getName() const { return name; }
std::string User::getEmail() const { return email; }
std::string User::getPhone() const { return phone; }
std::string User::getDepartment() const { return department; }
std::string User::getStatus() const { return status; }

void User::setEmail(const std::string &e) { email = e; }
void User::setPhone(const std::string &p) { phone = p; }
void User::setStatus(const std::string &s) { status = s; }

std::string User::describe() const {
    return name + " (" + eId + ") - " + getRoleName();
}
