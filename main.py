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
    cross_linked_over_time,
    thrombin_over_time,
)

WHITE = "#FFFFFF"
CREAM = "#FFFDD0"
GOLD = "#FFD700"
ROYALBLUE = "#4169E1"
simVars = SimulationVariables()
SIMULATION_END = 50000

disorders = [
    "None",
    "Von Willebrand Disease",
    "Haemophilia A (Mild)",
    "Haemophilia A (Severe)",
    "Haemophilia B",
    "Haemophilia C",
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
        self.timer.timeout.connect(self.time_passes)

        self.setStyleSheet(f"background-color: {CREAM};")
        self.setWindowIcon(QIcon("icon.jpg"))
        self.setWindowTitle("Coagulation Simulator")
        self.layout = QGridLayout()

        column_widths = ((0, 15), (1, 5), (2, 15), (3, 5), (4, 40), (5, 10))
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

        actions_row = 8
        disease_row = actions_row + 3
        self.injuryButton = self.create_widget(
            actions_row,
            5,
            text="Injury",
            colour=GOLD,
            action=self.injury_occurs,
            widget_type="BUTTON",
        )
        self.addFibrinogen = self.create_widget(
            actions_row + 1,
            5,
            text="Add Fibrinogen",
            colour=GOLD,
            action=self.increase_fibrinogen_level,
            widget_type="BUTTON",
        )
        self.fibrinolysisButton = self.create_widget(
            actions_row + 2,
            5,
            text="Fibrinolysis",
            colour=GOLD,
            action=self.fibrinolysis_occurs,
            widget_type="BUTTON",
        )

        self.create_widget(disease_row, 5, text="Disorder:", widget_type="LABEL")

        self.disorderBox = self.create_widget(
            disease_row + 1, 5, options=disorders, widget_type="COMBOBOX"
        )
        self.disorderBox.currentTextChanged.connect(self.disorder_changed)
        self.disorderBox.setSizeAdjustPolicy(
            self.disorderBox.AdjustToMinimumContentsLengthWithIcon
        )
        self.setup_time_functionality()
        self.setup_primary_haem()
        self.setup_secondary_haem()
        self.setup_anticoagulation()
        self.setup_fibrinolysis()
        self.set_up_plot()

    def setup_time_functionality(self):
        simulation_button_names = (
            "Start/Continue Simulation",
            "Pause Simulation",
            "Next Step",
            "Stop and Reset Simulation",
        )

        (
            self.startTimerButton,
            self.stopTimerButton,
            self.oneTimeStep,
            self.resetButton,
        ) = (
            self.create_widget(
                i,
                5,
                text=simulation_button_names[i],
                colour=ROYALBLUE,
                widget_type="BUTTON",
            )
            for i in range(0, 4)
        )

        self.startTimerButton.clicked.connect(self.start_timer)
        self.stopTimerButton.clicked.connect(self.stop_timer)
        self.oneTimeStep.clicked.connect(self.time_passes)
        self.resetButton.clicked.connect(self.reset_simulation)

        self.pickSpeedLabel = self.create_widget(
            4, 5, text="Speed:", widget_type="LABEL"
        )
        self.speedChoiceBox = self.create_widget(
            5, 5, options=speeds, widget_type="COMBOBOX"
        )
        self.speedChoiceBox.currentIndexChanged.connect(self.new_speed)
        self.currentTimeLabel = self.create_widget(6, 5, widget_type="LABEL")

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
            "TAFI",
            "TAFIa",
            "Plasmin Activator Inhibitor 1",
            "Alpha 2 Antiplasmin",
        )
        (
            self.plasminLabel,
            self.plasminogenLabel,
            self.fDPLabel,
            self.tPALabel,
            self.tAFILabel,
            self.tAFIaLabel,
            self.pAI1Label,
            self.a2ALabel,
        ) = (
            self.create_widget(
                23 + i, 0, widget_type="LABEL", text=fibrinolysis_texts[i]
            )
            for i in range(8)
        )

        (
            self.plasminLabel2,
            self.plasminogenLabel2,
            self.fDPLabel2,
            self.tPALabel2,
            self.tAFILabel2,
            self.tAFIaLabel2,
            self.pAI1Label2,
            self.a2ALabel2,
        ) = (self.create_widget(23 + i, 1, widget_type="LABEL") for i in range(8))

    def setup_anticoagulation(self):
        self.anticoagLabel = self.create_widget(
            14, 0, widget_type="LABEL", text="Antithrombotic Pathway"
        )
        self.set_bold(self.anticoagLabel)
        anticoagulation_texts = (
            "Protein C",
            "Activated Protein C",
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
            "Activated Partial Thromboplastin Time (APTT)",
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
        self.plot_widget.addLegend()
        self.plot_widget.setYRange(0, 50000)
        self.plot_widget.setXRange(0, 1000)
        self.plot_widget.showGrid(x=True, y=True)
        self.pen = pg.mkPen(color=(255, 0, 0))
        time_list = [i / 2 for i in range(len(cross_linked_over_time))]
        self.line = self.plot_widget.plot(
            time_list,
            cross_linked_over_time,
            pen=pg.mkPen(color=(255, 0, 0), width=3),
            name="line1",
        )
        self.line2 = self.plot_widget.plot(
            pen=pg.mkPen(color=(0, 0, 255), width=3), name="line2"
        )

    def update_lines(self):
        time_list = [i / 2 for i in range(len(cross_linked_over_time))]
        self.line.setData(time_list, cross_linked_over_time)
        self.line2.setData(time_list, thrombin_over_time)

    def time_passes(self):
        simVars.time_passes()
        self.update_lines()

        cross_linked_over_time.append(simVars.cross_linked_fibrin)
        thrombin_over_time.append(simVars.thrombin)
        if simVars.current_time // 2 == 1000:
            self.stop_timer()
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

    def injury_occurs(self):
        simVars.tissue_factor = 100
        simVars.subendothelium = 100
        simVars.injury_stage = 0
        self.update_ui_components()

    def increase_fibrinogen_level(self):
        simVars.fibrinogen += 20
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
        cross_linked_over_time.clear()
        thrombin_over_time.clear()
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
        cross_linked_over_time.clear()
        thrombin_over_time.clear()
        self.update_lines()

        self.stop_timer()
        self.speedChoiceBox.setCurrentIndex(0)
        self.disorderBox.setCurrentIndex(0)
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
        simVars.reset()
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
            case "HAEMOPHILIA A (MILD)":
                simVars.factor8 = 500
            case "HAEMOPHILIA A (SEVERE)":
                simVars.factor8 = 0
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

        for label in updating_labels:
            label[0].setText(format(abs(label[1]), ".2f"))
        self.currentTimeLabel.setText(f"Time: {simVars.current_time//2}")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
