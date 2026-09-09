#ifndef BOOKING_H
#define BOOKING_H

#include <string>

class Booking {
private:
    int bookingId;
    int userId;
    int laboratoryId;
    std::string purpose;
    std::string bookingDate; // "YYYY-MM-DD"
    std::string startTime;   // "HH:MM"
    std::string endTime;     // "HH:MM"
    std::string status;      // Pending / Approved / Rejected / Cancelled / Completed

public:
    Booking(int bookingId, int userId, int laboratoryId, std::string purpose,
            std::string bookingDate, std::string startTime, std::string endTime,
            std::string status = "Pending");

    int getBookingId() const;
    int getUserId() const;
    int getLaboratoryId() const;
    std::string getPurpose() const;
    std::string getBookingDate() const;
    std::string getStartTime() const;
    std::string getEndTime() const;
    std::string getStatus() const;

    void setStatus(const std::string &status);

    // Returns true if this booking's time range overlaps with [otherStart, otherEnd)
    // on the same date. Used by BookingManager for double-booking prevention.
    bool overlapsWith(const std::string &otherDate,
                       const std::string &otherStart,
                       const std::string &otherEnd) const;
};

#endif // BOOKING_H
