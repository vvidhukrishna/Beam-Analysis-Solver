import sys

from PyQt5.QtWidgets import QApplication

from gui import BeamAnalysisApp

def main():
    # Initialize the Qt Application
    app = QApplication(sys.argv)

    # Create and display the main window
    window = BeamAnalysisApp()
    window.show()

    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
