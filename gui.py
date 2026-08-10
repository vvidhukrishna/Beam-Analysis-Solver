# gui.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout, QFrame
)
from PyQt5.QtCore import Qt
from Validation import analyze_input_state


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Beam Analysis Tool")
        self.resize(600, 500)

        # Base Application styling (Light grey background)
        self.setStyleSheet("QMainWindow { background-color: #f4f5f7; }")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(10)

        # --- HEADER ---
        title_label = QLabel("BEAM ANALYSIS")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; font-weight: 800; color: #111827; letter-spacing: 1px;")

        subtitle_label = QLabel("Shear Force & Bending Moment Diagram Generator")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 13px; color: #6b7280; margin-bottom: 20px;")

        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)

        # --- MAIN CONTENT CARD ---
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #e5e7eb;
            }
        """)
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(20)

        # Form layout for inputs
        form_layout = QFormLayout()
        form_layout.setSpacing(16)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        # Style for the form labels
        self.setStyleSheet(self.styleSheet() + """
            QLabel { font-size: 13px; font-weight: 600; color: #374151; border: none; background: transparent; }
        """)

        # -- SECTION: BEAM CONFIGURATION --
        config_header = QLabel("BEAM CONFIGURATION")
        config_header.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #9ca3af; letter-spacing: 1px; margin-top: 5px;")
        form_layout.addRow(config_header)

        # Beam Length
        self.input_beam_length = QLineEdit()
        self.input_beam_length.setPlaceholderText("e.g. 6.0")

        beam_length_layout = QHBoxLayout()
        beam_length_layout.addWidget(self.input_beam_length)
        unit_label = QLabel("m")
        unit_label.setStyleSheet("color: #6b7280; font-weight: normal; background: transparent; border: none;")
        beam_length_layout.addWidget(unit_label)
        beam_length_layout.setContentsMargins(0, 0, 0, 0)

        beam_length_container = QWidget()
        beam_length_container.setStyleSheet("background: transparent; border: none;")
        beam_length_container.setLayout(beam_length_layout)
        form_layout.addRow("Beam Length", beam_length_container)

        # Point Locations
        self.input_points = QLineEdit()
        self.input_points.setPlaceholderText("e.g. 0.0, 3.0, 6.0")
        form_layout.addRow("Point Locations", self.input_points)

        # -- SECTION: LOADING CONDITIONS --
        loads_header = QLabel("LOADING CONDITIONS")
        loads_header.setStyleSheet(
            "font-size: 11px; font-weight: bold; color: #9ca3af; letter-spacing: 1px; margin-top: 15px;")
        form_layout.addRow(loads_header)

        # Point Loads
        self.input_point_loads = QLineEdit()
        self.input_point_loads.setPlaceholderText("e.g. 0.0, -20.0, 0.0")
        form_layout.addRow("Point Loads", self.input_point_loads)

        # Applied Moments
        self.input_applied_moments = QLineEdit()
        self.input_applied_moments.setPlaceholderText("e.g. 0.0, 10.0, 0.0")
        form_layout.addRow("Applied Moments", self.input_applied_moments)

        # UDLs
        self.input_udls = QLineEdit()
        self.input_udls.setPlaceholderText("start, end, intensity (e.g. 1.0, 4.0, -10.0)")
        form_layout.addRow("UDLs", self.input_udls)

        # UVLs
        self.input_uvls = QLineEdit()
        self.input_uvls.setPlaceholderText("start, end, w1, w2 (e.g. 2, 5, 0, -15)")
        form_layout.addRow("UVLs", self.input_uvls)

        card_layout.addLayout(form_layout)
        main_layout.addWidget(card_frame)

        main_layout.addStretch()

        # --- BUTTON ---
        btn_layout = QHBoxLayout()
        self.analyze_button = QPushButton("ANALYZE")
        self.analyze_button.setEnabled(False)  # Disabled by default
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background-color: #2b5797;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 14px 60px;
                border: none;
                border-radius: 7px;
                letter-spacing: 1px;
            }
            QPushButton:hover { background-color: #1f477f; }
            QPushButton:pressed { background-color: #183762; }
            QPushButton:disabled {
                background-color: #e5e7eb;
                color: #9ca3af;
            }
        """)

        btn_layout.addStretch()
        btn_layout.addWidget(self.analyze_button)
        btn_layout.addStretch()

        main_layout.addLayout(btn_layout)

        # Setup initial states and connections
        self.setup_inputs()

    def setup_inputs(self):
        """Applies base styles and connects textChanged signals."""
        self.inputs = [
            (self.input_beam_length, "float"),
            (self.input_points, "float_list"),
            (self.input_point_loads, "float_list"),
            (self.input_applied_moments, "float_list"),
            (self.input_udls, "udl_list"),
            (self.input_uvls, "uvl_list")
        ]

        for widget, expected_type in self.inputs:
            self.set_input_state(widget, "neutral")
            # Connect using a lambda to pass the specific widget and its type
            widget.textChanged.connect(lambda text, w=widget, t=expected_type: self.validate_field(w, t))

    def set_input_state(self, widget, state):
        """Applies stylesheet based on the validation state."""
        base_style = """
            QLineEdit {
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 13px;
                color: #111827;
        """

        if state == "valid":
            widget.setStyleSheet(base_style + """
                border: 2px solid #3fa36c;
                background-color: #f8fffa;
            }""")
        elif state == "invalid":
            widget.setStyleSheet(base_style + """
                border: 2px solid #d9534f;
                background-color: #fff8f8;
            }""")
        else:  # neutral / empty / incomplete
            widget.setStyleSheet(base_style + """
                border: 1px solid #d0d5dd;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2b5797;
                background-color: white;
            }""")

    def validate_field(self, widget, expected_type):
        """Validates a single field and triggers a global form check."""
        text = widget.text()
        state = analyze_input_state(text, expected_type)

        if state in ["empty", "incomplete"]:
            self.set_input_state(widget, "neutral")
        else:
            self.set_input_state(widget, state)

        self.check_overall_form_validity()

    def check_overall_form_validity(self):
        """Enables the Analyze button ONLY if required fields are valid and no fields are invalid."""
        all_valid = True

        for widget, expected_type in self.inputs:
            state = analyze_input_state(widget.text(), expected_type)

            # Beam length and points are strictly REQUIRED.
            if widget in [self.input_beam_length, self.input_points]:
                if state != "valid":
                    all_valid = False
            # Loads are OPTIONAL (can be empty), but if filled, they must not be invalid/incomplete
            else:
                if state in ["invalid", "incomplete"]:
                    all_valid = False

        self.analyze_button.setEnabled(all_valid)


def main():
    app = QApplication(sys.argv)
    # Set global application font
    font = app.font()
    font.setFamily("Segoe UI")  # Works well for modern UI on Windows/Linux
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()