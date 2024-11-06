#include "snigdhaosblackbox.h"
#include "./ui_snigdhaosblackbox.h"

SnigdhaOSBlackBox::SnigdhaOSBlackBox(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::SnigdhaOSBlackBox)
{
    ui->setupUi(this);
}

SnigdhaOSBlackBox::~SnigdhaOSBlackBox()
{
    delete ui;
}
