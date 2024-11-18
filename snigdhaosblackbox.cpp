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

void SnigdhaOSBlackBox::doInternetUpRequest(){
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

void SnigdhaOSBlackBox::doUpdate(){
    if (qEnvironmentVaribaleSet("SNIGDHAOS_BLACKBOX_SELFUPDATE")) {
        updateState(State::SELECT);
        return;
    }
    auto process = new QProcess(this);
    QTemporaryFile* file = new QTemporaryFile(this);
    file->open();
    file->setAutoRemove(true);
    process->start("/usr/lib/snigdhaos/launch-terminal", QStringList() << QString("sudo pacman -Syyu 2>&1 && rm \"" + file->fileName() + "\"; read -p 'Press Ebter to Exit'"));
    connect(process,QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished), this, [this, process, file](int exitcode, QProcess::ExitStatus status){
        process->deleteLater();
        file->deleteLater();
        
        if (exitcode == 0 && !file->exists()){
            relaunchSelf("POST_UPDATE");
        }
        else{
            relaunchSelf("UPDATE_RETRY");
        }
    });
}

void SnigdhaOSBlackBox::doApply(){
    QStringList packages;
    QStringList setup_commands;
    QStringList prepare_commands;

    auto checkboxList = ui->selectWidget_tabs->findChildren<QcheckBox*>();

    for (auto checkbox : checkboxList){
        if (checkbox->isChecked()){
            packages += checkbox->property("packages").toStringList();
            setup_commands += checkbox->property("setup_commands").toStringList();
            prepare_commands += checkbox->property("prepare_commands").toStringList();
        }
    }

    if (packages.empty()){
        updateState(State::SUCCESS);
        return;
    }

    if (packages.contains("docker")){
        setup_commands += "systemctl enable --now docker.socket";
    }
    if (packages.contains("virt-manager-meta") && packages.contains("gnome-boxes")){
        setup_commands += "systemctl enable --now libvirtd";
    }

    packages.removeDuplicates();

    QTemporaryFile* prepareFile = new QTemporaryFile(this);
    prepareFile->setAutoRemove(true);
    prepareFile->open();
    QTextStream prepareStream(prepareFile);
    prepareStream << prepare_commands.join('\n');
    prepareFile->close();
    QTemporaryFile* packagesFiles = new QTemporaryFile(this);
    
}