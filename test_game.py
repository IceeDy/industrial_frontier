import pytest

from game import economy, industry, logistics, market
from game.game_state import new_game
from game.models import COMPONENTS, ORE, REFINED, GameError
from game.simulation import advance_simulation


@pytest.fixture
def state():
    return new_game(seed=1)


def test_mine_generates_resources(state):
    industry.run_mines(state, 1.0)
    assert state.company.stock("Marte", ORE) == pytest.approx(100)


def test_refinery_consumes_ore(state):
    state.company.add("Marte", ORE, 100)
    industry.buy_facility(state, "refinery", "Marte")
    industry.run_refineries(state, 1.0)
    assert state.company.stock("Marte", ORE) == pytest.approx(50)
    assert state.company.stock("Marte", REFINED) == pytest.approx(40)


def test_factory_consumes_material(state):
    state.company.cash = 50_000
    state.company.add("Marte", REFINED, 200)
    industry.buy_facility(state, "factory", "Marte")
    industry.run_factories(state, 1.0)
    assert state.company.stock("Marte", REFINED) == pytest.approx(100)
    assert state.company.stock("Marte", COMPONENTS) == pytest.approx(10)


def test_sell_increases_cash(state):
    state.company.add("Marte", ORE, 100)
    cash = state.company.cash
    assert market.sell(state, "Marte", ORE, 50) > 0
    assert state.company.cash > cash


def test_buy_reduces_cash(state):
    cash = state.company.cash
    market.buy(state, "Terra", ORE, 100)
    assert state.company.cash < cash
    assert state.company.stock("Terra", ORE) == 100


def test_inventory_is_respected(state):
    with pytest.raises(GameError):
        market.sell(state, "Marte", ORE, 10)
    with pytest.raises(GameError):
        logistics.create_transport(state, "Marte", "Terra", REFINED, 10)


def test_transport_removes_cargo_from_origin(state):
    state.company.add("Marte", REFINED, 500)
    cash = state.company.cash
    logistics.create_transport(state, "Marte", "Terra", REFINED, 200)
    assert state.company.stock("Marte", REFINED) == 300
    assert state.company.cash == cash - 2000
    assert len(state.transports) == 1


def test_transport_delivers_cargo(state):
    state.company.add("Marte", REFINED, 500)
    logistics.create_transport(state, "Marte", "Terra", REFINED, 200)
    advance_simulation(state, 25)
    assert state.company.stock("Terra", REFINED) == pytest.approx(200)
    assert not state.transports


def test_supply_and_demand_move_price(state):
    e = state.markets[("Marte", ORE)]
    base = e.price
    e.stock *= 4
    assert economy.price_for(e) < base
    e.stock = e.target_stock / 4
    assert economy.price_for(e) > base
    e.stock = e.target_stock
    e.demand_mult = 2.0  # mais demanda, mesmo estoque -> preço sobe
    assert economy.price_for(e) > base


def test_time_advance_processes_operations(state):
    industry.buy_facility(state, "refinery", "Marte")
    advance_simulation(state, 10)
    assert state.t == pytest.approx(10)
    assert state.company.produced[ORE] > 0
    assert state.company.produced[REFINED] > 0
    assert state.company.cash < 5000  # manutenção descontada
    assert state.history
