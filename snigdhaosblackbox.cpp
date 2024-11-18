#include "snigdhaosblackbox.h"
#include "./ui_snigdhaosblackbox.h"

const char* INTERNET_CHECK_URL = "https://snigdha-os.github.io/"

SnigdhaOSBlackBox::SnigdhaOSBlackBox(QWidget *parent, Qstring state)
    : QMainWindow(parent)
    , ui(new Ui::SnigdhaOSBlackBox)
{
    this->setWindowIcon(QIcon("/usr/share/pixmaps/snigdhaos-blackbox.svg"));
    ui->setupUi(this);
    this->setWindowFlags(this->WindowFlags() & -Qt::WindowCloseButtonHint)
}

SnigdhaOSBlackBox::~SnigdhaOSBlackBox()
{
    delete ui;
}
