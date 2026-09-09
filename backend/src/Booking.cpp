#include "Booking.h"

Booking::Booking(int bookingId, int userId, int laboratoryId, std::string purpose,
                  std::string bookingDate, std::string startTime, std::string endTime,
                  std::string status)
    : bookingId(bookingId), userId(userId), laboratoryId(laboratoryId),
      purpose(std::move(purpose)), bookingDate(std::move(bookingDate)),
      startTime(std::move(startTime)), endTime(std::move(endTime)),
      status(std::move(status)) {}

int Booking::getBookingId() const { return bookingId; }
int Booking::getUserId() const { return userId; }
int Booking::getLaboratoryId() const { return laboratoryId; }
std::string Booking::getPurpose() const { return purpose; }
std::string Booking::getBookingDate() const { return bookingDate; }
std::string Booking::getStartTime() const { return startTime; }
std::string Booking::getEndTime() const { return endTime; }
std::string Booking::getStatus() const { return status; }

void Booking::setStatus(const std::string &s) { status = s; }

bool Booking::overlapsWith(const std::string &otherDate,
                           const std::string &otherStart,
                           const std::string &otherEnd) const {
    if (bookingDate != otherDate) return false;
    if (status == "Rejected" || status == "Cancelled") return false;

    // "HH:MM" strings compare correctly lexicographically for overlap checks.
    // Overlap if: existing.start < other.end AND existing.end > other.start
    return (startTime < otherEnd) && (endTime > otherStart);
}
