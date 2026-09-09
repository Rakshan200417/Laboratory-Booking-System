#ifndef STUDENT_H
#define STUDENT_H

#include "User.h"

class Student : public User {
private:
    int yearOfStudy;
    std::string indexNumber;
    std::string program;
    std::string batch;

public:
    Student(int userId, std::string eId, std::string name, std::string email,
            std::string phone, std::string department, int yearOfStudy,
            std::string indexNumber, std::string program, std::string batch);

    int getYearOfStudy() const;
    std::string getIndexNumber() const;
    std::string getProgram() const;
    std::string getBatch() const;

    std::string getRoleName() const override { return "Student"; }
};

#endif // STUDENT_H
