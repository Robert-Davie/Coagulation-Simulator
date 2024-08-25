from simulation_variables import SimulationVariables


def test_catalyze_1():
    simVars = SimulationVariables()
    simVars.factor10a = 100
    simVars.catalyze(
        catalyst="factor10a", source="prothrombin", destination="thrombin", factor=10
    )
    assert simVars.thrombin > 0


def test_catalyze_2():
    simVars = SimulationVariables()
    simVars.prothrombin = 100
    simVars.factor10a = 100
    simVars.catalyze(
        catalyst="factor10a", source="prothrombin", destination="thrombin", factor=10
    )
    assert simVars.prothrombin < 100


def test_haemostasis_1():
    simVars = SimulationVariables()
    simVars.set_haemostasis_mode(prothrombotic=True)
    for i in range(2000):
        simVars.time_passes()
    assert simVars.prothrombin < 1
