import pytest

from simulation_variables import SimulationVariables, ReactionVariables


@pytest.fixture()
def reaction():
    return ReactionVariables(
        catalyst_amount=0,
        source_amount=0,
        divisor=1,
    )


@pytest.fixture()
def empty_simulation():
    simulation = SimulationVariables()
    simulation.clear()
    return simulation


def test_get_maximum_inhibitor_amount(reaction):
    reaction.inhibitor_2_amount = 2
    reaction.multiplier_i2 = 2.0
    assert reaction.get_maximum_inhibitor_amount() == pytest.approx(4)


def test_calcium_multiplier(reaction):
    reaction.calcium_ions = 0.9
    reaction.reaction_affected_by_calcium = True
    assert reaction.calcium_multiplier() == pytest.approx(0.42, 1e-2)


def test_get_maximum_catalyst_available(reaction):
    reaction.catalyst_amount = 3
    reaction.catalyst_2_amount = 2
    reaction.multiplier = 100
    assert reaction.get_maximum_catalyst_available() == 200


def test_reaction_too_small_to_occur(reaction):
    reaction.source_amount = 0.1
    reaction.tail = 100
    assert reaction.get_reaction_size() == pytest.approx(0)


def test_get_reaction_size(reaction):
    reaction.catalyst_amount = 10
    reaction.source_amount = 1000
    reaction.destination_amount = 0
    reaction.divisor = 5
    reaction.tail = 100
    assert reaction.get_reaction_size() == pytest.approx(2)


def test_perform_reaction(empty_simulation):
    simulation = empty_simulation
    simulation.factor10 = 100
    simulation.perform_reaction("factor10", "factor10a", 2)
    assert simulation.factor10 == pytest.approx(98)
    assert simulation.factor10a == pytest.approx(2)


def test_convert_factor12(empty_simulation):
    simulation = empty_simulation
    simulation.subendothelium = 100
    simulation.factor12 = 100
    simulation.convert_factor12()
    assert simulation.factor12 == pytest.approx(99)
    assert simulation.factor12a == pytest.approx(1)


def test_convert_factor11(empty_simulation):
    simulation = empty_simulation
    simulation.factor12a = 500
    simulation.factor11 = 100
    simulation.convert_factor11()
    assert simulation.factor11 == pytest.approx(99)
    assert simulation.factor11a == pytest.approx(1)


def test_convert_factor9(empty_simulation):
    simulation = empty_simulation
    simulation.factor11a = 20
    simulation.factor7a = 10
    simulation.factor9 = 100
    simulation.convert_factor9()
    assert simulation.factor9 == pytest.approx(99)
    assert simulation.factor9a == pytest.approx(1)


def test_convert_factor10_intrinsic(empty_simulation):
    simulation = empty_simulation
    simulation.factor9a = 50
    simulation.factor8a = 40
    simulation.factor10 = 100
    simulation.convert_factor10_intrinsic()
    assert simulation.factor10 == pytest.approx(99)
    assert simulation.factor10a == pytest.approx(1)


def test_convert_factor7(empty_simulation):
    simulation = empty_simulation
    simulation.tissue_factor = 500
    simulation.factor7 = 100
    simulation.convert_factor7()
    assert simulation.factor7 == pytest.approx(99.5)
    assert simulation.factor7a == pytest.approx(0.5)


def test_convert_factor10_extrinsic(empty_simulation):
    simulation = empty_simulation
    simulation.factor7a = 500
    simulation.factor10 = 100
    simulation.convert_factor10_extrinsic()
    assert simulation.factor10 == pytest.approx(99.5)
    assert simulation.factor10a == pytest.approx(0.5)


def test_convert_prothrombin(empty_simulation):
    simulation = empty_simulation
    simulation.factor10a = 200
    simulation.factor5a = 300
    simulation.tFPI = 20
    simulation.prothrombin = 1000
    simulation.convert_prothrombin()
    assert simulation.prothrombin == pytest.approx(992)
    assert simulation.thrombin == pytest.approx(8)


def test_thrombin_convert_factor11(empty_simulation):
    simulation = empty_simulation
    simulation.thrombin = 1000
    simulation.factor11 = 100
    simulation.thrombin_convert_factor11()
    assert simulation.factor11 == pytest.approx(99)
    assert simulation.factor11a == pytest.approx(1)


def test_thrombin_convert_factor8(empty_simulation):
    simulation = empty_simulation
    simulation.thrombin = 1000
    simulation.factor8 = 100
    simulation.thrombin_convert_factor8()
    assert simulation.factor8 == pytest.approx(99)
    assert simulation.factor8a == pytest.approx(1)


def test_thrombin_convert_factor7(empty_simulation):
    simulation = empty_simulation
    simulation.thrombin = 1000
    simulation.factor7 = 100
    simulation.thrombin_convert_factor7()
    assert simulation.factor7 == pytest.approx(99)
    assert simulation.factor7a == pytest.approx(1)


def test_convert_factor5(empty_simulation):
    simulation = empty_simulation
    simulation.thrombin = 100
    simulation.factor10a = 200
    simulation.factor5 = 1000
    simulation.convert_factor5()
    assert simulation.factor5 == pytest.approx(995)
    assert simulation.factor5a == pytest.approx(5)


def test_convert_fibrinogen(empty_simulation):
    simulation = empty_simulation
    simulation.thrombin = 150
    simulation.fibrinogen = 1000
    simulation.convert_fibrinogen()
    assert simulation.fibrinogen == pytest.approx(990)
    assert simulation.fibrin == pytest.approx(10)


def test_convert_factor13(empty_simulation):
    simulation = empty_simulation
    simulation.thrombin = 20
    simulation.factor13 = 1000
    simulation.convert_factor13()
    assert simulation.factor13 == pytest.approx(999)
    assert simulation.factor13a == pytest.approx(1)


def test_convert_fibrin(empty_simulation):
    simulation = empty_simulation
    simulation.factor13a = 50
    simulation.fibrin = 1000
    simulation.convert_fibrin()
    assert simulation.fibrin == pytest.approx(999)
    assert simulation.cross_linked_fibrin == pytest.approx(1)
