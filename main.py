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
from PyQt5.QtCore import QTimer
from simulation_variables import SimulationVariables


# description_message = [
#     "Tissue damage results in release of tissue factor and endothelins",
#     "Endothelins result in vasoconstriction of damaged blood vessel",
#     "Primary haemostasis (platelet plug formation)",
#     "Platelets become activated",
#     "Platelets adhere to damaged endothelium",
#     "Secondary haemostasis (Coagulation cascade)",
#     "Fibrin forms cross-linked mesh",
#     "Stable thrombus formed",
# ]

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

speeds = ["x 1", "x 2", "x 4", "x 8", "x 16", "x 0.5"]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()

        self.setStyleSheet(f"background-color: {CREAM};")
        self.setWindowIcon(QIcon("icon.jpg"))
        self.setWindowTitle("Coagulation Simulator")
        self.layout = QGridLayout()

        column_widths = (
            (0, 0),
            (1, 45),
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

        self.primaryHaemLabel = self.create_label(0, 1, "Primary Haemostasis")
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

        self.calciumIonsLabel = QLabel()
        self.layout.addWidget(self.calciumIonsLabel, 3, 3)

        self.plateletsLabel = QLabel()
        self.layout.addWidget(self.plateletsLabel, 4, 3)

        self.descriptionLabel = QLabel()
        self.layout.addWidget(self.descriptionLabel, 5, 3)
        self.set_colour(self.descriptionLabel, "#90EE90")

        self.testResultsLabel = QLabel("Test Results")
        self.layout.addWidget(self.testResultsLabel, 0, 3)

        self.iNRLabel = QLabel()
        self.layout.addWidget(self.iNRLabel, 1, 3)

        self.aPTTLabel = QLabel()
        self.layout.addWidget(self.aPTTLabel, 2, 3)

        for test_widget in [
            self.testResultsLabel,
            self.iNRLabel,
            self.aPTTLabel,
            self.calciumIonsLabel,
            self.plateletsLabel,
        ]:
            self.set_colour(test_widget, WHITE)

        self.timer.timeout.connect(self.time_passes)

    def create_button(self, row, column, text, colour, action=None):
        this_button = QPushButton(text)
        self.layout.addWidget(this_button, row, column)
        self.set_colour(this_button, colour)
        if action is not None:
            this_button.clicked.connect(action)
        return this_button

    def create_label(self, row, column, text=""):
        this_label = QLabel()
        self.layout.addWidget(this_label, row, column)
        this_label.setText(text)
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
            5: 0.5,
        }
        simVars.speed = speed_dictionary[index]

    def disorder_changed(self, text):
        simVars.reset()
        match text:
            case "Liver Disorder":
                simVars.prothrombin = 100
                simVars.factor7 = 10
                simVars.factor9 = 10
                simVars.factor10 = 10
                simVars.platelets = 100
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

        simVars.catalyze("subendothelium", "factor12", "factor12a", 150)
        simVars.catalyze("factor12a", "factor11", "factor11a", 500)
        simVars.catalyze("factor11a", "factor9", "factor9a", 100, calcium=True)
        simVars.catalyze(
            "factor9a",
            "factor10",
            "factor10a",
            40000,
            catalyst_2="factor8a",
            multiplier=2000,
            calcium=True,
        )
        simVars.catalyze("tissue_factor", "factor7", "factor7a", 400)
        simVars.catalyze("factor7a", "factor10", "factor10a", 400)
        simVars.catalyze(
            "factor10a",
            "prothrombin",
            "thrombin",
            400,
            catalyst_2="factor5a",
            multiplier=100,
            calcium=True,
        )
        simVars.catalyze("thrombin", "factor11", "factor11a", 25)
        simVars.catalyze("thrombin", "factor8", "factor8a", 25)
        simVars.catalyze(
            "thrombin",
            "factor5",
            "factor5a",
            5000,
            catalyst_2="factor10a",
            multiplier=500,
        )
        simVars.catalyze("thrombin", "factor7", "factor7a", 25)
        simVars.catalyze("thrombin", "fibrinogen", "fibrin", 10, calcium=True)
        simVars.catalyze("thrombin", "factor13", "factor13a", 15)
        simVars.catalyze("factor13a", "fibrin", "cross_linked_fibrin", 15)

        simVars.current_time += 1
        if simVars.cross_linked_fibrin == 50000:
            self.stop_timer()
        self.update_ui_components()

    def update_ui_components(self):
        platelet_descriptor = ""
        if simVars.platelets > 450:
            platelet_descriptor = "(thrombocytosis)"
        elif simVars.platelets < 150:
            platelet_descriptor = "(thrombocytopaenia)"
        self.plateletsLabel.setText(
            f"Platelet Level: {simVars.platelets} * 10^9/L {platelet_descriptor}"
        )
        self.fibrinogenLabel.setText(f"\tFibrinogen (factor I) = {simVars.fibrinogen}")
        self.fibrinLabel.setText(f"\tFibrin (factor Ia) = {simVars.fibrin}")
        self.prothrombinLabel.setText(
            f"\tProthrombin (factor II) = {simVars.prothrombin}"
        )
        self.thrombinLabel.setText(f"\tThrombin (factor IIa) = {simVars.thrombin}")
        self.tissueFactorLabel.setText(
            f"\tExposed Tissue Factor (factor III): {simVars.tissue_factor}"
        )
        self.factor7Label.setText(f"\tFactor VII: {simVars.factor7}")
        self.factor7aLabel.setText(f"\tFactor VIIa: {simVars.factor7a}")
        self.factor8Label.setText(f"\tFactor VIII: {simVars.factor8}")
        self.factor8aLabel.setText(f"\tFactor VIIIa: {simVars.factor8a}")
        self.factor9Label.setText(f"\tFactor IX: {simVars.factor9}")
        self.factor9aLabel.setText(f"\tFactor IXa: {simVars.factor9a}")
        self.factor11Label.setText(f"\tFactor XI: {simVars.factor11}")
        self.factor11aLabel.setText(f"\tFactor XIa: {simVars.factor11a}")
        self.factor12Label.setText(f"\tFactor XII: {simVars.factor12}")
        self.factor12aLabel.setText(f"\tFactor XIIa: {simVars.factor12a}")
        self.factor10Label.setText(f"\tFactor X: {simVars.factor10}")
        self.factor10aLabel.setText(f"\tFactor Xa: {simVars.factor10a}")
        self.factor5Label.setText(f"\tFactor V: {simVars.factor5}")
        self.factor5aLabel.setText(f"\tFactor Va: {simVars.factor5a}")

        self.calciumIonsLabel.setText(
            f"Ca2+ (factor IV) Level: {simVars.calcium_ions}mmol/L"
        )
        self.factor13Label.setText(f"\tFactor XIII: {simVars.factor13}")
        self.factor13aLabel.setText(f"\tFactor XIIIa: {simVars.factor13a}")
        self.crossLinkedFibrinLabel.setText(
            f"\tCross-linked Fibrin: {simVars.cross_linked_fibrin}"
        )
        self.iNRLabel.setText(
            f"INR: {round(float(simVars.iNR), 2)} (extrinsic measure)"
        )
        self.aPTTLabel.setText(
            f"Activated Partial Thromboplastin Time: {simVars.aPTT}s (intrinsic measure)"
        )
        self.currentTimeLabel.setText(f"Current Time: {simVars.current_time//2}")
        self.exposedSubendotheliumLabel.setText(
            f"\tExposed subendothelium (containing Kallikrein & HMWK): {simVars.subendothelium}"
        )


app = QApplication([])
window = MainWindow()
window.show()
app.exec()
