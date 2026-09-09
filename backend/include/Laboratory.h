#ifndef LABORATORY_H
#define LABORATORY_H

#include <string>

class Laboratory {
private:
    int laboratoryId;
    std::string name;
    std::string code;
    std::string location;
    int capacity;
    std::string description;
    std::string status; // Available / Unavailable / Under Maintenance

public:
    Laboratory(int laboratoryId, std::string name, std::string code, std::string location,
               int capacity, std::string description, std::string status = "Available");

    int getLaboratoryId() const;
    std::string getName() const;
    std::string getCode() const;
    std::string getLocation() const;
    int getCapacity() const;
    std::string getDescription() const;
    std::string getStatus() const;

    void setStatus(const std::string &status);
    bool isBookable() const { return status == "Available"; }
};

#endif // LABORATORY_H
