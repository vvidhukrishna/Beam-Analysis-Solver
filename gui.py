import numpy as np
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeySequence, QIcon
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton, QComboBox,
    QDoubleSpinBox, QFormLayout, QFrame, QScrollArea, QSplitter, QSizePolicy, QToolBar, QAction, QMessageBox, QFileDialog, QTextEdit)

from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT)
from matplotlib.figure import Figure
from beam import (Beam, Support, PointLoad, AppliedMoment, UniformDistributedLoad,
    UniformVaryingLoad, FIXED, PINNED, ROLLER)

from solvers import solve_reactions, calculate_sfd_bmd
from Validation import (validate_support_location, validate_support_order,
    validate_udl_spec, validate_uvl_spec, validate_points)

from plotting import plot_beam_results
from history import (save_analysis_history, load_history, load_execution,
    plot_history_entry, save_graph)

from ui.styles import build_stylesheet, PALETTE, MONO_FAMILY
from ui.widgets import card, LoadTable
from ui.dialogs import HistoryDialog, AboutDialog
from ui import icons


class BeamAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beam Analysis Tool")
        self.resize(1280, 800)
        self.setMinimumSize(1040, 660)
        self.setStyleSheet(build_stylesheet())
        self.setWindowIcon(QIcon("logo.png"))
        self._build_toolbar()

        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self._build_model_panel())

        workspace_splitter = QSplitter(Qt.Vertical)
        workspace_splitter.addWidget(self._build_viewport())
        workspace_splitter.addWidget(self._build_results_card())
        workspace_splitter.setStretchFactor(0, 4)
        workspace_splitter.setStretchFactor(1, 1)
        workspace_splitter.setSizes([580, 180])
        workspace_splitter.setCollapsible(0, False)

        main_splitter.addWidget(workspace_splitter)
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setSizes([360, 920])
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)

        central_layout.addWidget(main_splitter)
        self.setCentralWidget(central)

        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        units_label = QLabel("SI UNITS")
        units_label.setObjectName("statusUnits")
        self.status_bar.addPermanentWidget(units_label)

        self.toggle_beam_type()
        self.result_box.setHtml(self._render_placeholder_html())
        self.refresh_history()

    # Header / toolbar
    def _build_toolbar(self):
        toolbar = QToolBar("Main")
        toolbar.setObjectName("mainToolBar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)

        title_box = QWidget()
        title_layout = QVBoxLayout(title_box)
        title_layout.setContentsMargins(6, 2, 18, 2)
        title_layout.setSpacing(0)
        title_lbl = QLabel("BEAM ANALYSIS SOLVER")
        title_lbl.setObjectName("appTitle")
        subtitle_lbl = QLabel("STATIC ANALYSIS  \u00b7  SFD / BMD")
        subtitle_lbl.setObjectName("appSubtitle")
        title_layout.addWidget(title_lbl)
        title_layout.addWidget(subtitle_lbl)
        toolbar.addWidget(title_box)
        toolbar.addSeparator()

        new_action = QAction(icons.icon("new", PALETTE["text_secondary"]), "New", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.setToolTip("Clear the current model (Ctrl+N)")
        new_action.triggered.connect(self.new_model)
        toolbar.addAction(new_action)

        run_action = QAction(icons.icon("run", PALETTE["accent"]), "Run Analysis", self)
        run_action.setShortcut(QKeySequence("Ctrl+R"))
        run_action.setToolTip("Solve reactions, shear force and bending moment (Ctrl+R)")
        run_action.triggered.connect(self.calculate)
        toolbar.addAction(run_action)
        run_button = toolbar.widgetForAction(run_action)
        if run_button is not None:
            run_button.setObjectName("runAction")
            run_button.setCursor(Qt.PointingHandCursor)

        toolbar.addSeparator()

        history_action = QAction(icons.icon("history", PALETTE["text_secondary"]), "History", self)
        history_action.setShortcut(QKeySequence("Ctrl+H"))
        history_action.setToolTip("Browse saved analyses (Ctrl+H)")
        history_action.triggered.connect(self.open_history_dialog)
        toolbar.addAction(history_action)

        export_action = QAction(icons.icon("export", PALETTE["text_secondary"]), "Export", self)
        export_action.setShortcut(QKeySequence("Ctrl+S"))
        export_action.setToolTip("Save the current plots as PNG, JPEG or PDF (Ctrl+S)")
        export_action.triggered.connect(self.save_current_graph)
        toolbar.addAction(export_action)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        help_action = QAction(icons.icon("help", PALETTE["text_secondary"]), "Help", self)
        help_action.setToolTip("About Beam Analysis Solver")
        help_action.triggered.connect(self.open_about_dialog)
        toolbar.addAction(help_action)

        return toolbar

    # Left: model / loading panel
    def _build_model_panel(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(320)
        scroll.setMaximumWidth(460)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(14, 14, 14, 16)
        layout.setSpacing(12)

        layout.addWidget(self._build_beam_type_card())
        layout.addWidget(self._build_beam_parameters_card())
        layout.addWidget(self._build_point_loads_card())
        layout.addWidget(self._build_moments_card())
        layout.addWidget(self._build_distributed_loads_card())

        self.calc_btn = QPushButton("Run Analysis")
        self.calc_btn.setObjectName("primaryButton")
        self.calc_btn.setCursor(Qt.PointingHandCursor)
        self.calc_btn.setToolTip("Solve reactions, shear force and bending moment (Ctrl+R).")
        self.calc_btn.clicked.connect(self.calculate)
        layout.addWidget(self.calc_btn)

        layout.addWidget(self._build_history_card())

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    def _build_beam_type_card(self):
        frame, content = card("Beam Type")

        segmented = QFrame()
        segmented.setObjectName("segmentedControl")
        seg_layout = QHBoxLayout(segmented)
        seg_layout.setContentsMargins(3, 3, 3, 3)
        seg_layout.setSpacing(2)

        self.radio_simply = QRadioButton("Simply Supported")
        self.radio_simply.setObjectName("segmentOption")
        self.radio_simply.setCursor(Qt.PointingHandCursor)
        self.radio_simply.setToolTip("Beam resting on two supports (pinned + roller).")

        self.radio_cantilever = QRadioButton("Cantilever")
        self.radio_cantilever.setObjectName("segmentOption")
        self.radio_cantilever.setCursor(Qt.PointingHandCursor)
        self.radio_cantilever.setToolTip("Beam rigidly fixed at x = 0.")

        self.radio_simply.setChecked(True)

        seg_layout.addWidget(self.radio_simply, 1)
        seg_layout.addWidget(self.radio_cantilever, 1)
        content.addWidget(segmented)

        self.radio_simply.toggled.connect(self.toggle_beam_type)
        self.radio_cantilever.toggled.connect(self.toggle_beam_type)
        return frame

    def _build_beam_parameters_card(self):
        frame, content = card("Beam Parameters")

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft)

        self.beam_length_input = QDoubleSpinBox()
        self.beam_length_input.setDecimals(2)
        self.beam_length_input.setRange(0.10, 100000.0)
        self.beam_length_input.setSingleStep(0.5)
        self.beam_length_input.setSuffix(" m")
        self.beam_length_input.setValue(10.0)
        self.beam_length_input.setAlignment(Qt.AlignRight)
        self.beam_length_input.setToolTip("Overall span of the beam.")
        form.addRow("Length", self.beam_length_input)
        self.beam_length_input.valueChanged.connect(self._on_length_changed)

        self.supp_a_label = QLabel("Support A")
        self.supp_a_input = QDoubleSpinBox()
        self.supp_a_input.setDecimals(2)
        self.supp_a_input.setRange(0.0, 100000.0)
        self.supp_a_input.setSingleStep(0.5)
        self.supp_a_input.setSuffix(" m")
        self.supp_a_input.setValue(0.0)
        self.supp_a_input.setAlignment(Qt.AlignRight)
        self.supp_a_input.setToolTip("Location of Support A, measured from x = 0.")
        form.addRow(self.supp_a_label, self.supp_a_input)

        self.supp_b_label = QLabel("Support B")
        self.supp_b_input = QDoubleSpinBox()
        self.supp_b_input.setDecimals(2)
        self.supp_b_input.setRange(0.0, 100000.0)
        self.supp_b_input.setSingleStep(0.5)
        self.supp_b_input.setSuffix(" m")
        self.supp_b_input.setValue(10.0)
        self.supp_b_input.setAlignment(Qt.AlignRight)
        self.supp_b_input.setToolTip("Location of Support B, measured from x = 0.")
        form.addRow(self.supp_b_label, self.supp_b_input)

        content.addLayout(form)

        self.fixed_support_hint = QLabel("Fixed support at x = 0.00 m")
        self.fixed_support_hint.setProperty("role", "hint")
        self.fixed_support_hint.setVisible(False)
        content.addWidget(self.fixed_support_hint)
        return frame

    def _build_point_loads_card(self):
        frame, content = card("Point Loads")
        self.point_loads_table = LoadTable(
            columns=[
                {"label": "Location", "unit": "m", "decimals": 2, "minimum": 0.0,
                 "maximum": 100000.0, "default": 0.0, "step": 0.5},
                {"label": "Magnitude", "unit": "kN", "decimals": 2, "minimum": -1_000_000.0,
                 "maximum": 1_000_000.0, "default": -10.0, "step": 1.0},],
            add_label="+ Add Point Load",
            empty_text="No point loads defined.",)
        content.addWidget(self.point_loads_table)
        return frame

    def _build_moments_card(self):
        frame, content = card("Applied Moments")
        self.moments_table = LoadTable(
            columns=[
                {"label": "Location", "unit": "m", "decimals": 2, "minimum": 0.0,
                 "maximum": 100000.0, "default": 0.0, "step": 0.5},
                {"label": "Moment", "unit": "kNm", "decimals": 2, "minimum": -1_000_000.0,
                 "maximum": 1_000_000.0, "default": 10.0, "step": 1.0},],
            add_label="+ Add Moment",
            empty_text="No applied moments defined.",)
        content.addWidget(self.moments_table)
        return frame

    def _build_distributed_loads_card(self):
        frame, content = card("Distributed Loads")

        udl_label = QLabel("UNIFORM (UDL)")
        udl_label.setProperty("role", "hint")
        content.addWidget(udl_label)
        self.udl_table = LoadTable(
            columns=[
                {"label": "Start", "unit": "m", "decimals": 2, "minimum": 0.0,
                 "maximum": 100000.0, "default": 0.0, "step": 0.5},
                {"label": "End", "unit": "m", "decimals": 2, "minimum": 0.0,
                 "maximum": 100000.0, "default": 1.0, "step": 0.5},
                {"label": "Intensity", "unit": "kN/m", "decimals": 2, "minimum": -1_000_000.0,
                 "maximum": 1_000_000.0, "default": -5.0, "step": 0.5},],
            add_label="+ Add UDL",
            empty_text="No uniform distributed loads defined.",)
        content.addWidget(self.udl_table)

        uvl_label = QLabel("VARYING (UVL)")
        uvl_label.setProperty("role", "hint")
        content.addWidget(uvl_label)
        self.uvl_table = LoadTable(
            columns=[
                {"label": "Start", "unit": "m", "decimals": 2, "minimum": 0.0,
                 "maximum": 100000.0, "default": 0.0, "step": 0.5},
                {"label": "End", "unit": "m", "decimals": 2, "minimum": 0.0,
                 "maximum": 100000.0, "default": 1.0, "step": 0.5},
                {"label": "Start Intensity", "unit": "kN/m", "decimals": 2, "minimum": -1_000_000.0,
                 "maximum": 1_000_000.0, "default": 0.0, "step": 0.5},
                {"label": "End Intensity", "unit": "kN/m", "decimals": 2, "minimum": -1_000_000.0,
                 "maximum": 1_000_000.0, "default": -5.0, "step": 0.5},],
            add_label="+ Add UVL",
            empty_text="No uniformly varying loads defined.",)
        content.addWidget(self.uvl_table)
        return frame

    def _build_history_card(self):
        frame, content = card("Recent Executions")

        self.history_combo = QComboBox()
        self.history_combo.setToolTip("Quick-select a previously saved execution.")
        content.addWidget(self.history_combo)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.btn_load_history = QPushButton("Load")
        self.btn_load_history.setObjectName("ghostButton")
        self.btn_load_history.setCursor(Qt.PointingHandCursor)
        self.btn_load_history.setToolTip("Reload the selected execution's plots and summary.")
        self.btn_load_history.clicked.connect(self.load_selected_history)
        btn_row.addWidget(self.btn_load_history)

        view_all_btn = QPushButton("View All\u2026")
        view_all_btn.setObjectName("ghostButton")
        view_all_btn.setCursor(Qt.PointingHandCursor)
        view_all_btn.clicked.connect(self.open_history_dialog)
        btn_row.addWidget(view_all_btn)
        content.addLayout(btn_row)
        return frame

    # Right: engineering viewport + results
    def _build_viewport(self):
        container = QWidget()
        v_layout = QVBoxLayout(container)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("viewportHeader")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(12, 2, 6, 2)
        title = QLabel("ENGINEERING VIEW")
        title.setObjectName("viewportTitle")
        h_layout.addWidget(title)
        h_layout.addStretch()

        # self-contained; plotting.py still owns everything drawn on it.
        self.figure = Figure(figsize=(8, 10))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumSize(800, 1000)

        self.plot_toolbar = NavigationToolbar2QT(self.canvas, container)
        self.plot_toolbar.setObjectName("plotToolBar")
        self.plot_toolbar.setIconSize(QSize(15, 15))
        h_layout.addWidget(self.plot_toolbar)

        v_layout.addWidget(header)

        canvas_scroll = QScrollArea()
        canvas_scroll.setObjectName("plotScrollArea")
        canvas_scroll.setWidgetResizable(False)
        canvas_scroll.setFrameShape(QFrame.NoFrame)

        canvas_host = QWidget()
        canvas_host.setObjectName("plotCanvasHost")
        canvas_layout = QVBoxLayout(canvas_host)
        canvas_layout.setContentsMargins(2, 2, 2, 2)
        canvas_layout.addWidget(self.canvas)

        canvas_scroll.setWidget(canvas_host)
        v_layout.addWidget(canvas_scroll, 1)
        return container

    def _build_results_card(self):
        frame, content = card("Analysis Results")
        self.result_box = QTextEdit()
        self.result_box.setObjectName("resultsPanel")
        self.result_box.setReadOnly(True)
        self.result_box.setMinimumHeight(110)
        content.addWidget(self.result_box)
        return frame

    # Behavior
    def toggle_beam_type(self):
        is_simply_supported = self.radio_simply.isChecked()
        self.supp_a_label.setVisible(is_simply_supported)
        self.supp_a_input.setVisible(is_simply_supported)
        self.supp_b_label.setVisible(is_simply_supported)
        self.supp_b_input.setVisible(is_simply_supported)
        self.fixed_support_hint.setVisible(not is_simply_supported)

    def _on_length_changed(self, value):
        # Keep support locations from silently exceeding the beam span.
        self.supp_a_input.setMaximum(value)
        self.supp_b_input.setMaximum(value)

    def new_model(self):
        """Reset the model to a blank slate. Purely additive and does not touch history.json."""
        self.radio_simply.setChecked(True)
        self.beam_length_input.setValue(10.0)
        self.supp_a_input.setValue(0.0)
        self.supp_b_input.setValue(10.0)
        self.point_loads_table.clear_rows()
        self.moments_table.clear_rows()
        self.udl_table.clear_rows()
        self.uvl_table.clear_rows()
        self.figure.clear()
        self.canvas.draw()
        self.result_box.setHtml(self._render_placeholder_html())
        self.status_bar.showMessage("Ready", 3000)

    def calculate(self):
        try:
            length = self.beam_length_input.value()
            beam = Beam(length)

            if self.radio_cantilever.isChecked():
                beam.add_event(0.0, Support(FIXED))
            else:
                x_a = validate_support_location(str(self.supp_a_input.value()), 0.0, length, "Support A")
                x_b = validate_support_location(str(self.supp_b_input.value()), length, length, "Support B")
                validate_support_order(x_a, x_b)
                beam.add_event(x_a, Support(PINNED))
                beam.add_event(x_b, Support(ROLLER))

            for loc, mag in self.point_loads_table.get_rows():
                validate_points(str(loc), length)
                beam.add_event(loc, PointLoad(mag))

            for loc, mag in self.moments_table.get_rows():
                validate_points(str(loc), length)
                beam.add_event(loc, AppliedMoment(mag))

            for s, e, intensity in self.udl_table.get_rows():
                s2, e2, i2 = validate_udl_spec(f"{s}, {e}, {intensity}", length)
                beam.add_distributed_event(UniformDistributedLoad(s2, e2, i2))

            for s, e, w1, w2 in self.uvl_table.get_rows():
                s2, e2, w1_2, w2_2 = validate_uvl_spec(f"{s}, {e}, {w1}, {w2}", length)
                beam.add_distributed_event(UniformVaryingLoad(s2, e2, w1_2, w2_2))

            reactions = solve_reactions(beam)
            x_vals, v_vals, m_vals = calculate_sfd_bmd(beam)

            summary_stats = {
                "max_shear_force": float(np.max(v_vals)),
                "min_shear_force": float(np.min(v_vals)),
                "max_bending_moment": float(np.max(m_vals)),
                "min_bending_moment": float(np.min(m_vals)),}

            plot_beam_results(beam, x_vals, v_vals, m_vals, self.figure, reactions)
            self.canvas.draw()

            save_analysis_history(
                beam=beam,
                system_type=reactions["type"],
                reactions=reactions,
                x_grid=x_vals,
                shear_force=v_vals,
                bending_moment=m_vals,
                summary_statistics=summary_stats)

            self.refresh_history()
            self.result_box.setHtml(self._render_results_html(reactions, x_vals, v_vals, m_vals))
            self.status_bar.showMessage("Analysis complete", 5000)

        except Exception as e:
            self.result_box.setHtml(self._render_error_html(str(e)))
            self.status_bar.showMessage("Input error", 5000)

    def refresh_history(self):
        history = load_history()
        self.history_combo.clear()
        for entry in history:
            execution = entry.get("execution")
            timestamp = entry.get("timestamp")
            self.history_combo.addItem(f"Execution {execution} \u2014 {timestamp}", execution)

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
            plot_history_entry(entry, self.figure)
            self.canvas.draw()

            stats = entry["analysis"]["summary_statistics"]
            self.result_box.setHtml(self._render_history_summary_html(execution_number, stats))
            self.status_bar.showMessage(f"Loaded execution {execution_number}", 4000)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load historical execution: {str(e)}")

    def open_history_dialog(self):
        history = load_history()
        dialog = HistoryDialog(history, self._load_execution_from_dialog, parent=self)
        dialog.exec_()

    def _load_execution_from_dialog(self, execution_number):
        index = self.history_combo.findData(execution_number)
        if index == -1:
            self.refresh_history()
            index = self.history_combo.findData(execution_number)
        if index != -1:
            self.history_combo.setCurrentIndex(index)
            self.load_selected_history()

    def open_about_dialog(self):
        AboutDialog(self).exec_()

    def save_current_graph(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Graph", "", "PNG Image (*.png);;JPEG Image (*.jpg);;PDF (*.pdf)")
        if not filename:
            return

        try:
            save_graph(self.figure, filename)
            QMessageBox.information(self, "Success", f"Graph saved to {filename}")
            self.status_bar.showMessage("Graph exported", 4000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save graph: {str(e)}")
            self.status_bar.showMessage("Export failed", 4000)

    # Results panel rendering (presentation only -- no engineering logic)
    def _render_placeholder_html(self):
        p = PALETTE
        return f"""
        <div style="color:{p['text_tertiary']}; font-family:{MONO_FAMILY};">
        Define a beam model on the left and choose
        <span style="color:{p['text_secondary']};">Run Analysis</span>
        to compute reactions, shear force and bending moment.
        </div>
        """

    def _render_results_html(self, reactions, x_vals, v_vals, m_vals):
        p = PALETTE
        max_v = float(np.max(v_vals))
        min_v = float(np.min(v_vals))
        max_m = float(np.max(m_vals))
        min_m = float(np.min(m_vals))
        x_max_v = float(x_vals[int(np.argmax(v_vals))])
        x_min_v = float(x_vals[int(np.argmin(v_vals))])
        x_max_m = float(x_vals[int(np.argmax(m_vals))])
        x_min_m = float(x_vals[int(np.argmin(m_vals))])

        if reactions["type"] == "cantilever":
            system_label = "Cantilever"
            reactions_rows = (
                f'<tr><td style="color:{p["text_secondary"]};padding:2px 10px 2px 0;">'
                f'Fixed Support (x = {reactions["x_A"]:.2f} m)</td>'
                f'<td align="right" style="color:{p["text_primary"]};padding:2px 0;">'
                f'{reactions["R_A"]:.2f} kN</td></tr>'
                f'<tr><td style="color:{p["text_secondary"]};padding:2px 10px 2px 0;">'
                f'Reaction Moment</td>'
                f'<td align="right" style="color:{p["text_primary"]};padding:2px 0;">'
                f'{reactions["M_A"]:.2f} kNm</td></tr>')
        else:
            system_label = "Simply Supported"
            reactions_rows = (
                f'<tr><td style="color:{p["text_secondary"]};padding:2px 10px 2px 0;">'
                f'Support A (x = {reactions["x_A"]:.2f} m)</td>'
                f'<td align="right" style="color:{p["text_primary"]};padding:2px 0;">'
                f'{reactions["R_A"]:.2f} kN</td></tr>'
                f'<tr><td style="color:{p["text_secondary"]};padding:2px 10px 2px 0;">'
                f'Support B (x = {reactions["x_B"]:.2f} m)</td>'
                f'<td align="right" style="color:{p["text_primary"]};padding:2px 0;">'
                f'{reactions["R_B"]:.2f} kN</td></tr>')

        return f"""
        <div style="color:{p['text_primary']}; font-family:{MONO_FAMILY};">
          <div style="color:{p['success']}; font-weight:600; margin-bottom:8px;">
            Analysis Successful &mdash; {system_label} System
          </div>
          <div style="color:{p['text_tertiary']}; font-size:8pt; letter-spacing:1px;">REACTIONS</div>
          <table width="100%" cellspacing="0" cellpadding="0" style="margin-top:2px;">{reactions_rows}</table>
          <div style="color:{p['text_tertiary']}; font-size:8pt; letter-spacing:1px; margin-top:10px;">EXTREMA</div>
          <table width="100%" cellspacing="0" cellpadding="0" style="margin-top:2px;">
            <tr><td style="color:{p['text_secondary']};padding:2px 10px 2px 0;">Maximum Shear Force</td>
                <td align="right" style="color:{p['text_primary']};padding:2px 0;">
                {max_v:.2f} kN @ {x_max_v:.2f} m</td></tr>
            <tr><td style="color:{p['text_secondary']};padding:2px 10px 2px 0;">Minimum Shear Force</td>
                <td align="right" style="color:{p['text_primary']};padding:2px 0;">
                {min_v:.2f} kN @ {x_min_v:.2f} m</td></tr>
            <tr><td style="color:{p['text_secondary']};padding:2px 10px 2px 0;">Maximum Bending Moment</td>
                <td align="right" style="color:{p['text_primary']};padding:2px 0;">
                {max_m:.2f} kNm @ {x_max_m:.2f} m</td></tr>
            <tr><td style="color:{p['text_secondary']};padding:2px 10px 2px 0;">Minimum Bending Moment</td>
                <td align="right" style="color:{p['text_primary']};padding:2px 0;">
                {min_m:.2f} kNm @ {x_min_m:.2f} m</td></tr>
          </table>
          <div style="color:{p['text_tertiary']}; font-size:8pt; margin-top:10px;">Saved to history.json</div>
        </div>
        """

    def _render_error_html(self, message):
        p = PALETTE
        return f"""
        <div style="color:{p['text_primary']}; font-family:{MONO_FAMILY};">
          <div style="color:{p['error']}; font-weight:600; margin-bottom:6px;">
            Error &mdash; Invalid Input
          </div>
          <div style="color:{p['text_secondary']};">{message}</div>
        </div>
        """

    def _render_history_summary_html(self, execution_number, stats):
        p = PALETTE
        return f"""
        <div style="color:{p['text_primary']}; font-family:{MONO_FAMILY};">
          <div style="color:{p['accent']}; font-weight:600; margin-bottom:6px;">
            Loaded Execution: {execution_number}
          </div>
          <div style="color:{p['text_secondary']};">Max Shear Force:
            <span style="color:{p['text_primary']};">{stats['max_shear_force']:.2f} kN</span>
          </div>
          <div style="color:{p['text_secondary']};">Max Bending Moment:
            <span style="color:{p['text_primary']};">{stats['max_bending_moment']:.2f} kNm</span>
          </div>
        </div>
        """