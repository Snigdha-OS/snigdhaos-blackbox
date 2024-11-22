#ifndef SNIGDHAOSBLACKBOX_H
#define SNIGDHAOSBLACKBOX_H

#include <QMainWindow>
#include <QAbstractButton>
#include <QtNetwork/QNetworkAccessManager>

QT_BEGIN_NAMESPACE
namespace Ui {
class SnigdhaOSBlackbox;
}
QT_END_NAMESPACE

class SnigdhaOSBlackbox : public QMainWindow
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
    SnigdhaOSBlackbox(QWidget *parent = nullptr, QString state = "WELCOME");
    ~SnigdhaOSBlackbox();
private slots:
    void on_textWidget_buttonBox_clicked(QAbstractButton* button);
    void on_selectWidget_buttonBox_Clicked(QAbstractButton* button);

private:
    Ui::SnigdhaOSBlackbox *ui;
    QDateTime executable_modify_date;
    State currentState;

    void doInternetUpRequest();
    void doUpdate();
    void doApply();
    void populateSelectWidget();
    void populateSelectWidget(QString filename, QString label);
    void updateState(State state);
    void updateState(QString state);
    void relaunchSelf(QString param);
};
#endif // SNIGDHAOSBLACKBOX_H
