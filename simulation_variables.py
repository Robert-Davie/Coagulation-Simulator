import math
from dataclasses import dataclass
import random


line_1_y = []
line_2_y = []


@dataclass
class SimulationVariables:
    # values of compounds are roughly aiming to be in ratio of 1AU = 0.1ng/mL
    speed: int = 64
    vWF: float = 100000
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
    calcium_ions: float = 1.2
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
    protein_c: float = 10000
    protein_ca: float = 0
    tFPI: float = 0
    antithrombin3: float = 0
    thrombomodulin: float = 0
    protein_s: float = 0
    c1_esterase_inhibitor: float = 0
    plasmin: float = 0
    plasminogen: float = 10000
    tAFI: float = 1000
    tAFIa: float = 0
    tPA: float = 0
    pAI1: float = 100
    a2A: float = 100
    fDP: float = 0
    dummy: float = 0

    def reset(self):
        self.__dict__ = SimulationVariables().__dict__

    def catalyze(
        self,
        catalyst,
        source,
        destination,
        factor,
        catalyst_2=None,
        multiplier=1.0,
        inhibitor_1=None,
        multiplier_i1=0.0,
        inhibitor_2=None,
        multiplier_i2=0.0,
        tail=100.0,
        calcium=False,
        vitamin_k=False,
    ):
        catalyst_amount = self.__dict__[catalyst]
        catalyst_2_amount = 0
        if catalyst_2:
            catalyst_2_amount = self.__dict__[catalyst_2]
        inhibitor_amount = 0
        i1, i2 = 0, 0
        if inhibitor_1:
            i1 = self.__dict__[inhibitor_1]
        if inhibitor_2:
            i2 = self.__dict__[inhibitor_2]
        inhibitor_amount = max(
            i1 * multiplier_i1,
            i2 * multiplier_i2,
        )
        if self.__dict__[source] > 0:
            choice2 = max(
                catalyst_amount / factor - inhibitor_amount,
                catalyst_2_amount / factor - inhibitor_amount,
                min(catalyst_amount, catalyst_2_amount) * (multiplier / factor)
                - inhibitor_amount,
                0,
            )
            if calcium and self.calcium_ions < 1.2:
                choice2 *= (calcium / 1.2) ** 3
            change = round(min(self.__dict__[source] / tail, choice2), 10)
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
        # convert X to Xa by VIIIa and IXa
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
        # convert II to IIa by Xa
        self.catalyze(
            "factor10a",
            "prothrombin",
            "thrombin",
            120000,
            catalyst_2="factor5a",
            multiplier=6000,
            calcium=True,
            inhibitor_1="tFPI",
            multiplier_i1=0.1,
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
        self.catalyze("factor13a", "fibrin", "cross_linked_fibrin", 50)
        self.catalyze("tPA", "plasminogen", "plasmin", 20, tail=500)
        self.catalyze(
            "plasmin",
            "cross_linked_fibrin",
            "fDP",
            20,
            inhibitor_1="tAFIa",
            multiplier_i1=0.15,
        )
        self.catalyze(
            "plasmin",
            "fibrin",
            "fDP",
            40,
            inhibitor_1="tAFIa",
            multiplier_i1=0.15,
        )
        self.catalyze("thrombin", "tAFI", "tAFIa", 400)
        self.catalyze("pAI1", "tPA", "dummy", 500)
        self.catalyze("a2A", "plasmin", "dummy", 100)
        if self.thrombomodulin > 0.01:
            self.catalyze(
                "thrombomodulin",
                "protein_c",
                "protein_ca",
                100,
                catalyst_2="thrombin",
                multiplier=100,
            )
        self.catalyze(
            "protein_ca",
            "factor8a",
            "dummy",
            2000,
            catalyst_2="protein_s",
            multiplier=2000,
        )
        self.catalyze(
            "protein_ca",
            "factor5a",
            "dummy",
            2000,
            catalyst_2="protein_s",
            multiplier=2000,
        )
        self.catalyze("tFPI", "factor7a", "dummy", 2000)
        self.catalyze("tFPI", "factor10a", "dummy", 2000)
        self.catalyze("c1_esterase_inhibitor", "factor11a", "dummy", 2000)
        self.catalyze("c1_esterase_inhibitor", "factor12a", "dummy", 2000)
        self.catalyze("antithrombin3", "thrombin", "dummy", 2000)
        self.catalyze("antithrombin3", "factor10a", "dummy", 2000)
        self.catalyze("antithrombin3", "factor9a", "dummy", 2000)

        self.current_time += 1
