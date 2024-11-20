#include "snigdhaosblackbox.h"
#include "./ui_snigdhaosblackbox.h"
#include <QCheckBox>
#include <QDebug>
#include <QFileInfo>
#include <QProcess>
#include <QScrollArea>
#include <QTemporaryFile>
#include <QTimer>
#include <QNetworkReply>
#include <unistd.h>

const char* INTERNET_CHECK_URL = "https://snigdha-os.github.io/";

SnigdhaOSBlackBox::SnigdhaOSBlackBox(QWidget *parent, QString state)
    : QMainWindow(parent)
    , ui(new Ui::SnigdhaOSBlackBox)
{
    this->setWindowIcon(QIcon("/usr/share/pixmaps/snigdhaos-blackbox.svg"));
    ui->setupUi(this);
    this->setWindowFlags(this->windowFlags() & -Qt::WindowCloseButtonHint);
    executable_modify_date = QFileInfo(QCoreApplication::applicationFilePath()).lastModified();
    updateState(state);
}
//destructor for Snigdha OS Blackbox class

SnigdhaOSBlackBox::~SnigdhaOSBlackBox()
{
    delete ui;
}

void SnigdhaOSBlackBox::doInternetUpRequest(){
    QNetworkAccessManager* network_manager = new QNetworkAccessManager();
    auto network_reply = network_manager->head(QNetworkRequest(QString(INTERNET_CHECK_URL)));

    QTimer* timer = new QTimer(this);
    timer->setSingleShot(true);
    timer->start(5000); //5 sec

    // if the time is out we will try again
    connect(timer, &QTimer::timeout, this, [this, timer, network_reply, network_manager](){
        timer->stop();
        timer->deleteLater();
        network_reply->deleteLater();
        network_manager->deleteLater();

        if (network_reply->error() == network_reply->NoError){
            updateState(State::UPDATE);
        }
        else{
            doInternetUpRequest();
        }
    });
}

