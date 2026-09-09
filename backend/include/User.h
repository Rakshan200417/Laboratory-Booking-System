#ifndef USER_H
#define USER_H

#include <string>

// Base class for all system users.
// Student, Lecturer, Administrator inherit from this (INHERITANCE).
// All fields are private (ENCAPSULATION) - accessed only via getters/setters.
class User {
protected:
    int userId;
    std::string eId;       // University E-ID
    std::string name;
    std::string email;
    std::string phone;
    std::string department;
    std::string status;    // Active / Inactive

public:
    User(int userId, std::string eId, std::string name, std::string email,
         std::string phone, std::string department, std::string status = "Active");
    virtual ~User() = default;

    // Getters
    int getUserId() const;
    std::string getEId() const;
    std::string getName() const;
    std::string getEmail() const;
    std::string getPhone() const;
    std::string getDepartment() const;
    std::string getStatus() const;

    // Setters
    void setEmail(const std::string &email);
    void setPhone(const std::string &phone);
    void setStatus(const std::string &status);

    // POLYMORPHISM: each derived user type describes itself differently.
    virtual std::string getRoleName() const = 0;   // pure virtual -> abstraction
    virtual std::string describe() const;
};

#endif // USER_H
