import sys
import numpy as np

try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTextEdit, QScrollArea, QGroupBox,
        QFormLayout, QMessageBox
    )
    from PyQt6.QtCore import Qt
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
except ImportError:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTextEdit, QScrollArea, QGroupBox,
        QFormLayout, QMessageBox
    )
    from PyQt5.QtCore import Qt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.figure import Figure
from get_beam_data import build_beam_from_gui_data
from solvers import solve_reactions, calculate_sfd_bmd
from plotting import plot_beam_results
from Validation import (
    validate_points, validate_float_list, validate_udl_spec,
    validate_uvl_spec, validate_support_location, validate_support_separation
)


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=7, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)


class BeamAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beam Analysis & SFD/BMD Tool")
        self.resize(1280, 800)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # ------------------- LEFT PANEL (INPUTS & RESULTS) -------------------
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)

        # Scroll area for inputs
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Inputs Group
        input_group = QGroupBox("Beam Parameters & Loading")
        form_layout = QFormLayout(input_group)

        self.input_points = QLineEdit("0.0, 2.5, 5.0, 8.0")
        self.input_loads = QLineEdit("0.0, -15.0, 0.0, 0.0")
        self.input_moments = QLineEdit("0.0, 0.0, 0.0, 0.0")
        self.input_udls = QLineEdit("0.0, 2.5, -10.0")
        self.input_uvls = QLineEdit("5.0, 8.0, 0.0, -20.0")
        self.input_sup_a = QLineEdit("0.0")
        self.input_sup_b = QLineEdit("8.0")

        form_layout.addRow(QLabel("Points x (m):"), self.input_points)
        form_layout.addRow(QLabel("Point Loads (kN):"), self.input_loads)
        form_layout.addRow(QLabel("Applied Moments (kNm):"), self.input_moments)
        form_layout.addRow(QLabel("UDLs (start, end, intensity; ...):"), self.input_udls)
        form_layout.addRow(QLabel("UVLs (start, end, w1, w2; ...):"), self.input_uvls)
        form_layout.addRow(QLabel("Support A x (m):"), self.input_sup_a)
        form_layout.addRow(QLabel("Support B x (m):"), self.input_sup_b)

        scroll_layout.addWidget(input_group)

        # Solve Button
        self.btn_calculate = QPushButton("Calculate & Plot")
        self.btn_calculate.setStyleSheet("font-weight: bold; padding: 8px;")
        self.btn_calculate.clicked.connect(self.run_analysis)
        scroll_layout.addWidget(self.btn_calculate)

        # Results Display Box
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout(results_group)
        self.results_box = QTextEdit()
        self.results_box.setReadOnly(True)
        results_layout.addWidget(self.results_box)

        scroll_layout.addWidget(results_group)
        scroll_area.setWidget(scroll_content)

        left_layout.addWidget(scroll_area)
        left_container.setMaximumWidth(420)
        main_layout.addWidget(left_container)

        # ------------------- RIGHT PANEL (CANVAS) -------------------
        self.canvas_frame = QWidget()
        canvas_layout = QVBoxLayout(self.canvas_frame)
        self.canvas = MplCanvas(self.canvas_frame)
        canvas_layout.addWidget(self.canvas)

        main_layout.addWidget(self.canvas_frame, stretch=1)

        # Run initial calculation on load
        self.run_analysis()

    def parse_udl_text(self, text: str, beam_length: float) -> list[tuple[float, float, float]]:
        text = text.strip()
        if not text:
            return []
        udls = []
        for spec in text.split(";"):
            if spec.strip():
                udls.append(validate_udl_spec(spec, beam_length))
        return udls

    def parse_uvl_text(self, text: str, beam_length: float) -> list[tuple[float, float, float, float]]:
        text = text.strip()
        if not text:
            return []
        uvls = []
        for spec in text.split(";"):
            if spec.strip():
                uvls.append(validate_uvl_spec(spec, beam_length))
        return uvls

    def run_analysis(self):
        try:
            points = validate_points(self.input_points.text())
            num_pts = len(points)
            beam_length = max(points)

            point_loads = validate_float_list(self.input_loads.text(), num_pts, "Point loads")
            moments = validate_float_list(self.input_moments.text(), num_pts, "Applied moments")

            udls = self.parse_udl_text(self.input_udls.text(), beam_length)
            uvls = self.parse_uvl_text(self.input_uvls.text(), beam_length)

            x_A = validate_support_location(self.input_sup_a.text(), points[0], beam_length, "Support A")
            x_B = validate_support_location(self.input_sup_b.text(), points[-1], beam_length, "Support B")
            validate_support_separation(x_A, x_B)

            # Build Beam
            beam = build_beam_from_gui_data(points, point_loads, moments, udls, uvls, x_A, x_B)

            # Solve Reactions
            x_A, R_A, x_B, R_B = solve_reactions(beam)

            # Calculate SFD and BMD
            x_grid, V_grid, M_grid = calculate_sfd_bmd(beam)

            # Summary Statistics
            max_v_idx = np.argmax(np.abs(V_grid))
            max_m_idx = np.argmax(np.abs(M_grid))

            res_text = (
                "=== SUPPORT REACTIONS ===\n"
                f"Support A (x = {x_A:.2f} m): R_A = {R_A:.2f} kN\n"
                f"Support B (x = {x_B:.2f} m): R_B = {R_B:.2f} kN\n\n"
                "=== EXTREMA ===\n"
                f"Max |Shear Force|    : {abs(V_grid[max_v_idx]):.2f} kN (at x = {x_grid[max_v_idx]:.2f} m)\n"
                f"Max |Bending Moment| : {abs(M_grid[max_m_idx]):.2f} kNm (at x = {x_grid[max_m_idx]:.2f} m)\n"
            )
            self.results_box.setText(res_text)

            # Plot onto embedded Qt Canvas
            plot_beam_results(self.canvas.fig, beam, x_grid, V_grid, M_grid)

        except Exception as e:
            QMessageBox.critical(self, "Input / Calculation Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BeamAnalysisApp()
    window.show()
    sys.exit(app.exec())