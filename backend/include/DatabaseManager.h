#ifndef DATABASEMANAGER_H
#define DATABASEMANAGER_H

#include <QSqlDatabase>
#include <QString>

// Singleton wrapper around the SQLite connection.
// Everything else (BookingManager, UI screens) goes through this
// instead of touching QSqlDatabase directly - keeps DB access in one place.
class DatabaseManager {
private:
    DatabaseManager() = default;
    static DatabaseManager *instance;
    QSqlDatabase db;

public:
    static DatabaseManager *getInstance();

    bool connect(const QString &dbPath = "lab_booking.db");
    bool runSchema(const QString &schemaFilePath); // executes db/schema.sql on first run
    QSqlDatabase &getDb();
    void close();
};

#endif // DATABASEMANAGER_H
