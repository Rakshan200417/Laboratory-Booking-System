#ifndef BOOKINGMANAGER_H
#define BOOKINGMANAGER_H

#include <QString>
#include <vector>
#include "Booking.h"

// This is the class that demonstrates the "double booking prevention" feature
// called out in the proposal. Everything routes through here, not through
// raw SQL scattered across the UI.
class BookingManager {
public:
    // Returns true if the laboratory is free for the requested date/time.
    bool isLaboratoryAvailable(int laboratoryId, const QString &date,
                                const QString &startTime, const QString &endTime);

    // Creates a booking with status "Pending" if available; returns new booking_id,
    // or -1 if the slot is already booked.
    int createBooking(int userId, int laboratoryId, const QString &purpose,
                       const QString &date, const QString &startTime, const QString &endTime);

    bool approveBooking(int bookingId, int approvedByUserId, const QString &remarks = "");
    bool rejectBooking(int bookingId, int approvedByUserId, const QString &remarks = "");
    bool cancelBooking(int bookingId, int cancelledByUserId, const QString &reason = "");

    std::vector<Booking> getBookingsForLab(int laboratoryId, const QString &date);
};

#endif // BOOKINGMANAGER_H
