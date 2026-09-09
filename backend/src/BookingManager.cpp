#include "BookingManager.h"
#include "DatabaseManager.h"
#include <QSqlQuery>
#include <QVariant>

bool BookingManager::isLaboratoryAvailable(int laboratoryId, const QString &date,
                                            const QString &startTime, const QString &endTime) {
    QSqlQuery query(DatabaseManager::getInstance()->getDb());
    // Overlap rule: existing.start < new.end AND existing.end > new.start
    query.prepare(
        "SELECT COUNT(*) FROM BOOKINGS "
        "WHERE laboratory_id = :labId "
        "AND booking_date = :date "
        "AND status NOT IN ('Rejected', 'Cancelled') "
        "AND start_time < :endTime "
        "AND end_time > :startTime"
    );
    query.bindValue(":labId", laboratoryId);
    query.bindValue(":date", date);
    query.bindValue(":endTime", endTime);
    query.bindValue(":startTime", startTime);

    if (!query.exec()) return false; // fail safe: treat as unavailable on error
    if (query.next()) {
        return query.value(0).toInt() == 0;
    }
    return false;
}

int BookingManager::createBooking(int userId, int laboratoryId, const QString &purpose,
                                   const QString &date, const QString &startTime, const QString &endTime) {
    if (!isLaboratoryAvailable(laboratoryId, date, startTime, endTime)) {
        return -1; // reject: this IS the double-booking prevention in action
    }

    QSqlQuery query(DatabaseManager::getInstance()->getDb());
    query.prepare(
        "INSERT INTO BOOKINGS (user_id, laboratory_id, purpose, booking_date, start_time, end_time, status) "
        "VALUES (:userId, :labId, :purpose, :date, :startTime, :endTime, 'Pending')"
    );
    query.bindValue(":userId", userId);
    query.bindValue(":labId", laboratoryId);
    query.bindValue(":purpose", purpose);
    query.bindValue(":date", date);
    query.bindValue(":startTime", startTime);
    query.bindValue(":endTime", endTime);

    if (!query.exec()) return -1;
    return query.lastInsertId().toInt();
}

bool BookingManager::approveBooking(int bookingId, int approvedByUserId, const QString &remarks) {
    QSqlQuery update(DatabaseManager::getInstance()->getDb());
    update.prepare("UPDATE BOOKINGS SET status = 'Approved', updated_at = CURRENT_TIMESTAMP WHERE booking_id = :id");
    update.bindValue(":id", bookingId);
    if (!update.exec()) return false;

    QSqlQuery log(DatabaseManager::getInstance()->getDb());
    log.prepare("INSERT INTO APPROVALS (booking_id, approved_by, decision, remarks) "
                "VALUES (:bid, :uid, 'Approved', :remarks)");
    log.bindValue(":bid", bookingId);
    log.bindValue(":uid", approvedByUserId);
    log.bindValue(":remarks", remarks);
    return log.exec();
}

bool BookingManager::rejectBooking(int bookingId, int approvedByUserId, const QString &remarks) {
    QSqlQuery update(DatabaseManager::getInstance()->getDb());
    update.prepare("UPDATE BOOKINGS SET status = 'Rejected', updated_at = CURRENT_TIMESTAMP WHERE booking_id = :id");
    update.bindValue(":id", bookingId);
    if (!update.exec()) return false;

    QSqlQuery log(DatabaseManager::getInstance()->getDb());
    log.prepare("INSERT INTO APPROVALS (booking_id, approved_by, decision, remarks) "
                "VALUES (:bid, :uid, 'Rejected', :remarks)");
    log.bindValue(":bid", bookingId);
    log.bindValue(":uid", approvedByUserId);
    log.bindValue(":remarks", remarks);
    return log.exec();
}

bool BookingManager::cancelBooking(int bookingId, int cancelledByUserId, const QString &reason) {
    QSqlQuery update(DatabaseManager::getInstance()->getDb());
    update.prepare("UPDATE BOOKINGS SET status = 'Cancelled', updated_at = CURRENT_TIMESTAMP WHERE booking_id = :id");
    update.bindValue(":id", bookingId);
    if (!update.exec()) return false;

    QSqlQuery log(DatabaseManager::getInstance()->getDb());
    log.prepare("INSERT INTO CANCELLATIONS (booking_id, cancelled_by, reason) "
                "VALUES (:bid, :uid, :reason)");
    log.bindValue(":bid", bookingId);
    log.bindValue(":uid", cancelledByUserId);
    log.bindValue(":reason", reason);
    return log.exec();
}

std::vector<Booking> BookingManager::getBookingsForLab(int laboratoryId, const QString &date) {
    std::vector<Booking> results;
    QSqlQuery query(DatabaseManager::getInstance()->getDb());
    query.prepare("SELECT booking_id, user_id, laboratory_id, purpose, booking_date, "
                  "start_time, end_time, status FROM BOOKINGS "
                  "WHERE laboratory_id = :labId AND booking_date = :date");
    query.bindValue(":labId", laboratoryId);
    query.bindValue(":date", date);

    if (query.exec()) {
        while (query.next()) {
            results.emplace_back(
                query.value(0).toInt(),
                query.value(1).toInt(),
                query.value(2).toInt(),
                query.value(3).toString().toStdString(),
                query.value(4).toString().toStdString(),
                query.value(5).toString().toStdString(),
                query.value(6).toString().toStdString(),
                query.value(7).toString().toStdString()
            );
        }
    }
    return results;
}
