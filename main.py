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
import math
from dataclasses import dataclass


description_message = [
    "Tissue damage results in release of tissue factor and endothelins",
    "Endothelins result in vasoconstriction of damaged blood vessel",
    "Primary haemostasis (platelet plug formation)",
    "Platelets become activated",
    "Platelets adhere to damaged endothelium",
    "Secondary haemostasis (Coagulation cascade)",
    "Fibrin forms cross-linked mesh",
    "Stable thrombus formed",
]


ROYALBLUE = "#4169E1"


@dataclass
class SimulationVariables:
    speed: int = 1
    subendothelium: str = "ABSENT"
    current_time: int = 0
    injury_stage: int = -1
    iNR: float = 1.0
    aPTT: float = 30
    calcium_ions: float = 2.35
    fibrinogen: int = 10000
    fibrin: int = 0
    prothrombin: int = 1000
    thrombin: int = 0
    tissue_factor: int = 0
    factor5: int = 100
    factor5a: int = 0
    factor7: int = 100
    factor7a: int = 0
    factor8: int = 100
    factor8a: int = 0
    factor9: int = 100
    factor9a: int = 0
    factor10: int = 100
    factor10a: int = 0
    factor11: int = 100
    factor11a: int = 0
    factor12: int = 100
    factor12a: int = 0
    factor13: int = 150
    factor13a: int = 0
    cross_linked_fibrin: int = 0
    platelets: int = 300
    time: int = 0

    def reset(self):
        self.__dict__ = SimulationVariables().__dict__

    def catalyze(self, catalyst, source, destination, factor):
        if self.__dict__[source] > 0:
            change = min(self.__dict__[source], round(self.__dict__[catalyst] / factor))
            self.__dict__[destination] += change
            self.__dict__[source] -= change


simVars = SimulationVariables()


