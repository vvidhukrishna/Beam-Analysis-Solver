from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QGroupBox, QFormLayout, QRadioButton, QComboBox,
    QMessageBox, QFileDialog
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np

from beam import Beam, Support, PointLoad, AppliedMoment, UniformDistributedLoad, UniformVaryingLoad, FIXED, PINNED, \
    ROLLER
from solvers import solve_reactions, calculate_sfd_bmd
from Validation import (
    validate_float_list, validate_support_location, validate_support_order,
    validate_udl_spec, validate_uvl_spec, validate_points
)
from plotting import plot_beam_results
from history import (
    save_analysis_history,
    load_history,
    load_execution,
    plot_history_entry,
    save_graph
)


class BeamAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beam Analysis Tool")
        self.setGeometry(100, 100, 1000, 800)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        input_panel = QVBoxLayout()

        self.type_group = QGroupBox("Beam Type")
        type_layout = QHBoxLayout()
        self.radio_simply = QRadioButton("Simply Supported (2 Supports)")
        self.radio_cantilever = QRadioButton("Cantilever (Fixed at x=0)")
        self.radio_simply.setChecked(True)

        type_layout.addWidget(self.radio_simply)
        type_layout.addWidget(self.radio_cantilever)
        self.type_group.setLayout(type_layout)
        input_panel.addWidget(self.type_group)

        self.radio_simply.toggled.connect(self.toggle_beam_type)
        self.radio_cantilever.toggled.connect(self.toggle_beam_type)

        beam_group = QGroupBox("Beam Parameters")
        beam_layout = QFormLayout()

        self.beam_length_input = QLineEdit("10")
        self.supp_a_input = QLineEdit("0")
        self.supp_b_input = QLineEdit("10")

        beam_layout.addRow("Beam Length (m):", self.beam_length_input)
        self.supp_a_label = QLabel("Support A Location (m):")
        beam_layout.addRow(self.supp_a_label, self.supp_a_input)
        self.supp_b_label = QLabel("Support B Location (m):")
        beam_layout.addRow(self.supp_b_label, self.supp_b_input)

        beam_group.setLayout(beam_layout)
        input_panel.addWidget(beam_group)

        pt_group = QGroupBox("Point Loads & Moments")
        pt_layout = QFormLayout()
        self.pt_loc_input = QLineEdit()
        self.pt_loc_input.setPlaceholderText("e.g., 2, 5, 8")
        self.pt_mag_input = QLineEdit()
        self.pt_mag_input.setPlaceholderText("e.g., -10, -15, 20")

        self.mom_loc_input = QLineEdit()
        self.mom_loc_input.setPlaceholderText("e.g., 4")
        self.mom_mag_input = QLineEdit()
        self.mom_mag_input.setPlaceholderText("e.g., 50")

        pt_layout.addRow("Point Load Locations (m):", self.pt_loc_input)
        pt_layout.addRow("Point Load Magnitudes (kN):", self.pt_mag_input)
        pt_layout.addRow("Moment Locations (m):", self.mom_loc_input)
        pt_layout.addRow("Moment Magnitudes (kNm):", self.mom_mag_input)
        pt_group.setLayout(pt_layout)
        input_panel.addWidget(pt_group)

        dist_group = QGroupBox("Distributed Loads")
        dist_layout = QFormLayout()
        self.udl_input = QLineEdit()
        self.udl_input.setPlaceholderText("start, end, intensity; ...")
        self.uvl_input = QLineEdit()
        self.uvl_input.setPlaceholderText("start, end, w1, w2; ...")
        dist_layout.addRow("UDLs:", self.udl_input)
        dist_layout.addRow("UVLs:", self.uvl_input)
        dist_group.setLayout(dist_layout)
        input_panel.addWidget(dist_group)

        self.calc_btn = QPushButton("Calculate & Plot")
        self.calc_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.calc_btn.clicked.connect(self.calculate)
        input_panel.addWidget(self.calc_btn)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setMaximumHeight(150)
        input_panel.addWidget(self.result_box)

        # History Section
        history_group = QGroupBox("History")
        history_layout = QVBoxLayout()

        self.history_combo = QComboBox()
        history_layout.addWidget(self.history_combo)

        self.btn_load_history = QPushButton("Load Selected Execution")
        self.btn_save_graph = QPushButton("Save Graph")
        history_layout.addWidget(self.btn_load_history)
        history_layout.addWidget(self.btn_save_graph)

        self.btn_load_history.clicked.connect(self.load_selected_history)
        self.btn_save_graph.clicked.connect(self.save_current_graph)

        history_group.setLayout(history_layout)
        input_panel.addWidget(history_group)

        input_panel.addStretch()

        self.figure = plt.figure(figsize=(6, 8))
        self.canvas = FigureCanvas(self.figure)

        main_layout.addLayout(input_panel, 1)
        main_layout.addWidget(self.canvas, 2)

        self.setLayout(main_layout)

        self.refresh_history()

    def toggle_beam_type(self):
        is_simply_supported = self.radio_simply.isChecked()
        self.supp_a_label.setVisible(is_simply_supported)
        self.supp_a_input.setVisible(is_simply_supported)
        self.supp_b_label.setVisible(is_simply_supported)
        self.supp_b_input.setVisible(is_simply_supported)

    def refresh_history(self):
        history = load_history()
        self.history_combo.clear()
        for entry in history:
            execution = entry.get("execution")
            timestamp = entry.get("timestamp")
            self.history_combo.addItem(f"Execution {execution} - {timestamp}", execution)

    def load_selected_history(self):
        execution_number = self.history_combo.currentData()

        if execution_number is None:
            QMessageBox.warning(self, "Warning", "No execution selected.")
            return

        entry = load_execution(execution_number)

        if entry is None:
            QMessageBox.warning(self, "Warning", "Execution not found.")
            return

        try:
            self.result_box.clear()
            plot_history_entry(entry, self.figure)
            self.canvas.draw()

            stats = entry["analysis"]["summary_statistics"]
            self.result_box.append(f"Loaded Execution: {execution_number}")
            self.result_box.append(f"Max Shear Force: {stats['max_shear_force']:.2f} kN")
            self.result_box.append(f"Max Bending Moment: {stats['max_bending_moment']:.2f} kNm")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load historical execution: {str(e)}")

    def save_current_graph(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Graph",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;PDF (*.pdf)"
        )
        if not filename:
            return

        try:
            save_graph(self.figure, filename)
            QMessageBox.information(self, "Success", f"Graph saved to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save graph: {str(e)}")

    def calculate(self):
        try:
            self.result_box.clear()

            length = float(self.beam_length_input.text())
            beam = Beam(length)

            if self.radio_cantilever.isChecked():
                beam.add_event(0.0, Support(FIXED))
            else:
                x_A = validate_support_location(self.supp_a_input.text(), 0.0, length, "Support A")
                x_B = validate_support_location(self.supp_b_input.text(), length, length, "Support B")
                validate_support_order(x_A, x_B)
                beam.add_event(x_A, Support(PINNED))
                beam.add_event(x_B, Support(ROLLER))

            pt_locs = validate_points(self.pt_loc_input.text(), length)
            if pt_locs:
                pt_mags = validate_float_list(self.pt_mag_input.text(), len(pt_locs), "Point Load Magnitudes")
                for loc, mag in zip(pt_locs, pt_mags):
                    beam.add_event(loc, PointLoad(mag))

            mom_locs = validate_points(self.mom_loc_input.text(), length)
            if mom_locs:
                mom_mags = validate_float_list(self.mom_mag_input.text(), len(mom_locs), "Moment Magnitudes")
                for loc, mag in zip(mom_locs, mom_mags):
                    beam.add_event(loc, AppliedMoment(mag))

            udl_text = self.udl_input.text().strip()
            if udl_text:
                for chunk in udl_text.split(";"):
                    if chunk.strip():
                        s, e, i = validate_udl_spec(chunk, length)
                        beam.add_distributed_event(UniformDistributedLoad(s, e, i))

            uvl_text = self.uvl_input.text().strip()
            if uvl_text:
                for chunk in uvl_text.split(";"):
                    if chunk.strip():
                        s, e, w1, w2 = validate_uvl_spec(chunk, length)
                        beam.add_distributed_event(UniformVaryingLoad(s, e, w1, w2))

            reactions = solve_reactions(beam)
            x_vals, v_vals, m_vals = calculate_sfd_bmd(beam)

            if reactions["type"] == "cantilever":
                self.result_box.append(" Analysis Successful (Cantilever Beam)")
                self.result_box.append(f"• Fixed Support at x = {reactions['x_A']} m")
                self.result_box.append(f"  Reaction Force: {reactions['R_A']:.2f} kN")
                self.result_box.append(f"  Reaction Moment: {reactions['M_A']:.2f} kNm")
            else:
                self.result_box.append(" Analysis Successful (Simply Supported)")
                self.result_box.append(f"• Support A (x = {reactions['x_A']} m): {reactions['R_A']:.2f} kN")
                self.result_box.append(f"• Support B (x = {reactions['x_B']} m): {reactions['R_B']:.2f} kN")

            summary_stats = {
                "max_shear_force": float(np.max(v_vals)),
                "min_shear_force": float(np.min(v_vals)),
                "max_bending_moment": float(np.max(m_vals)),
                "min_bending_moment": float(np.min(m_vals))
            }

            plot_beam_results(beam, x_vals, v_vals, m_vals, self.figure, reactions)
            self.canvas.draw()

            save_analysis_history(
                beam=beam,
                system_type=reactions["type"],
                reactions=reactions,
                x_grid=x_vals,
                shear_force=v_vals,
                bending_moment=m_vals,
                summary_statistics=summary_stats
            )

            self.refresh_history()
            self.result_box.append("\nSaved to history.json")

        except Exception as e:
            self.result_box.setText(f"Error: {str(e)}")