import math
from dataclasses import dataclass
import random


cross_linked_over_time = []


@dataclass
class SimulationVariables:
    speed: int = 1
    vWF: float = 0
    activated_platelets: float = 0
    glyc1b: float = 0
    glyc2b3a: float = 0
    prostacyclin: float = 0
    endothelin: float = 0
    nitric_oxide: float = 0
    alpha_granules: float = 0
    dense_granules: float = 0
    serotonin: float = 0
    aDP: float = 0
    subendothelium: float = 0
    current_time: int = 0
    injury_stage: int = -1
    iNR: float = 1.0
    aPTT: float = 30
    calcium_ions: float = 2.35
    fibrinogen: float = 50000
    fibrin: float = 0
    prothrombin: float = 10000
    thrombin: float = 0
    tissue_factor: float = 0
    factor5: float = 1000
    factor5a: float = 0
    factor7: float = 100
    factor7a: float = 0
    factor8: float = 1000
    factor8a: float = 0
    factor9: float = 1000
    factor9a: float = 0
    factor10: float = 1000
    factor10a: float = 0
    factor11: float = 1000
    factor11a: float = 0
    factor12: float = 1000
    factor12a: float = 0
    factor13: float = 10000
    factor13a: float = 0
    cross_linked_fibrin: float = 0
    platelets: float = 300
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
                catalyst_amount / factor,
                catalyst_2_amount / factor,
                min(catalyst_amount, catalyst_2_amount) * multiplier / factor,
                0,
            )
            change = round(min(self.__dict__[source], choice2), 10)
            self.__dict__[destination] += change
            self.__dict__[source] -= change

    def time_passes(self):
        self.catalyze("subendothelium", "factor12", "factor12a", 100)
        self.catalyze("factor12a", "factor11", "factor11a", 500)
        self.catalyze(
            "factor11a",
            "factor9",
            "factor9a",
            2000,
            calcium=True,
            catalyst_2="factor7a",
            multiplier=200,
        )
        self.catalyze(
            "factor9a",
            "factor10",
            "factor10a",
            120000,
            catalyst_2="factor8a",
            multiplier=3000,
            calcium=True,
        )
        self.catalyze("tissue_factor", "factor7", "factor7a", 1000)
        self.catalyze("factor7a", "factor10", "factor10a", 1000)
        self.catalyze(
            "factor10a",
            "prothrombin",
            "thrombin",
            120000,
            catalyst_2="factor5a",
            multiplier=6000,
            calcium=True,
        )
        self.catalyze("thrombin", "factor11", "factor11a", 1000)
        self.catalyze("thrombin", "factor8", "factor8a", 1000)
        self.catalyze("thrombin", "factor7", "factor7a", 1000)
        self.catalyze(
            "thrombin",
            "factor5",
            "factor5a",
            120000,
            catalyst_2="factor10a",
            multiplier=6000,
        )
        self.catalyze("thrombin", "fibrinogen", "fibrin", 15, calcium=True)
        self.catalyze("thrombin", "factor13", "factor13a", 19)
        self.catalyze("factor13a", "fibrin", "cross_linked_fibrin", 40)

        self.current_time += 1
