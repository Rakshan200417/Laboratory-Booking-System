#ifndef LOGINWINDOW_H
#define LOGINWINDOW_H

#include <QMainWindow>
#include <QLineEdit>
#include <QPushButton>
#include <QLabel>
#include <QVBoxLayout>

class LoginWindow : public QMainWindow {
    Q_OBJECT

private:
    QLineEdit *eIdEdit;
    QLineEdit *passwordEdit;
    QPushButton *loginButton;
    QPushButton *exitButton;
    QLabel *statusLabel;

    void setupUi();

private slots:
    void handleLogin();

public:
    explicit LoginWindow(QWidget *parent = nullptr);
    ~LoginWindow() override = default;
};

#endif // LOGINWINDOW_H