void SnigdhaOSBlackBox::doUpdate(){
    if (qEnvironmentVariableIsSet("SNIGDHAOS_BLACKBOX_SELFUPDATE")) {
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

    auto checkboxList = ui->selectWidget_tabs->findChildren<QCheckBox*>();

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
    packagesFiles->setAutoRemove(true);
    packagesFiles->open();
    QTextStream packagesStream(packagesFiles);
    packagesStream << packages.join(' ');
    packagesFiles->close();
    QTemporaryFile* setupFile = new QTemporaryFile(this);
    setupFile->setAutoRemove(true);
    setupFile->open();
    QTextStream setupStream(setupFile);
    setupStream <<setup_commands.join('\n');
    setupFile->close();

    auto process = new QProcess(this);
    process->start("/usr/lib/snigdhaos/launch-terminal", QStringList() << QString("/usr/lib/snigdhaos/-blackbox/apply.sh \"") + prepareFile->fileName() + "\" \"" + packagesFiles->fileName() + "\" \"" + setupFile->fileName() + "\"");
    connect(process,QOverload<int,QProcess::ExitStatus>::of(&QProcess::finished), this, [this, process, prepareFile, packagesFiles, setupFile](int exitcode, QProcess::ExitStatus status) {
        process->deleteLater();
        prepareFile->deleteLater();
        packagesFiles->deleteLater();
        setupFile->deleteLater();

        if (exitcode == 0 && !packagesFiles->exists()){
            updateState(State::SELECT);
        }
        else{
            updateState(State::APPLY_RETRY);
        }
    });
}

void SnigdhaOSBlackBox::populateSelectWidget() {
    if (ui->selectWidget_tabs->count() > 1){
        return;
    }

    auto desktop = qEnvironmentVariable("XDG_SESSION_DESKTOP");
    // I will go for gnome only!
    ui->checkBox_GNOME->setVisible(desktop == "gnome");

    bool isDesktop = false;
    auto chassis = QFile("/sys/class/dmi/id/chassis_type");
    if (chassis.open(QFile::ReadOnly)) {
        QStringList list = {"3", "4", "6", "7", "23", "24"};
        QTextStream in(&chassis);
        isDesktop = list.contains(in.readLine());
    }
    ui->checkBox_Performance->setVisible(isDesktop);

    populateSelectWidget("/usr/lib/snigdhaos-blackbox/eshan.txt", "Eshan");
}

void SnigdhaOSBlackBox::populateSelectWidget(QString filename, QString label){
    QFile file(filename);
    if (file.open(QIODevice::ReadOnly)){
        QScrollArea* scroll = new QScrollArea(ui->selectWidget_tabs);
        QWidget* tab = new QWidget(scroll);
        QVBoxLayout* layout = new QVBoxLayout(tab);
        QTextStream in(&file);
        while(!in.atEnd()) {
            QString def = in.readLine();
            QString packages = in.readLine();
            QString display = in.readLine();
            auto checkbox = new QCheckBox(tab);
            checkbox->setChecked(def == "true");
            checkbox->setText(display);
            checkbox->setProperty("packages", packages.split(" "));
            layout->addWidget(checkbox);
        }

        scroll->setWidget(tab);
        ui->selectWidget_tabs->addTab(scroll, label);
        file.close();
    }
}

void SnigdhaOSBlackBox::updateState(State state){
    if (currentState != state){
        currentState = state;
        this->show();
        this->activateWindow();
        this->raise();

        switch(state){
            case State::WELCOME:
                ui->mainStackedWidget->setCurrentWidget(ui->textWidget);
                ui->textStackedWidget->setCurrentWidget(ui->textWidget_welcome);
                ui->textWidget_buttonBox->setStandardButtons(QDialogButtonBox::Ok | QDialogButtonBox::Cancel);
                break;
            case State::INTERNET:
                ui->mainStackedWidget->setCurrentWidget(ui->waitingWidget);
                ui->waitingWidget_text->setText("Waiting For Internet Connection...");
                doInternetUpRequest();
                break;
            case State::UPDATE:
                ui->mainStackedWidget->setCurrentWidget(ui->waitingWidget);
                ui->waitingWidget_text->setText("Waiting For Update To Finish...");
                doUpdate();
                break;
            case State::UPDATE_RETRY:
                ui->mainStackedWidget->setCurrentWidget(ui->textWidget);
                ui->textStackedWidget->setCurrentWidget(ui->textWidget_updateRetry);
                ui->textWidget_buttonBox->setStandardButtons(QDialogButtonBox::Yes | QDialogButtonBox::No);
                break;
            case State::QUIT:
                ui->mainStackedWidget->setCurrentWidget(ui->textWidget);
                ui->textStackedWidget->setCurrentWidget(ui->textWidget_quit);
                ui->textWidget_buttonBox->setStandardButtons(QDialogButtonBox::Ok | QDialogButtonBox::Reset);
                break;
            case State::SELECT:
                ui->mainStackedWidget->setCurrentWidget(ui->selectWidget);
                populateSelectWidget();
                break;
            case State::APPLY:
                ui->mainStackedWidget->setCurrentWidget(ui->waitingWidget);
                ui->waitingWidget_text->setText("Applying...");
                doApply();
                break;
            case State::APPLY_RETRY:
                ui->mainStackedWidget->setCurrentWidget(ui->textWidget);
                ui->textStackedWidget->setCurrentWidget(ui->textWidget_applyRetry);
                ui->textWidget_buttonBox->setStandardButtons(QDialogButtonBox::Yes | QDialogButtonBox::No);
                break;
            case State::SUCCESS:
                ui->mainStackedWidget->setCurrentWidget(ui->textWidget);
                ui->textStackedWidget->setCurrentWidget(ui->textWidget_success);
                ui->textWidget_buttonBox->setStandardButtons(QDialogButtonBox::Ok);
                break;
        }
    }
}

void SnigdhaOSBlackBox::updateState(QString state) {
    if (state == "POST_UPDATE"){
        updateState(State::SELECT);
    }
    else if (state == "UPDATE_RETRY"){
        updateState(State::UPDATE_RETRY);
    }
    else{
        updateState(State::WELCOME);
    }
}

void SnigdhaOSBlackBox::relaunchSelf(QString param) {
    auto binary = QFileInfo(QCoreApplication::applicationFilePath());
    if (executable_modify_date != binary.lastModified()) {
        execlp(binary.absolutePath().toUtf8().constData(), binary.fileName().toUtf8().constData(), param.toUtf8().constData(), NULL);
        exit(0);
    }
    else {
        updateState(param);
    }
}

void SnigdhaOSBlackBox::on_textWidget_buttonBox_clicked(QAbstractButton* button) {
    switch(currentState) {
        case State::WELCOME:
            if (ui->textWidget_buttonBox->standardButton(button) == QDialogButtonBox::Ok) {
                updateState(State::INTERNET);
            }
            break;
        case State::UPDATE_RETRY:
            if (ui->textWidget_buttonBox->standardButton(button) == QDialogButtonBox::Yes) {
                updateState(State::INTERNET);
            }
            break;
        case State::APPLY_RETRY:
            if (ui->textWidget_buttonBox->standardButton(button) == QDialogButtonBox::Ok) {
                updateState(State::APPLY);
            }
            else if (ui->textWidget_buttonBox->standardButton(button) == QDialogButtonBox::Reset) {
                updateState(State::SELECT);
            }
            break;
        case State::SUCCESS:
            if (ui->textWidget_buttonBox->standardButton(button) == QDialogButtonBox::Ok) {
                QApplication::quit();
            }
            break;
        case State::QUIT:
            if (ui->textWidget_buttonBox->standardButton(button) == QDialogButtonBox::No || ui->textWidget_buttonBox->standardButton(button) == QDialogButtonBox::Ok) {
                QApplication::quit();
            }
            else {
                updateState(State::WELCOME);
            }
        default:;
    }
    if (ui->textWidget_buttonBox->standardButton(button) == QDialogButtonBox::No || ui->textWidget_buttonBox->standardButton(button) == QDialogButtonBox::Cancel) {
        updateState(State::QUIT);
    }
}

void SnigdhaOSBlackBox::on_selectWidget_buttonBox_clicked(QAbstractButton* button) {
    if (ui->textWidget_buttonBox->standardButton(button) == QDialogButtonBox::Ok) {
        updateState(State::APPLY);
    }
    else {
        updateState(State::QUIT);
    }
}
