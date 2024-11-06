#ifndef SNIGDHAOSBLACKBOX_H
#define SNIGDHAOSBLACKBOX_H

#include <QMainWindow>

QT_BEGIN_NAMESPACE
namespace Ui {
class SnigdhaOSBlackBox;
}
QT_END_NAMESPACE

class SnigdhaOSBlackBox : public QMainWindow
{
    Q_OBJECT

public:
    SnigdhaOSBlackBox(QWidget *parent = nullptr);
    ~SnigdhaOSBlackBox();

private:
    Ui::SnigdhaOSBlackBox *ui;
};
#endif // SNIGDHAOSBLACKBOX_H
