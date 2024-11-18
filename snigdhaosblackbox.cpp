#include "snigdhaosblackbox.h"
#include "./ui_snigdhaosblackbox.h"

const char* INTERNET_CHECK_URL = "https://snigdha-os.github.io/"

SnigdhaOSBlackBox::SnigdhaOSBlackBox(QWidget *parent, Qstring state)
    : QMainWindow(parent)
    , ui(new Ui::SnigdhaOSBlackBox)
{
    this->setWindowIcon(QIcon("/usr/share/pixmaps/snigdhaos-blackbox.svg"));
    ui->setupUi(this);
    this->setWindowFlags(this->WindowFlags() & -Qt::WindowCloseButtonHint);
    executable_modify_date = QFileInfo(QCoreApplication::applicationFilePath()).lastModified();
    updateState(state);
}
//destructor for Snigdha OS Blackbox class

SnigdhaOSBlackBox::~SnigdhaOSBlackBox()
{
    delete ui;
}

void SnigdhaOSBlackbox::doInternetUpRequest(){
    QNetworkAccessManager* = network_manager = new QNetworkAccessManager();
    auto network_reply = network_manager->head(QNetworkRequest(QString(INTERNET_CHECK_URL)));

    QTimer* timer = new QTimer(this);
    timer->setSingleShot(true);
    timer->start(5000); //5 sec

    // if the time is out we will try again
    connect(timer, QTimer::timeout, this, [this, timer, network_reply, network_manager](){
        timer->stop();
        timer->deleteLayer();
        network_reply->deleteLater();
        network_manager->deleteLater();

        if (network_reply->error() == network_reply->NoError){
            updateState(state::UPDATE);
        }
        else{
            doInternetUpRequest();
        }
    });
}