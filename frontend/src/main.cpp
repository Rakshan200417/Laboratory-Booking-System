#include <QApplication>
#include "DatabaseManager.h"
#include "LoginWindow.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    // 1. Connect to (or create) SQLite database
    if (!DatabaseManager::getInstance()->connect("lab_booking.db")) {
        return 1;
    }

    // 2. Initialize schema from backend/db/schema.sql on launch
    DatabaseManager::getInstance()->runSchema("backend/db/schema.sql");

    // 3. Launch Login Window
    LoginWindow loginWindow;
    loginWindow.show();

    int result = app.exec();
    DatabaseManager::getInstance()->close();
    return result;
}
