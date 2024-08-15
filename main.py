from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QPushButton,
    QGridLayout,
    QMainWindow,
    QComboBox,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt
from simulation_variables import SimulationVariables, cross_linked_over_time

WHITE = "#FFFFFF"
CREAM = "#FFFDD0"
GOLD = "#FFD700"
ROYALBLUE = "#4169E1"
simVars = SimulationVariables()

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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.speed = 1
        self.timer = QTimer()
        self.timer.timeout.connect(self.time_passes)

        self.setStyleSheet(f"background-color: {CREAM};")
        self.setWindowIcon(QIcon("icon.jpg"))
        self.setWindowTitle("Coagulation Simulator")
        self.layout = QGridLayout()

        column_widths = (
            (0, 15),
            (1, 5),
            (2, 45),
            (3, 45),
            (4, 15),
        )
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
        extrinsic_row = intrinsic_row + 10
        common_pathway_row = extrinsic_row + 4

        actions_row = 8
        disease_row = actions_row + 2

        self.injuryButton = self.create_button(
            actions_row, 4, "Injury", GOLD, self.injury_occurs
        )
        self.addFibrinogen = self.create_button(
            actions_row + 1, 4, "Add Fibrinogen", GOLD, self.increase_fibrinogen_level
        )

        self.create_label(disease_row, 4, "Disorder:")

        self.disorderBox = self.create_combobox(disease_row + 1, 4, disorders)
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
            self.create_button(i, 4, simulation_button_names[i], ROYALBLUE)
            for i in range(0, 4)
        )

        self.startTimerButton.clicked.connect(self.start_timer)
        self.stopTimerButton.clicked.connect(self.stop_timer)
        self.oneTimeStep.clicked.connect(self.time_passes)
        self.resetButton.clicked.connect(self.reset_simulation)

        self.pickSpeedLabel = self.create_label(4, 4, "Speed:")
        self.speedChoiceBox = self.create_combobox(5, 4, speeds)
        self.speedChoiceBox.currentIndexChanged.connect(self.new_speed)
        self.currentTimeLabel = self.create_label(6, 4)

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
        ) = (self.create_label(common_pathway_row + i, 2) for i in range(0, 12))

        self.commonPathwayLabel.setText("Common Pathway")

        self.primaryHaemLabel = self.create_label(0, 0, "Primary Haemostasis")
        self.primaryHaemLabel.setAlignment(Qt.AlignLeft)
        self.secondaryHaemLabel = self.create_label(0, 2, "Secondary Haemostasis")

        (
            self.intrinsicPathwayLabel,
            self.exposedSubendotheliumLabel,
            self.factor12Label,
            self.factor12aLabel,
            self.factor11Label,
            self.factor11aLabel,
            self.factor9Label,
            self.factor9aLabel,
            self.factor8Label,
            self.factor8aLabel,
        ) = (self.create_label(intrinsic_row + i, 2) for i in range(0, 10))

        self.intrinsicPathwayLabel.setText("Intrinsic Pathway")

        (
            self.extrinsicPathwayLabel,
            self.tissueFactorLabel,
            self.factor7Label,
            self.factor7aLabel,
        ) = (self.create_label(extrinsic_row + i, 2) for i in range(0, 4))

        self.extrinsicPathwayLabel.setText("Extrinsic Pathway")

        (
            self.testResultsLabel,
            self.iNRLabel,
            self.aPTTLabel,
            self.descriptionLabel,
        ) = (self.create_label(i, 3, "", WHITE) for i in range(4))

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
        ) = (self.create_label(i, 0) for i in range(1, 14))

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
        ) = (self.create_label(i, 1, "test", set_align="RIGHT") for i in range(1, 14))

        self.testResultsLabel.setText("Test Results:")
        self.set_colour(self.descriptionLabel, "#90EE90")

    def create_button(self, row, column, text, colour, action=None):
        this_button = QPushButton(text)
        self.layout.addWidget(this_button, row, column)
        self.set_colour(this_button, colour)
        if action is not None:
            this_button.clicked.connect(action)
        return this_button

    def create_label(self, row, column, text="", colour="", set_align="RIGHT"):
        this_label = QLabel()
        self.layout.addWidget(this_label, row, column)
        if colour != "":
            self.set_colour(this_label, colour)
        this_label.setText(text)
        alignment = Qt.AlignLeft
        match set_align:
            case "RIGHT":
                alignment = Qt.AlignRight
            case "CENTRE":
                alignment = Qt.AlignCenter
            case "LEFT":
                alignment = Qt.AlignLeft
        this_label.setAlignment(alignment)
        return this_label

    def create_combobox(self, row, column, options):
        this_box = QComboBox()
        self.layout.addWidget(this_box, row, column)
        this_box.addItems(options)
        return this_box

    def set_colour(self, widget, colour):
        widget.setStyleSheet(f"background-color : {colour}")

    def injury_occurs(self):
        simVars.tissue_factor = 100
        simVars.subendothelium = 100
        simVars.injury_stage = 0
        self.update_ui_components()

    def increase_fibrinogen_level(self):
        simVars.fibrinogen += 20
        self.update_ui_components()

    def start_timer(self):
        timer_speed = int(500 // self.speed)
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
        self.speed = speed_dictionary[index]

    def disorder_changed(self, text):
        simVars.reset()
        match text:
            case "Liver Disorder":
                simVars.prothrombin = 100
                simVars.factor7 = 10
                simVars.factor9 = 10
                simVars.factor10 = 10
                simVars.platelets = 100
            case "Haemophilia C":
                simVars.factor11 = 0
            case "Haemophilia B":
                simVars.factor9 = 0
            case "Haemophilia A (Mild)":
                simVars.factor8 = 500
            case "Haemophilia A (Severe)":
                simVars.factor8 = 0
            case _:
                pass

        self.update_ui_components()

    def time_passes(self):

        simVars.catalyze("subendothelium", "factor12", "factor12a", 100)
        simVars.catalyze("factor12a", "factor11", "factor11a", 500)
        simVars.catalyze(
            "factor11a",
            "factor9",
            "factor9a",
            2000,
            calcium=True,
            catalyst_2="factor7a",
            multiplier=200,
        )
        simVars.catalyze(
            "factor9a",
            "factor10",
            "factor10a",
            120000,
            catalyst_2="factor8a",
            multiplier=3000,
            calcium=True,
        )
        simVars.catalyze("tissue_factor", "factor7", "factor7a", 1000)
        simVars.catalyze("factor7a", "factor10", "factor10a", 1000)
        simVars.catalyze(
            "factor10a",
            "prothrombin",
            "thrombin",
            120000,
            catalyst_2="factor5a",
            multiplier=6000,
            calcium=True,
        )
        simVars.catalyze("thrombin", "factor11", "factor11a", 1000)
        simVars.catalyze("thrombin", "factor8", "factor8a", 1000)
        simVars.catalyze("thrombin", "factor7", "factor7a", 1000)
        simVars.catalyze(
            "thrombin",
            "factor5",
            "factor5a",
            120000,
            catalyst_2="factor10a",
            multiplier=6000,
        )
        simVars.catalyze("thrombin", "fibrinogen", "fibrin", 15, calcium=True)
        simVars.catalyze("thrombin", "factor13", "factor13a", 19)
        simVars.catalyze("factor13a", "fibrin", "cross_linked_fibrin", 40)

        simVars.current_time += 1
        cross_linked_over_time.append(simVars.cross_linked_fibrin)
        if round(simVars.cross_linked_fibrin, 7) == 50000:
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
            (self.factor7aLabel, f"\tFactor VII: {round(simVars.factor7a, 3)}"),
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
            (self.iNRLabel, f"INR: {round(float(simVars.iNR), 2)} (extrinsic measure)"),
            (
                self.aPTTLabel,
                f"Activated Partial Thromboplastin Time: {simVars.aPTT}s (intrinsic measure)",
            ),
            (self.currentTimeLabel, f"Current Time: {simVars.current_time//2}"),
            (
                self.exposedSubendotheliumLabel,
                f"\tExposed Subendothelium (containing Kallikrein & HMWK): {simVars.subendothelium}",
            ),
        )

        for label in updating_labels:
            label[0].setText(label[1])


app = QApplication([])
window = MainWindow()
window.show()
app.exec()
