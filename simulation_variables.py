from dataclasses import dataclass
from constants import SIMULATION_END


line_1_y = []
line_2_y = []


@dataclass
class ReactionVariables:
    catalyst_amount: float
    source_amount: float
    divisor: float
    catalyst_2_amount: float = 0.0
    calcium_ions: float = 1.2
    reaction_affected_by_calcium: bool = False
    multiplier: float = 1.0
    inhibitor_1_amount: float = 0.0
    multiplier_i1: float = 0.0
    inhibitor_2_amount: float = 0.0
    multiplier_i2: float = 0.0
    tail: float = 100.0
    vitamin_k: bool = False
    maximum_inhibitor_amount: float = 0.0

    def get_reaction_size(self) -> float:
        maximum_source_available = self.source_amount / self.tail
        if self.source_amount < 0.005:
            return 0
        self.maximum_inhibitor_amount = self.get_maximum_inhibitor_amount()
        maximum_catalyst_available = self.get_maximum_catalyst_available()
        change = min(maximum_source_available, maximum_catalyst_available)
        return change

    def get_maximum_catalyst_available(self):
        maximum_catalyst_available = (
            max(
                self.catalyst_amount,
                self.catalyst_2_amount,
                min(self.catalyst_amount, self.catalyst_2_amount) * self.multiplier,
            )
            / self.divisor
            - self.maximum_inhibitor_amount
        )
        return max(maximum_catalyst_available * self.calcium_multiplier(), 0)

    def calcium_multiplier(self) -> float:
        if not self.reaction_affected_by_calcium:
            return 1.0
        if self.calcium_ions > 1.199:
            return 1.0
        return (self.calcium_ions / 1.2) ** 3

    def get_maximum_inhibitor_amount(self):
        return max(
            self.inhibitor_1_amount * self.multiplier_i1,
            self.inhibitor_2_amount * self.multiplier_i2,
        )


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

    def clear(self):
        self.__dict__ = {i: 0 for i in self.__dict__.keys()}

    def convert_factor12(self):
        reaction = ReactionVariables(
            catalyst_amount=self.subendothelium,
            source_amount=self.factor12,
            divisor=100,
        )
        self.perform_reaction("factor12", "factor12a", reaction.get_reaction_size())

    def convert_factor11(self):
        reaction = ReactionVariables(
            catalyst_amount=self.factor12a,
            source_amount=self.factor11,
            divisor=500,
        )
        self.perform_reaction("factor11", "factor11a", reaction.get_reaction_size())

    def convert_factor9(self):
        reaction = ReactionVariables(
            catalyst_amount=self.factor11a,
            source_amount=self.factor9,
            divisor=2000,
            reaction_affected_by_calcium=True,
            catalyst_2_amount=self.factor7a,
            multiplier=200,
        )
        self.perform_reaction("factor9", "factor9a", reaction.get_reaction_size())

    def convert_factor10_intrinsic(self):
        reaction = ReactionVariables(
            catalyst_amount=self.factor9a,
            catalyst_2_amount=self.factor8a,
            source_amount=self.factor10,
            divisor=120000,
            multiplier=3000,
            reaction_affected_by_calcium=True,
        )
        self.perform_reaction("factor10", "factor10a", reaction.get_reaction_size())

    def convert_factor7(self):
        reaction = ReactionVariables(
            catalyst_amount=self.tissue_factor,
            source_amount=self.factor7,
            divisor=1000,
        )
        self.perform_reaction("factor7", "factor7a", reaction.get_reaction_size())

    def convert_factor10_extrinsic(self):
        reaction = ReactionVariables(
            catalyst_amount=self.factor7a,
            source_amount=self.factor10,
            divisor=1000,
        )
        self.perform_reaction("factor10", "factor10a", reaction.get_reaction_size())

    def convert_prothrombin(self):
        reaction = ReactionVariables(
            catalyst_amount=self.factor10a,
            catalyst_2_amount=self.factor5a,
            source_amount=self.prothrombin,
            divisor=120000,
            multiplier=6000,
            reaction_affected_by_calcium=True,
            inhibitor_1_amount=self.tFPI,
            multiplier_i1=0.1,
        )
        self.perform_reaction("prothrombin", "thrombin", reaction.get_reaction_size())

    def thrombin_convert_factor11(self):
        reaction = ReactionVariables(
            catalyst_amount=self.thrombin,
            source_amount=self.factor11,
            divisor=1000,
        )
        self.perform_reaction("factor11", "factor11a", reaction.get_reaction_size())

    def thrombin_convert_factor8(self):
        reaction = ReactionVariables(
            catalyst_amount=self.thrombin,
            source_amount=self.factor8,
            divisor=1000,
        )
        self.perform_reaction("factor8", "factor8a", reaction.get_reaction_size())

    def thrombin_convert_factor7(self):
        reaction = ReactionVariables(
            catalyst_amount=self.thrombin,
            source_amount=self.factor7,
            divisor=1000,
        )
        self.perform_reaction("factor7", "factor7a", reaction.get_reaction_size())

    def convert_factor5(self):
        reaction = ReactionVariables(
            catalyst_amount=self.thrombin,
            catalyst_2_amount=self.factor10a,
            source_amount=self.factor5,
            divisor=120_000,
            multiplier=6000,
        )
        self.perform_reaction("factor5", "factor5a", reaction.get_reaction_size())

    def convert_fibrinogen(self):
        reaction = ReactionVariables(
            catalyst_amount=self.thrombin,
            source_amount=self.fibrinogen,
            divisor=15,
            reaction_affected_by_calcium=True,
        )
        self.perform_reaction("fibrinogen", "fibrin", reaction.get_reaction_size())

    def convert_factor13(self):
        reaction = ReactionVariables(
            catalyst_amount=self.thrombin,
            source_amount=self.factor13,
            divisor=20,
        )
        self.perform_reaction("factor13", "factor13a", reaction.get_reaction_size())

    def convert_fibrin(self):
        reaction = ReactionVariables(
            catalyst_amount=self.factor13a, source_amount=self.fibrin, divisor=50
        )
        self.perform_reaction(
            "fibrin", "cross_linked_fibrin", reaction.get_reaction_size()
        )

    def time_passes(self):
        self.convert_fibrinogen()
        self.convert_fibrin()
        self.convert_prothrombin()
        self.thrombin_convert_factor7()
        self.thrombin_convert_factor8()
        self.thrombin_convert_factor11()
        self.convert_factor5()
        self.convert_factor7()
        self.convert_factor9()
        self.convert_factor10_extrinsic()
        self.convert_factor10_intrinsic()
        self.convert_factor11()
        self.convert_factor12()
        self.convert_factor13()
        # TODO: add remaining reactions
        # self.catalyze("factor13a", "fibrin", "cross_linked_fibrin", 50)
        # self.catalyze("tPA", "plasminogen", "plasmin", 20, tail=500)
        # self.catalyze(
        #     "plasmin",
        #     "cross_linked_fibrin",
        #     "fDP",
        #     20,
        #     inhibitor_1="tAFIa",
        #     multiplier_i1=0.15,
        # )
        # self.catalyze(
        #     "plasmin",
        #     "fibrin",
        #     "fDP",
        #     40,
        #     inhibitor_1="tAFIa",
        #     multiplier_i1=0.15,
        # )
        # self.catalyze("thrombin", "tAFI", "tAFIa", 400)
        # self.catalyze("pAI1", "tPA", "dummy", 500)
        # self.catalyze("a2A", "plasmin", "dummy", 100)
        # if self.thrombomodulin > 0.01:
        #     self.catalyze(
        #         "thrombomodulin",
        #         "protein_c",
        #         "protein_ca",
        #         100,
        #         catalyst_2="thrombin",
        #         multiplier=100,
        #     )
        # self.catalyze(
        #     "protein_ca",
        #     "factor8a",
        #     "dummy",
        #     2000,
        #     catalyst_2="protein_s",
        #     multiplier=2000,
        # )
        # self.catalyze(
        #     "protein_ca",
        #     "factor5a",
        #     "dummy",
        #     2000,
        #     catalyst_2="protein_s",
        #     multiplier=2000,
        # )
        # self.catalyze("tFPI", "factor7a", "dummy", 2000)
        # self.catalyze("tFPI", "factor10a", "dummy", 2000)
        # self.catalyze("c1_esterase_inhibitor", "factor11a", "dummy", 2000)
        # self.catalyze("c1_esterase_inhibitor", "factor12a", "dummy", 2000)
        # self.catalyze("antithrombin3", "thrombin", "dummy", 2000)
        # self.catalyze("antithrombin3", "factor10a", "dummy", 2000)
        # self.catalyze("antithrombin3", "factor9a", "dummy", 2000)

        self.current_time += 1

    def perform_reaction(self, source, destination, change):
        source_amount = getattr(self, source)
        destination_amount = getattr(self, destination)
        setattr(self, source, source_amount - change)
        setattr(self, destination, destination_amount + change)

    def set_haemostasis_mode(self, prothrombotic: bool):
        self.tissue_factor = 100
        self.subendothelium = 100
        self.plasminogen = 10000
        self.a2A = 100
        self.injury_stage = 0
        if not prothrombotic:
            self.thrombomodulin = 100
            self.protein_s = 1000
            self.tFPI = 100
            self.antithrombin3 = 10000
            self.c1_esterase_inhibitor = 10000

    def increase_fibrinogen_level(self):
        self.fibrinogen += 1000

    def set_fibrinolysis_mode(self):
        self.current_time = 0
        self.plasminogen = 10000
        self.tPA = 100
        self.pAI1 = 0
        self.fibrinogen = 0
        self.cross_linked_fibrin = SIMULATION_END

    def set_disorder(self, text):
        match text.upper():
            case "LIVER DISORDER":
                self.prothrombin = 100
                self.factor7 = 10
                self.factor9 = 10
                self.factor10 = 10
                self.platelets = 100
            case "HAEMOPHILIA C":
                self.factor11 = 0
            case "HAEMOPHILIA B":
                self.factor9 = 0
            case "HAEMOPHILIA A (MODERATE)":
                self.factor8 = 500
            case "HAEMOPHILIA A (SEVERE)":
                self.factor8 = 0
            case "HYPOCALCAEMIA (MODERATE)":
                self.calcium_ions = 1.1
            case "HYPOCALCAEMIA (SEVERE)":
                self.calcium_ions = 0.9
            case _:
                pass
