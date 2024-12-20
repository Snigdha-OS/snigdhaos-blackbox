#ifndef SNIGDHAOSBLACKBOX_H // Start of include guard to prevent multiple inclusions of this header file.
#define SNIGDHAOSBLACKBOX_H // Define the include guard macro.

#include <QMainWindow> // Base class for the main window of a Qt application, providing menus, toolbars, etc.
#include <QAbstractButton> // Abstract base class for button widgets such as QPushButton, QCheckBox, etc.
#include <QtNetwork/QNetworkAccessManager> // Used for sending and managing network requests and responses.

QT_BEGIN_NAMESPACE // Marks the start of Qt's namespace, for compatibility with C++ namespaces.
namespace Ui {
class SnigdhaOSBlackbox; // Forward declaration of the `Ui::SnigdhaOSBlackbox` class, generated from the .ui file.
}
QT_END_NAMESPACE // Marks the end of the Qt namespace.

class SnigdhaOSBlackbox : public QMainWindow // Inherits from QMainWindow to represent the application's main window.
{
    Q_OBJECT // Qt's macro enabling signals, slots, and other meta-object features.

public:
    // Enumeration for managing the application's various states.
    enum class State {
        QUIT,           // Exit the application.
        WELCOME,        // Display the welcome screen.
        INTERNET,       // Check internet connectivity.
        UPDATE,         // Perform updates.
        UPDATE_RETRY,   // Retry updating if the previous attempt failed.
        SELECT,         // Allow the user to select options or tools.
        APPLY,          // Apply the selected options or configurations.
        APPLY_RETRY,    // Retry applying changes if the first attempt fails.
        SUCCESS         // Indicate successful completion of operations.
    };

    // Constructor for the SnigdhaOSBlackbox class.
    // Parameters:
    // - parent: Pointer to the parent widget. Defaults to nullptr, meaning no parent.
    // - state: The initial state of the application, defaulting to "WELCOME".
    SnigdhaOSBlackbox(QWidget *parent = nullptr, QString state = "WELCOME");

    // Destructor to clean up resources.
    ~SnigdhaOSBlackbox();

private slots: // Qt slots, which respond to signals (e.g., button clicks).
    // Slot to handle button clicks in the text widget.
    void on_textWidget_buttonBox_clicked(QAbstractButton* button);

    // Slot to handle button clicks in the select widget.
    void on_selectWidget_buttonBox_Clicked(QAbstractButton* button);

private:
    Ui::SnigdhaOSBlackbox *ui; // Pointer to the UI object generated from the .ui file.

    QDateTime executable_modify_date; // Stores the modification date of the application executable, possibly for update checks.

    State currentState; // Keeps track of the current state of the application.

    // Private member functions for internal operations:
    void doInternetUpRequest(); // Checks for internet connectivity.
    void doUpdate(); // Handles the update process.
    void doApply(); // Applies the selected configuration or changes.

    // Populates the selection widget with options.
    void populateSelectWidget();
    
    // Overloaded version to populate the widget with specific files and labels.
    void populateSelectWidget(QString filename, QString label);

    // Updates the application state using the `State` enum.
    void updateState(State state);
    
    // Overloaded version to update the application state using a QString.
    void updateState(QString state);

    // Relaunches the application, possibly with additional parameters.
    void relaunchSelf(QString param);
};

#endif // SNIGDHAOSBLACKBOX_H // End of the include guard.
