#include "snigdhaosblackbox.h"
// #include "./ui_snigdhaosblackbox.h"

#include <QApplication>

// const char* INTERNET_CHECK_URL = "https://snigdhaos.org/";

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    SnigdhaOSBlackBox w;
    w.show();
    return a.exec();
}