class MainWindow(QMainWindow):
    def __init__(self):
        self.timer = QTimer()
        super().__init__()
        self.setStyleSheet("background-color: #FFFDD0;")

        self.setWindowIcon(QIcon("icon.jpg"))
        self.setWindowTitle("Coagulation Simulator")

        self.layout = QGridLayout()
        self.layout.setColumnStretch(0, 0)
        self.layout.setColumnStretch(1, 45)
        self.layout.setColumnStretch(2, 45)
        self.layout.setColumnStretch(3, 45)
        self.layout.setColumnStretch(4, 15)

        self.ui_components()

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.update_ui_components()
        self.showMaximized()

    def ui_components(self):
        actions_row = 8
        disease_row = actions_row + 2
        intrinsic_row = 1
        extrinsic_row = intrinsic_row + 10
        common_pathway_row = extrinsic_row + 4

        self.injuryButton = QPushButton("Injury")
        self.layout.addWidget(self.injuryButton, actions_row, 4)
        self.injuryButton.setStyleSheet("background-color : #FFD700")
        self.injuryButton.clicked.connect(self.injury_occurs)

        self.addFibrinogen = QPushButton("Add Fibrinogen")
        self.layout.addWidget(self.addFibrinogen, actions_row + 1, 4)
        self.addFibrinogen.setStyleSheet("background-color : #FFD700")
        self.addFibrinogen.clicked.connect(self.increase_fibrinogen_level)

        self.create_label(disease_row, 4, "Disorder:")

        self.disorderBox = QComboBox()
        self.disorderBox.addItems(
            [
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
        )
        self.layout.addWidget(self.disorderBox, disease_row + 1, 4)
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
            self.create_button(i, 4, simulation_button_names[i], "#4169E1")
            for i in range(0, 4)
        )

        self.startTimerButton.clicked.connect(self.start_timer)
        self.stopTimerButton.clicked.connect(self.stop_timer)
        self.oneTimeStep.clicked.connect(self.time_passes)
        self.resetButton.clicked.connect(self.reset_simulation)

        self.speedChoiceBox = QComboBox()
        self.speedChoiceBox.addItems(["x 1", "x 2", "x 4", "x 8", "x 16", "x 0.5"])
        self.layout.addWidget(self.speedChoiceBox, 5, 4)
        self.speedChoiceBox.currentIndexChanged.connect(self.new_speed)

        self.pickSpeedLabel = self.create_label(4, 4, "Speed:")
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
            self.factor8Label,
            self.factor8aLabel,
            self.factor9Label,
            self.factor9aLabel,
            self.factor11Label,
            self.factor11aLabel,
            self.factor12Label,
            self.factor12aLabel,
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
            self.set_colour(test_widget, "#FFFFFF")

        self.timer.timeout.connect(self.time_passes)

    def create_button(self, row, column, text, colour):
        this_button = QPushButton(text)
        self.layout.addWidget(this_button, row, column)
        self.set_colour(this_button, colour)
        return this_button

    def create_label(self, row, column, text=""):
        this_label = QLabel()
        self.layout.addWidget(this_label, row, column)
        this_label.setText(text)
        return this_label

    def set_colour(self, widget, colour):
        widget.setStyleSheet(f"background-color : {colour}")

    def injury_occurs(self):
        simVars.tissue_factor = 100
        simVars.subendothelium = "PRESENT"
        simVars.injury_stage = 0
        self.update_ui_components()

    def increase_fibrinogen_level(self):
        simVars.fibrinogen += 20
        self.update_ui_components()

    def start_timer(self):
        timer_speed = int(500 // simVars.speed)
        self.timer.start(timer_speed)
        self.startTimerButton.setDisabled(True)
        self.set_colour(self.startTimerButton, "#FFFFFF")
        self.speedChoiceBox.setDisabled(True)

    def stop_timer(self):
        self.timer.stop()
        self.startTimerButton.setDisabled(False)
        self.set_colour(self.startTimerButton, ROYALBLUE)
        self.speedChoiceBox.setDisabled(False)

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
        match text:
            case "Liver Disorder":
                simVars.prothrombin = 100
                simVars.factor7 = 10
                simVars.factor9 = 10
                simVars.factor10 = 10
                simVars.platelets = 100
            case "Haemophilia A (Mild)":
                simVars.factor8 = 50
            case "Haemophilia A (Severe)":
                simVars.factor8 = 0
            case _:
                simVars.reset()

        self.update_ui_components()

    def time_passes(self):
        if simVars.factor10 > 0:
            change = min(simVars.factor10, simVars.factor9a // 10)
            simVars.factor10a += change
            simVars.factor10 -= change
        if simVars.factor5 > 0:
            change = min(simVars.factor5, simVars.factor9a // 10)
            simVars.factor5a += change
            simVars.factor5 -= change
        if simVars.factor9 > 0:
            change = min(simVars.factor9, simVars.factor11a // 20)
            simVars.factor9 -= change
            simVars.factor9a += change
        if simVars.factor11 > 0:
            change = min(simVars.factor11, simVars.factor12a // 20)
            simVars.factor11 -= change
            simVars.factor11a += change
        if simVars.subendothelium == "PRESENT" and simVars.factor12 > 0:
            if simVars.time % 5 == 0:
                simVars.factor12 -= 1
                simVars.factor12a += 1

        simVars.catalyze("factor8a", "factor10", "factor10a", 10)
        simVars.catalyze("factor13a", "fibrin", "cross_linked_fibrin", 2)

        if simVars.thrombin > 0:
            if simVars.factor11 > 0:
                simVars.factor11 -= 1
                simVars.factor11a += 1
            if simVars.factor8 > 0:
                simVars.factor8a += 1
                simVars.factor8 -= 1
            if simVars.factor5 >= 1:
                simVars.factor5a += 1
                simVars.factor5 -= 1
            if simVars.factor13 > 0:
                change = min(simVars.factor13, simVars.thrombin // 30)
                simVars.factor13 -= change
                simVars.factor13a += change
            if simVars.factor7 > simVars.thrombin // 10:
                simVars.factor7 -= simVars.thrombin // 10
                simVars.factor7a += simVars.thrombin // 10
            if simVars.fibrinogen > 0:
                change = min(simVars.thrombin, simVars.fibrinogen)
                simVars.fibrinogen -= change
                simVars.fibrin += change
        if simVars.prothrombin > 0:
            change = min(
                simVars.prothrombin, simVars.factor10a // 20 + simVars.factor5a // 20
            )
            simVars.prothrombin -= change
            simVars.thrombin += change
        if simVars.factor10 > 0:
            change = min(simVars.factor10, simVars.factor7a // 5)
            simVars.factor10 -= change
            simVars.factor10a += change
        if simVars.tissue_factor > 0 and simVars.factor7 > 0:
            if simVars.time % 3 == 0:
                simVars.factor7 -= 1
                simVars.factor7a += 1

        simVars.current_time += 1
        if simVars.cross_linked_fibrin == 10000:
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
            f"\tExposed negatively charged subendothelium: {simVars.subendothelium}"
        )


app = QApplication([])
window = MainWindow()
window.show()
app.exec()
