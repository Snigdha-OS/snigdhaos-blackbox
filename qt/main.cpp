#include "snigdhaosblackbox.h" // Include the header file for the SnigdhaOSBlackbox class, which defines the core functionality of the application.

#include <QApplication> // Include the QApplication class, which manages application-wide resources and event handling.

int main(int argc, char *argv[]) // Entry point of the application. It accepts command-line arguments.
{
    // Create a QApplication object to manage the application's GUI event loop and initialize resources.
    QApplication a(argc, argv);

    // Check if any additional command-line arguments are passed.
    // If more than one argument exists, the second argument (index 1) is passed to the SnigdhaOSBlackbox constructor as a string.
    // Otherwise, an empty string is passed.
    SnigdhaOSBlackbox w(nullptr, a.arguments().length() > 1 ? a.arguments()[1] : "");

    // Show the main window of the SnigdhaOSBlackbox application.
    w.show();

    // Enter the event loop, which waits for and processes user interaction events.
    return a.exec();
}
