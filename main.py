from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QPushButton,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QMainWindow,
    QComboBox,
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QTimer, Qt
from simulation_variables import SimulationVariables, cross_linked_over_time

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

        column_widths = ((0, 15), (1, 5), (2, 15), (3, 5), (4, 30), (5, 10))
        for i in column_widths:
            self.layout.setColumnStretch(i[0], i[1])

        # (
        #     self.layout_0,
        #     self.layout_1,
        #     self.layout_2,
        #     self.layout_3,
        #     self.layout_4,
        #     self.layout_5,
        # ) = (QVBoxLayout() for i in range(6))
        #
        # self.layouts = (
        #     self.layout_0,
        #     self.layout_1,
        #     self.layout_2,
        #     self.layout_3,
        #     self.layout_4,
        #     self.layout_5,
        # )
        #
        # for number, layout in enumerate(self.layouts):
        #     self.layout.addLayout(layout)

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

        (
            self.commonPathwayLabel,
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
            self.create_widget(common_pathway_row + i, 2, widget_type="LABEL")
            for i in range(0, 12)
        )

        self.commonPathwayLabel.setText("Common Pathway")
        self.set_bold(self.commonPathwayLabel)

        (
            self.intrinsicPathwayLabel,
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
            self.create_widget(intrinsic_row + i, 2, widget_type="LABEL")
            for i in range(0, 11)
        )

        self.intrinsicPathwayLabel.setText("Intrinsic Pathway")
        self.aPTTLabel.setText("Activated Partial Thromboplastin Time (APTT)")
        self.set_bold(self.intrinsicPathwayLabel)

        (
            self.extrinsicPathwayLabel,
            self.iNRLabel,
            self.tissueFactorLabel,
            self.factor7Label,
            self.factor7aLabel,
        ) = (
            self.create_widget(extrinsic_row + i, 2, widget_type="LABEL")
            for i in range(0, 5)
        )

        self.extrinsicPathwayLabel.setText("Extrinsic Pathway")
        self.iNRLabel.setText("International Normalized Ratio (INR)")
        self.set_bold(self.extrinsicPathwayLabel)

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
            self.create_widget(i, 1, "", alignment="LEFT", widget_type="LABEL")
            for i in range(1, 14)
        )

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

    def time_passes(self):
        simVars.time_passes()
        cross_linked_over_time.append(simVars.cross_linked_fibrin)
        if round(simVars.cross_linked_fibrin, 4) == SIMULATION_END:
            self.stop_timer()
            for i in cross_linked_over_time:
                print(i)
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
            label_pair[0].setText(str(round(label_pair[1], 3)))

        updating_labels = (
            (
                self.fibrinogenLabel,
                f"\tFibrinogen (factor I): {round(simVars.fibrinogen, 3)}",
            ),
            (self.fibrinLabel, f"\tFibrin (factor Ia): {round(simVars.fibrin, 3)}"),
            (
                self.prothrombinLabel,
                f"\tProthrombin (factor II): {round(simVars.prothrombin, 3)}",
            ),
            (
                self.thrombinLabel,
                f"\tThrombin (factor IIa): {round(simVars.thrombin, 3)}",
            ),
            (
                self.tissueFactorLabel,
                f"\tExposed Tissue Factor (factor III): {round(simVars.tissue_factor, 3)}",
            ),
            (self.factor7Label, f"\tFactor VII: {round(simVars.factor7, 3)}"),
            (self.factor7aLabel, f"\tFactor VIIa: {round(simVars.factor7a, 3)}"),
            (self.factor8Label, f"\tFactor VIII: {round(simVars.factor8, 3)}"),
            (self.factor8aLabel, f"\tFactor VIIIa: {round(simVars.factor8a, 3)}"),
            (self.factor9Label, f"\tFactor IX: {round(simVars.factor9, 3)}"),
            (self.factor9aLabel, f"\tFactor IXa: {round(simVars.factor9a, 3)}"),
            (self.factor11Label, f"\tFactor XI: {round(simVars.factor11, 3)}"),
            (self.factor11aLabel, f"\tFactor XIa: {round(simVars.factor11a, 3)}"),
            (self.factor12Label, f"\tFactor XII: {round(simVars.factor12, 3)}"),
            (self.factor12aLabel, f"\tFactor XIIa: {round(simVars.factor12a, 3)}"),
            (self.factor10Label, f"\tFactor X: {round(simVars.factor10, 3)}"),
            (self.factor10aLabel, f"\tFactor Xa: {round(simVars.factor10a, 3)}"),
            (self.factor5Label, f"\tFactor V: {round(simVars.factor5, 3)}"),
            (self.factor5aLabel, f"\tFactor Va: {round(simVars.factor5a, 3)}"),
            (self.factor13Label, f"\tFactor XIII: {round(simVars.factor13, 3)}"),
            (self.factor13aLabel, f"\tFactor XIIIa: {round(simVars.factor13a, 3)}"),
            (
                self.crossLinkedFibrinLabel,
                f"\tFactor XIII: {round(simVars.factor13, 3)}",
            ),
            (self.factor13aLabel, f"\tFactor XIIIa: {round(simVars.factor13a, 3)}"),
            (
                self.crossLinkedFibrinLabel,
                f"\tCross-linked Fibrin: {round(simVars.cross_linked_fibrin, 3)}",
            ),
            (self.currentTimeLabel, f"Current Time: {simVars.current_time//2}"),
            (
                self.exposedSubendotheliumLabel,
                f"\tExposed Subendothelium (with Kallikrein & HMWK): {simVars.subendothelium}",
            ),
        )

        for label in updating_labels:
            label[0].setText(label[1])


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
