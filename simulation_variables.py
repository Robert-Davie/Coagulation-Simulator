import math
from dataclasses import dataclass
import random


@dataclass
class SimulationVariables:
    speed: int = 1
    subendothelium: int = 0
    current_time: int = 0
    injury_stage: int = -1
    iNR: float = 1.0
    aPTT: float = 30
    calcium_ions: float = 2.35
    fibrinogen: int = 50000
    fibrin: int = 0
    prothrombin: int = 10000
    thrombin: int = 0
    tissue_factor: int = 0
    factor5: int = 1000
    factor5a: int = 0
    factor7: int = 100
    factor7a: int = 0
    factor8: int = 1000
    factor8a: int = 0
    factor9: int = 1000
    factor9a: int = 0
    factor10: int = 1000
    factor10a: int = 0
    factor11: int = 1000
    factor11a: int = 0
    factor12: int = 1000
    factor12a: int = 0
    factor13: int = 10000
    factor13a: int = 0
    cross_linked_fibrin: int = 0
    platelets: int = 300
    time: int = 0

    def reset(self):
        self.__dict__ = SimulationVariables().__dict__

    def catalyze(
        self,
        catalyst,
        source,
        destination,
        factor,
        catalyst_2=None,
        multiplier=1,
        calcium=False,
        vitamin_k=False,
    ):
        catalyst_amount = self.__dict__[catalyst]
        catalyst_2_amount = 0
        if catalyst_2:
            catalyst_2_amount = self.__dict__[catalyst_2]
        if self.__dict__[source] > 0:

            choice2 = max(
                math.ceil(catalyst_amount / factor - random.random()),
                math.ceil(catalyst_2_amount / factor - random.random()),
                math.ceil(
                    min(catalyst_amount, catalyst_2_amount) * multiplier / factor - 0.1
                ),
                0,
            )
            change = min(self.__dict__[source], choice2)
            self.__dict__[destination] += change
            self.__dict__[source] -= change
