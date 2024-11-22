#ifndef SNIGDHAOSBLACKBOX_H
#define SNIGDHAOSBLACKBOX_H

#include <QMainWindow>
#include <QAbstractButton>
#include <QNetworkAccessManager>

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

    SnigdhaOSBlackBox(QWidget* parent = nullptr, QString state = "WELCOME");
    ~SnigdhaOSBlackBox();

private slots:
    void on_textWidget_buttonBox_clicked(QAbstractButton* button);
    void on_selectWidget_buttonBox_clicked(QAbstractButton* button);

private:
    Ui::SnigdhaOSBlackBox *ui;
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
