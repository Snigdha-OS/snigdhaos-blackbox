#ifndef SNIGDHAOSBLACKBOX_H
#define SNIGDHAOSBLACKBOX_H

#include <QMainWindow>
#include <QAbstractButton>
#include <QNetwork/QNetworkAccessManager>

QT_BEGIN_NAMESPACE
namespace Ui {
class SnigdhaOSBlackBox;
}
QT_END_NAMESPACE

class SnigdhaOSBlackBox : public QMainWindow
{
    Q_OBJECT

public:
    enum class State {
        QUIT,
        WELCOME,
        INTERNET,
        UPDATE,
        UPDATE_RETRY,
        SELECT,
        APPLY,
        APPLY_RETRY,
        SUCCESS
    };

    SnigdhaOSBlackBox(QWidget *parent = nullptr, QString state = "WELCOME");
    ~SnigdhaOSBlackBox();

private:
    Ui::SnigdhaOSBlackBox *ui;
    QDateTime executable_modify_date;
    State currentState;

    void doInternetUpRequest();
};
#endif // SNIGDHAOSBLACKBOX_H
