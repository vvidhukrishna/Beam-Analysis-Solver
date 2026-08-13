import sys

# Try importing PyQt6 first, fallback to PyQt5 if needed
try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
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