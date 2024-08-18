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

speeds = ["x 1", "x 2", "x 4", "x 8", "x 16", "x 32", "x 0.5"]

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
        intrinsic_row = 1
        extrinsic_row = intrinsic_row + 11
        common_pathway_row = extrinsic_row + 5

        actions_row = 8
        disease_row = actions_row + 2

        self.primaryHaemLabel = self.create_widget(
            0, 0, text="Primary Haemostasis", widget_type="LABEL"
        )
        self.set_bold(self.primaryHaemLabel)
        self.secondaryHaemLabel = self.create_widget(
            0, 2, text="Secondary Haemostasis", widget_type="LABEL"
        )
        self.set_bold(self.secondaryHaemLabel)

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

        self.create_widget(disease_row, 5, text="Disorder:", widget_type="LABEL")

        self.disorderBox = self.create_widget(
            disease_row + 1, 5, options=disorders, widget_type="COMBOBOX"
        )
        self.disorderBox.currentTextChanged.connect(self.disorder_changed)
        self.disorderBox.setSizeAdjustPolicy(
            self.disorderBox.AdjustToMinimumContentsLengthWithIcon
        )

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
                common_pathway_row + i,
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
                common_pathway_row + i, 3, widget_type="LABEL", alignment="RIGHT"
            )
            for i in range(1, 12)
        )

        intrinsic_names = (
            "Intrinsic Pathway",
            "Activated Partial Thromboplastin Time (APTT)",
            "Exposed Subendothelium (with Kallikrein & HMWK)",
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
                intrinsic_row + i,
                2,
                widget_type="LABEL",
                alignment="RIGHT",
                text=intrinsic_names[i],
            )
            for i in range(0, 11)
        )

        (
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
                intrinsic_row + i, 3, widget_type="LABEL", alignment="RIGHT"
            )
            for i in range(2, 11)
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
                extrinsic_row + i,
                2,
                widget_type="LABEL",
                text=extrinsic_names[i],
                alignment="RIGHT",
            )
            for i in range(5)
        )

        (
            self.tissueFactorLabel,
            self.factor7Label,
            self.factor7aLabel,
        ) = (
            self.create_widget(
                extrinsic_row + i, 3, widget_type="LABEL", alignment="RIGHT"
            )
            for i in range(2, 5)
        )

        self.extrinsicPathwayLabel2.setText("Extrinsic Pathway")
        self.iNRLabel2.setText("International Normalized Ratio (INR)")
        self.set_bold(self.extrinsicPathwayLabel2)

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
        self.calciumIonsLabel.setText("\tCalcium")

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
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget, 8, 4, 21, 1)
        self.plot_widget.setTitle("Compound Levels over Time", color=(0, 0, 0))
        self.plot_widget.setBackground("w")
        self.plot_widget.setYRange(0, 50000)
        self.plot_widget.setXRange(0, 1000)
        self.plot_widget.showGrid(x=True, y=True)
        self.pen = pg.mkPen(color=(255, 0, 0))
        time_list = [i / 2 for i in range(len(cross_linked_over_time))]
        self.line = self.plot_widget.plot(
            time_list, cross_linked_over_time, pen=pg.mkPen(color=(255, 0, 0), width=3)
        )
        self.line2 = self.plot_widget.plot(pen=pg.mkPen(color=(0, 0, 255), width=3))

    def update_lines(self):
        time_list = [i / 2 for i in range(len(cross_linked_over_time))]
        self.line.setData(time_list, cross_linked_over_time)
        self.line2.setData(time_list, thrombin_over_time)

    def time_passes(self):
        simVars.time_passes()
        self.update_lines()

        cross_linked_over_time.append(simVars.cross_linked_fibrin)
        thrombin_over_time.append(simVars.thrombin)
        if round(simVars.cross_linked_fibrin, 4) == SIMULATION_END:
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

    def start_timer(self):
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
            6: 0.5,
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
        )
        for label_pair in updating_labels:
            label_pair[0].setText(format(label_pair[1], ".2f").rjust(10))

        updating_labels = (
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
