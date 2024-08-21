import pyqtgraph as pg

from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QPushButton,
    QGridLayout,
    QMainWindow,
    QComboBox,
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QTimer, Qt
from simulation_variables import (
    SimulationVariables,
    line_1_y,
    line_2_y,
)

WHITE = "#FFFFFF"
CREAM = "#FFFDD0"
GOLD = "#FFD700"
LIGHTRED = "#FFCCCB"
LIGHTGREEN = "#90EE90"
LIGHTBLUE = "#ADD8E6"
ROYALBLUE = "#4169E1"
simVars = SimulationVariables()
SIMULATION_END = 50000

disorders = [
    "None",
    "Von Willebrand Disease",
    "Haemophilia A (Moderate)",
    "Haemophilia A (Severe)",
    "Haemophilia B",
    "Haemophilia C",
    "Hypocalcaemia (Moderate)",
    "Hypocalcaemia (Severe)",
    "Vitamin K Deficiency",
    "Liver Disorder",
    "Factor V Leiden",
]

speeds = ["x 1", "x 2", "x 4", "x 8", "x 16", "x 32", "x 64", "x 0.5"]

boldFont = QFont()
boldFont.setBold(True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.time_limit = True
        self.line1_name = "cross_linked_fibrin"
        self.line2_name = "thrombin"
        self.time_list_1 = []
        self.time_list_2 = []
        self.timer.timeout.connect(self.time_passes)

        self.setStyleSheet(f"background-color: {CREAM};")
        self.setWindowIcon(QIcon("icon.jpg"))
        self.setWindowTitle("Coagulation Simulator")
        self.layout = QGridLayout()

        column_widths = ((0, 15), (1, 3), (2, 15), (3, 3), (4, 50), (5, 10))
        for i in column_widths:
            self.layout.setColumnStretch(i[0], i[1])

        self.setup_ui_components()

        self.main_window = QWidget()
        self.main_window.setLayout(self.layout)
        self.setCentralWidget(self.main_window)
        self.update_ui_components()
        self.showMaximized()

    def setup_ui_components(self):
        self.intrinsic_row = 1
        self.extrinsic_row = self.intrinsic_row + 11
        self.common_pathway_row = self.extrinsic_row + 5

        actions_row = 9
        disease_row = actions_row + 3

        self.simulationModeLabel = self.create_widget(
            actions_row,
            5,
            text="Simulation Mode",
            alignment="LEFT",
            widget_type="LABEL",
        )
        self.simulationModeCombo = self.create_widget(
            actions_row + 1,
            5,
            options=(
                "None",
                "Haemostasis (Pro-thrombotic)",
                "Haemostasis (Anti-thrombotic)",
                "Fibrinolysis",
            ),
            widget_type="COMBOBOX",
        )
        self.simulationModeCombo.setCurrentText("None")
        self.simulationModeCombo.currentTextChanged.connect(self.preset_changed)

        self.create_widget(
            disease_row, 5, text="Disorder", alignment="LEFT", widget_type="LABEL"
        )

        self.disorderBox = self.create_widget(
            disease_row + 1, 5, options=sorted(disorders), widget_type="COMBOBOX"
        )
        self.disorderBox.currentTextChanged.connect(self.disorder_changed)
        self.disorderBox.setSizeAdjustPolicy(
            self.disorderBox.AdjustToMinimumContentsLengthWithIcon
        )
        self.line1Combo = self.create_widget(
            disease_row + 4,
            5,
            widget_type="COMBOBOX",
            options=sorted(simVars.__dict__),
            colour=LIGHTRED,
        )
        self.line2Combo = self.create_widget(
            disease_row + 7,
            5,
            widget_type="COMBOBOX",
            options=sorted(simVars.__dict__),
            colour=LIGHTBLUE,
        )
        self.line1Combo.currentTextChanged.connect(self.change_line1_variable)
        self.line2Combo.currentTextChanged.connect(self.change_line2_variable)
        self.line1ComboLabel = self.create_widget(
            disease_row + 3,
            5,
            text="Red Line Variable",
            widget_type="LABEL",
            alignment="LEFT",
        )
        self.line2ComboLabel = self.create_widget(
            disease_row + 6,
            5,
            text="Blue Line Variable",
            widget_type="LABEL",
            alignment="LEFT",
        )
        self.setup_time_functionality()
        self.setup_primary_haem()
        self.setup_secondary_haem()
        self.setup_anticoagulation()
        self.setup_fibrinolysis()
        self.set_up_plot()
        self.disorderBox.setCurrentText("None")
        self.line1Combo.setCurrentText(self.line1_name)
        self.line2Combo.setCurrentText(self.line2_name)

    def change_line1_variable(self, text):
        self.line1_name = text
        self.line1.setData(name=text)
        self.change_line_variable(1)
        self.legend.removeItem(self.line1)
        self.legend.removeItem(self.line2)
        self.legend.addItem(self.line1, text)
        self.legend.addItem(self.line2, self.line2_name)

    def change_line2_variable(self, text):
        self.line2_name = text
        self.line2.setData(name=text)
        self.change_line_variable(2)
        self.legend.removeItem(self.line2)
        self.legend.addItem(self.line2, text)

    def change_line_variable(self, line: int):
        match line:
            case 1:
                line_1_y.clear()
                self.time_list_1.clear()
            case 2:
                line_2_y.clear()
                self.time_list_2.clear()
        self.update_lines()

    def setup_time_functionality(self):
        simulation_button_names = (
            "Start/Continue Simulation",
            "Pause Simulation",
            "Next Step",
            "Stop and Reset Simulation",
            "Time Limit ON",
        )

        (
            self.startTimerButton,
            self.stopTimerButton,
            self.oneTimeStep,
            self.resetButton,
            self.timeLimitButton,
        ) = (
            self.create_widget(
                i,
                5,
                text=simulation_button_names[i],
                colour=ROYALBLUE,
                widget_type="BUTTON",
            )
            for i in range(5)
        )

        self.startTimerButton.clicked.connect(self.start_timer)
        self.stopTimerButton.clicked.connect(self.stop_timer)
        self.oneTimeStep.clicked.connect(self.time_passes)
        self.resetButton.clicked.connect(self.reset_simulation)
        self.timeLimitButton.clicked.connect(self.toggle_time_limit)

        self.pickSpeedLabel = self.create_widget(
            5, 5, text="Speed:", widget_type="LABEL"
        )
        self.speedChoiceBox = self.create_widget(
            6, 5, options=speeds, widget_type="COMBOBOX"
        )
        self.speedChoiceBox.currentIndexChanged.connect(self.new_speed)
        self.speedChoiceBox.setCurrentText("x 64")
        self.currentTimeLabel = self.create_widget(7, 5, widget_type="LABEL")

    def setup_fibrinolysis(self):
        self.fibrinolysisLabel = self.create_widget(
            22, 0, widget_type="LABEL", text="Fibrinolysis"
        )
        self.set_bold(self.fibrinolysisLabel)
        fibrinolysis_texts = (
            "Plasminogen",
            "Plasmin",
            "Fibrin Degradation Products (e.g. D-Dimer)",
            "t-PA",
            "Plasmin Activator Inhibitor 1",
            "Alpha 2 Antiplasmin",
            "TAFI",
            "TAFIa",
        )
        (
            self.plasminogenLabel,
            self.plasminLabel,
            self.fDPLabel,
            self.tPALabel,
            self.pAI1Label,
            self.a2ALabel,
            self.tAFILabel,
            self.tAFIaLabel,
        ) = (
            self.create_widget(
                23 + i, 0, widget_type="LABEL", text=fibrinolysis_texts[i]
            )
            for i in range(8)
        )

        (
            self.plasminogenLabel2,
            self.plasminLabel2,
            self.fDPLabel2,
            self.tPALabel2,
            self.pAI1Label2,
            self.a2ALabel2,
            self.tAFILabel2,
            self.tAFIaLabel2,
        ) = (self.create_widget(23 + i, 1, widget_type="LABEL") for i in range(8))

    def setup_anticoagulation(self):
        self.anticoagLabel = self.create_widget(
            14, 0, widget_type="LABEL", text="Antithrombotic Pathway"
        )
        self.set_bold(self.anticoagLabel)
        anticoagulation_texts = (
            "Protein C (XIV)",
            "Activated Protein C (XIVa)",
            "TFPI",
            "Antithrombin III",
            "Thrombomodulin",
            "Protein S",
            "C1 Esterase Inhibitor",
        )

        (
            self.proteinCLabel,
            self.proteinCaLabel,
            self.tFPILabel,
            self.antithrombin3Label,
            self.thrombomodulinLabel,
            self.proteinSLabel,
            self.c1EsteraseInhibitorLabel,
        ) = (
            self.create_widget(
                15 + i, 0, widget_type="LABEL", text=anticoagulation_texts[i]
            )
            for i in range(7)
        )

        (
            self.proteinCLabel2,
            self.proteinCaLabel2,
            self.tFPILabel2,
            self.antithrombin3Label2,
            self.thrombomodulinLabel2,
            self.proteinSLabel2,
            self.c1EsteraseInhibitorLabel2,
        ) = (self.create_widget(15 + i, 1, widget_type="LABEL") for i in range(7))

    def setup_primary_haem(self):
        self.primaryHaemLabel = self.create_widget(
            0, 0, text="Primary Haemostasis", widget_type="LABEL"
        )
        self.aULabel1 = self.create_widget(
            0, 1, text="Amount \n(AU)", widget_type="LABEL"
        )
        self.set_bold(self.primaryHaemLabel)
        (
            self.vWFLabel,
            self.plateletsLabel,
            self.activatedPlateletsLabel,
            self.glycoprotein1bLabel,
            self.glycoprotein2b3aLabel,
            self.endothelinLabel,
            self.nitricOxideLabel,
            self.prostacyclinLabel,
            self.alphaGranulesLabel,
            self.denseGranulesLabel,
            self.serotoninLabel,
            self.aDPLabel,
            self.calciumIonsLabel,
        ) = (self.create_widget(i, 0, widget_type="LABEL") for i in range(1, 14))

        self.vWFLabel.setText("\tVon Willebrand Factor")
        self.plateletsLabel.setText("\tInactive Platelets")
        self.activatedPlateletsLabel.setText("\tActivated Platelets")
        self.glycoprotein1bLabel.setText("\tGlycoprotein Ib")
        self.glycoprotein2b3aLabel.setText("\tGlycoprotein IIb/IIIa")
        self.endothelinLabel.setText("\tEndothelin")
        self.nitricOxideLabel.setText("\tNitric Oxide")
        self.prostacyclinLabel.setText("\tProstacyclin")
        self.alphaGranulesLabel.setText("\tAlpha Granules")
        self.denseGranulesLabel.setText("\tDense Granules")
        self.serotoninLabel.setText("\tSerotonin")
        self.aDPLabel.setText("\tADP")
        self.calciumIonsLabel.setText("\tCalcium 2+ Ions")

        (
            self.vWFLabel2,
            self.plateletsLabel2,
            self.activatedPlateletsLabel2,
            self.glycoprotein1bLabel2,
            self.glycoprotein2b3aLabel2,
            self.endothelinLabel2,
            self.nitricOxideLabel2,
            self.prostacyclinLabel2,
            self.alphaGranulesLabel2,
            self.denseGranulesLabel2,
            self.serotoninLabel2,
            self.aDPLabel2,
            self.calciumIonsLabel2,
        ) = (
            self.create_widget(i, 1, "", alignment="RIGHT", widget_type="LABEL")
            for i in range(1, 14)
        )

    def setup_secondary_haem(self):
        self.secondaryHaemLabel = self.create_widget(
            0, 2, text="Secondary Haemostasis", widget_type="LABEL"
        )
        self.aULabel2 = self.create_widget(
            0, 3, text="Amount\n (AU)", widget_type="LABEL"
        )
        self.set_bold(self.secondaryHaemLabel)
        common_pathway_names = (
            "Common Pathway",
            "Factor X",
            "Factor Xa",
            "Factor V",
            "Factor Va",
            "Prothrombin (II)",
            "Thrombin (IIa)",
            "Fibrinogen (I)",
            "Fibrin (Ia)",
            "Factor XIII",
            "Factor XIIIa",
            "Cross Linked Fibrin",
        )

        (
            self.commonPathwayLabel2,
            self.factor10Label2,
            self.factor10aLabel2,
            self.factor5Label2,
            self.factor5aLabel2,
            self.prothrombinLabel2,
            self.thrombinLabel2,
            self.fibrinogenLabel2,
            self.fibrinLabel2,
            self.factor13Label2,
            self.factor13aLabel2,
            self.crossLinkedFibrinLabel2,
        ) = (
            self.create_widget(
                self.common_pathway_row + i,
                2,
                text=common_pathway_names[i],
                widget_type="LABEL",
            )
            for i in range(12)
        )

        self.set_bold(self.commonPathwayLabel2)

        (
            self.factor10Label,
            self.factor10aLabel,
            self.factor5Label,
            self.factor5aLabel,
            self.prothrombinLabel,
            self.thrombinLabel,
            self.fibrinogenLabel,
            self.fibrinLabel,
            self.factor13Label,
            self.factor13aLabel,
            self.crossLinkedFibrinLabel,
        ) = (
            self.create_widget(
                self.common_pathway_row + i, 3, widget_type="LABEL", alignment="RIGHT"
            )
            for i in range(1, 12)
        )

        intrinsic_names = (
            "Intrinsic Pathway",
            "Activated Partial \nThromboplastin Time (APTT)",
            "Kallikrein & HMWK",
            "Factor XII",
            "Factor XIIa",
            "Factor XI",
            "Factor XIa",
            "Factor IX",
            "Factor IXa",
            "Factor VIII",
            "Factor VIIIa",
        )

        (
            self.intrinsicPathwayLabel2,
            self.aPTTLabel2,
            self.exposedSubendotheliumLabel2,
            self.factor12Label2,
            self.factor12aLabel2,
            self.factor11Label2,
            self.factor11aLabel2,
            self.factor9Label2,
            self.factor9aLabel2,
            self.factor8Label2,
            self.factor8aLabel2,
        ) = (
            self.create_widget(
                self.intrinsic_row + i,
                2,
                widget_type="LABEL",
                alignment="RIGHT",
                text=intrinsic_names[i],
            )
            for i in range(0, 11)
        )

        (
            self.aPTTLabel,
            self.exposedSubendotheliumLabel,
            self.factor12Label,
            self.factor12aLabel,
            self.factor11Label,
            self.factor11aLabel,
            self.factor9Label,
            self.factor9aLabel,
            self.factor8Label,
            self.factor8aLabel,
        ) = (
            self.create_widget(
                self.intrinsic_row + i, 3, widget_type="LABEL", alignment="RIGHT"
            )
            for i in range(1, 11)
        )

        self.intrinsicPathwayLabel2.setText("Intrinsic Pathway")
        self.set_bold(self.intrinsicPathwayLabel2)

        extrinsic_names = (
            "Extrinsic Pathway",
            "International Normalized Ratio (INR)",
            "Tissue Factor (III)",
            "Factor VII",
            "Factor VIIa",
        )

        (
            self.extrinsicPathwayLabel2,
            self.iNRLabel2,
            self.factor3Label2,
            self.factor7Label2,
            self.factor7aLabel2,
        ) = (
            self.create_widget(
                self.extrinsic_row + i,
                2,
                widget_type="LABEL",
                text=extrinsic_names[i],
                alignment="RIGHT",
            )
            for i in range(5)
        )

        (
            self.iNRLabel,
            self.tissueFactorLabel,
            self.factor7Label,
            self.factor7aLabel,
        ) = (
            self.create_widget(
                self.extrinsic_row + i, 3, widget_type="LABEL", alignment="RIGHT"
            )
            for i in range(1, 5)
        )

        self.extrinsicPathwayLabel2.setText("Extrinsic Pathway")
        self.iNRLabel2.setText("International Normalized Ratio (INR)")
        self.set_bold(self.extrinsicPathwayLabel2)

    def set_up_plot(self):
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget, 8, 4, 21, 1)
        self.plot_widget.setTitle("Compound Levels over Time", color=(0, 0, 0))
        self.plot_widget.setBackground("w")
        self.legend = self.plot_widget.addLegend()
        self.plot_widget.setYRange(0, 50000)
        self.plot_widget.setXRange(0, 1000)
        self.plot_widget.setLabel("bottom", "Time (seconds)")
        self.plot_widget.setLabel("left", "Amount (AU)")
        self.plot_widget.showGrid(x=True, y=True)
        self.pen = pg.mkPen(color=(255, 0, 0))
        time_list = [i / 2 for i in range(len(line_1_y))]
        self.line1 = self.plot_widget.plot(
            time_list,
            line_1_y,
            pen=pg.mkPen(color=(255, 0, 0), width=3),
            name=self.line1_name,
        )
        self.line2 = self.plot_widget.plot(
            pen=pg.mkPen(color=(0, 0, 255), width=3), name=self.line2_name
        )

    def update_lines(self):
        # time_list = [i / 2 for i in range(len(line_1_y))]
        self.line1.setData(self.time_list_1, line_1_y)
        self.line2.setData(self.time_list_2, line_2_y)

    def time_passes(self):
        simVars.time_passes()
        self.update_lines()

        self.time_list_1.append(simVars.current_time / 2)
        self.time_list_2.append(simVars.current_time / 2)
        line_1_y.append(simVars.__dict__[self.line1_name])
        line_2_y.append(simVars.__dict__[self.line2_name])
        if self.time_limit and simVars.current_time // 2 > 1000:
            self.stop_timer()
            print(simVars.calcium_ions)
        self.update_ui_components()

    def create_widget(
        self,
        row,
        column,
        text="",
        colour="",
        action=None,
        alignment="RIGHT",
        widget_type="",
        options=None,
    ):
        match widget_type:
            case "LABEL":
                widget = QLabel()
            case "BUTTON":
                widget = QPushButton()
            case "COMBOBOX":
                widget = QComboBox()
            case _:
                raise Exception(f"widget type '{widget_type}' not valid")
        self.layout.addWidget(widget, row, column)
        if widget_type in {"LABEL", "BUTTON"}:
            widget.setText(text)
        self.set_colour(widget, colour)
        if widget_type == "BUTTON" and action is not None:
            widget.clicked.connect(action)
        match alignment:
            case "RIGHT":
                alignment = Qt.AlignRight
            case "CENTRE":
                alignment = Qt.AlignCenter
            case "LEFT":
                alignment = Qt.AlignLeft
        if widget_type in {"LABEL"}:
            widget.setAlignment(alignment)
        if widget_type == "COMBOBOX":
            widget.addItems(options)
        return widget

    def set_colour(self, widget, colour):
        widget.setStyleSheet(f"background-color : {colour}")

    def set_bold(self, widget):
        widget.setFont(boldFont)

    def preset_changed(self, text):
        match text:
            case "None":
                pass
            case "Haemostasis (Pro-thrombotic)":
                self.injury_occurs(prothrombotic=True)
            case "Haemostasis (Anti-thrombotic)":
                self.injury_occurs(prothrombotic=False)
            case "Fibrinolysis":
                self.fibrinolysis_occurs()

    def injury_occurs(self, prothrombotic: bool):
        simVars.tissue_factor = 100
        simVars.subendothelium = 100
        simVars.plasminogen = 10000
        simVars.a2A = 100
        simVars.injury_stage = 0
        if not prothrombotic:
            simVars.thrombomodulin = 100
            simVars.protein_s = 1000
            simVars.tFPI = 100
            simVars.antithrombin3 = 10000
            simVars.c1_esterase_inhibitor = 10000
        self.update_ui_components()

    def increase_fibrinogen_level(self):
        simVars.fibrinogen += 1000
        self.update_ui_components()

    def fibrinolysis_occurs(self):
        simVars.current_time = 0
        simVars.plasminogen = 10000
        simVars.tPA = 100
        simVars.pAI1 = 0
        simVars.fibrinogen = 0
        simVars.cross_linked_fibrin = SIMULATION_END
        self.clear_lines()
        self.update_ui_components()

    def clear_lines(self):
        line_1_y.clear()
        line_2_y.clear()
        self.time_list_1.clear()
        self.time_list_2.clear()
        self.update_lines()

    def start_timer(self):
        self.new_speed(self.speedChoiceBox.currentIndex())
        timer_speed = int(500 // simVars.speed)
        self.timer.start(timer_speed)
        self.startTimerButton.setDisabled(True)
        self.speedChoiceBox.setDisabled(True)
        self.set_colour(self.startTimerButton, WHITE)

    def stop_timer(self):
        self.timer.stop()
        self.startTimerButton.setDisabled(False)
        self.speedChoiceBox.setDisabled(False)
        self.set_colour(self.startTimerButton, ROYALBLUE)

    def reset_simulation(self):
        simVars.reset()
        self.clear_lines()
        self.update_lines()
        self.stop_timer()
        self.simulationModeCombo.setCurrentText("None")
        self.speedChoiceBox.setCurrentText("x 64")
        self.disorderBox.setCurrentText("None")
        self.update_ui_components()

    def toggle_time_limit(self):
        self.time_limit = not self.time_limit
        self.set_colour(
            self.timeLimitButton, ROYALBLUE if self.time_limit else LIGHTGREEN
        )
        self.update_ui_components()

    def new_speed(self, index):
        speed_dictionary = {
            0: 1,
            1: 2,
            2: 4,
            3: 8,
            4: 16,
            5: 32,
            6: 64,
            7: 0.5,
        }
        simVars.speed = speed_dictionary[index]

    def disorder_changed(self, text):
        match text.upper():
            case "LIVER DISORDER":
                simVars.prothrombin = 100
                simVars.factor7 = 10
                simVars.factor9 = 10
                simVars.factor10 = 10
                simVars.platelets = 100
            case "HAEMOPHILIA C":
                simVars.factor11 = 0
            case "HAEMOPHILIA B":
                simVars.factor9 = 0
            case "HAEMOPHILIA A (MODERATE)":
                simVars.factor8 = 500
            case "HAEMOPHILIA A (SEVERE)":
                simVars.factor8 = 0
            case "HYPOCALCAEMIA (MODERATE)":
                simVars.calcium_ions = 1.1
            case "HYPOCALCAEMIA (SEVERE)":
                simVars.calcium_ions = 0.9
            case _:
                pass

        self.update_ui_components()

    def update_ui_components(self):
        updating_labels = (
            (self.vWFLabel2, simVars.vWF),
            (self.plateletsLabel2, simVars.platelets),
            (self.activatedPlateletsLabel2, simVars.activated_platelets),
            (self.glycoprotein1bLabel2, simVars.glyc1b),
            (self.glycoprotein2b3aLabel2, simVars.glyc2b3a),
            (self.prostacyclinLabel2, simVars.prostacyclin),
            (self.endothelinLabel2, simVars.endothelin),
            (self.nitricOxideLabel2, simVars.nitric_oxide),
            (self.alphaGranulesLabel2, simVars.alpha_granules),
            (self.denseGranulesLabel2, simVars.dense_granules),
            (self.serotoninLabel2, simVars.serotonin),
            (self.aDPLabel2, simVars.aDP),
            (self.calciumIonsLabel2, simVars.calcium_ions),
            (self.fibrinogenLabel, simVars.fibrinogen),
            (self.fibrinLabel, simVars.fibrin),
            (self.prothrombinLabel, simVars.prothrombin),
            (self.thrombinLabel, simVars.thrombin),
            (self.tissueFactorLabel, simVars.tissue_factor),
            (self.factor7Label, simVars.factor7),
            (self.factor7aLabel, simVars.factor7a),
            (self.factor8Label, simVars.factor8),
            (self.factor8aLabel, simVars.factor8a),
            (self.factor9Label, simVars.factor9),
            (self.factor9aLabel, simVars.factor9a),
            (self.factor11Label, simVars.factor11),
            (self.factor11aLabel, simVars.factor11a),
            (self.factor12Label, simVars.factor12),
            (self.factor12aLabel, simVars.factor12a),
            (self.factor10Label, simVars.factor10),
            (self.factor10aLabel, simVars.factor10a),
            (self.factor5Label, simVars.factor5),
            (self.factor5aLabel, simVars.factor5a),
            (self.factor13Label, simVars.factor13),
            (self.factor13aLabel, simVars.factor13a),
            (self.iNRLabel, simVars.iNR),
            (self.aPTTLabel, simVars.aPTT),
            (self.proteinCLabel2, simVars.protein_c),
            (self.proteinCaLabel2, simVars.protein_ca),
            (self.tFPILabel2, simVars.tFPI),
            (self.thrombomodulinLabel2, simVars.thrombomodulin),
            (self.antithrombin3Label2, simVars.antithrombin3),
            (self.proteinSLabel2, simVars.protein_s),
            (self.c1EsteraseInhibitorLabel2, simVars.c1_esterase_inhibitor),
            (self.plasminLabel2, simVars.plasmin),
            (self.plasminogenLabel2, simVars.plasminogen),
            (self.fDPLabel2, simVars.fDP),
            (self.tPALabel2, simVars.tPA),
            (self.tAFILabel2, simVars.tAFI),
            (self.tAFIaLabel2, simVars.tAFIa),
            (self.pAI1Label2, simVars.pAI1),
            (self.a2ALabel2, simVars.a2A),
            (
                self.crossLinkedFibrinLabel,
                simVars.cross_linked_fibrin,
            ),
            (
                self.exposedSubendotheliumLabel,
                simVars.subendothelium,
            ),
        )

        self.timeLimitButton.setText(f"Time Limit {'ON' if self.time_limit else 'OFF'}")

        for label in updating_labels:
            label[0].setText(format(abs(label[1]), ".2f"))
        self.currentTimeLabel.setText(f"Time: {simVars.current_time//2} seconds")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
