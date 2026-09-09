#include "Student.h"

Student::Student(int userId, std::string eId, std::string name, std::string email,
                  std::string phone, std::string department, int yearOfStudy,
                  std::string indexNumber, std::string program, std::string batch)
    : User(userId, std::move(eId), std::move(name), std::move(email), std::move(phone), std::move(department)),
      yearOfStudy(yearOfStudy), indexNumber(std::move(indexNumber)),
      program(std::move(program)), batch(std::move(batch)) {}

int Student::getYearOfStudy() const { return yearOfStudy; }
std::string Student::getIndexNumber() const { return indexNumber; }
std::string Student::getProgram() const { return program; }
std::string Student::getBatch() const { return batch; }
