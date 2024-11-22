#include "snigdhaosblackbox.h"

#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    SnigdhaOSBlackbox w(nullptr, a.arguments().length() > 1 ? a.arguments()[1] : "");
    w.show();
    return a.exec();
}
