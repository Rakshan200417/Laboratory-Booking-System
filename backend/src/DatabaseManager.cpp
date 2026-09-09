#include "DatabaseManager.h"
#include <QSqlQuery>
#include <QSqlError>
#include <QFile>
#include <QTextStream>
#include <QDebug>

DatabaseManager *DatabaseManager::instance = nullptr;

DatabaseManager *DatabaseManager::getInstance() {
    if (!instance) instance = new DatabaseManager();
    return instance;
}

bool DatabaseManager::connect(const QString &dbPath) {
    db = QSqlDatabase::addDatabase("QSQLITE");
    db.setDatabaseName(dbPath);
    if (!db.open()) {
        qWarning() << "Database connection failed:" << db.lastError().text();
        return false;
    }
    return true;
}

bool DatabaseManager::runSchema(const QString &schemaFilePath) {
    QFile file(schemaFilePath);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        qWarning() << "Could not open schema file:" << schemaFilePath;
        return false;
    }

    QTextStream in(&file);
    QString cleanSql;
    while (!in.atEnd()) {
        QString line = in.readLine();
        int commentIdx = line.indexOf("--");
        if (commentIdx != -1) {
            line = line.left(commentIdx);
        }
        cleanSql += line + "\n";
    }
    file.close();

    const QStringList statements = cleanSql.split(';', Qt::SkipEmptyParts);
    QSqlQuery query(db);
    for (const QString &stmtRaw : statements) {
        QString stmt = stmtRaw.trimmed();
        if (stmt.isEmpty()) continue;
        if (!query.exec(stmt)) {
            qWarning() << "Schema statement failed:" << query.lastError().text()
                       << "\nStatement was:" << stmt;
        }
    }
    return true;
}

QSqlDatabase &DatabaseManager::getDb() { return db; }

void DatabaseManager::close() {
    if (db.isOpen()) db.close();
}
