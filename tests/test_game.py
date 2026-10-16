import pytest
from game.game_state import new_game
from game.models import Product, GameError
from game import industry, logistics, market
from game.simulation import advance_simulation, finance_summary
from game.persistence import dump_state, load_state


@pytest.fixture
def state():
    return new_game(seed=1)


def test_mining(state):
    advance_simulation(state, 1)
    assert state.company.stock("Marte", Product.IRON_ORE) == pytest.approx(100)


def test_refining(state):
    state.company.cash = 50000
    state.company.add("Marte", Product.IRON_ORE, 100)
    industry.buy_facility(state, "refinery", "Marte")
    advance_simulation(state, 1)
    assert state.company.stock("Marte", Product.IRON_ORE) == pytest.approx(0)
    assert state.company.stock("Marte", Product.REFINED_IRON) == pytest.approx(160)


def test_manufacturing(state):
    state.company.cash = 100000
    state.company.add("Marte", Product.REFINED_IRON, 200)
    industry.buy_facility(state, "factory", "Marte")
    advance_simulation(state, 1)
    assert state.company.stock("Marte", Product.REFINED_IRON) == pytest.approx(100)
    assert state.company.stock("Marte", Product.INDUSTRIAL_COMPONENT) == pytest.approx(10)


def test_market(state):
    cash = state.company.cash
    market.buy(state, "Terra", Product.IRON_ORE, 100)
    assert state.company.cash < cash
    state.company.add("Marte", Product.IRON_ORE, 100)
    cash = state.company.cash
    market.sell(state, "Marte", Product.IRON_ORE, 50)
    assert state.company.cash > cash


def test_transport(state):
    state.company.add("Marte", Product.REFINED_IRON, 200)
    logistics.create_transport(
        state, "Marte", "Terra", Product.REFINED_IRON, 200
    )
    advance_simulation(state, 25)
    assert state.company.stock("Terra", Product.REFINED_IRON) == pytest.approx(200)
    assert not state.transports


def test_logistics_capacity(state):
    # Isolate logistics capacity from the destination warehouse limit.
    state.company.warehouse_capacity["Terra"] = 5000
    state.company.add("Marte", Product.IRON_ORE, 1000)
    logistics.create_transport(state, "Marte", "Terra", Product.IRON_ORE, 1000)
    with pytest.raises(GameError):
        logistics.create_transport(state, "Marte", "Terra", Product.IRON_ORE, 1)


def test_price_moves(state):
    market_state = state.markets[("Marte", Product.IRON_ORE)]
    base = market_state.price
    market_state.stock *= 4
    advance_simulation(state, 0.25)
    low = market_state.price
    market_state.stock = market_state.target_stock / 4
    advance_simulation(state, 0.25)
    assert low < base and market_state.price > low


def test_time_history(state):
    advance_simulation(state, 10)
    assert state.t == pytest.approx(10)
    assert state.history
    assert state.company.produced[Product.IRON_ORE] > 0


def test_facility_not_double_counted_in_company_value(state):
    state.company.cash += 50000
    before = finance_summary(state)
    industry.buy_facility(state, "refinery", "Marte")
    after = finance_summary(state)
    # Purchase transfers cash into an asset; the facility value is represented once.
    assert after["value"] - before["value"] == pytest.approx(0)


def test_transport_rejects_unavailable_destination_space(state):
    state.company.add("Marte", Product.IRON_ORE, 500)
    state.company.warehouse_capacity["Terra"] = 100
    with pytest.raises(GameError, match="Espaço insuficiente"):
        logistics.create_transport(state, "Marte", "Terra", Product.IRON_ORE, 200)
    assert state.company.stock("Marte", Product.IRON_ORE) == pytest.approx(500)
    assert not state.transports


def test_unaffordable_upkeep_deactivates_facility(state):
    state.company.cash = 0
    advance_simulation(state, 0.25)
    assert not state.company.facilities[0].active
    assert state.company.cash == pytest.approx(0)



def test_save_load_round_trip_preserves_game_state(state):
    state.company.cash = 4321.5
    state.company.add("Marte", Product.IRON_ORE, 25)
    logistics.create_transport(state, "Marte", "Terra", Product.IRON_ORE, 10)
    advance_simulation(state, 2)
    restored = load_state(dump_state(state))

    assert restored.t == pytest.approx(state.t)
    assert restored.company.cash == pytest.approx(state.company.cash)
    assert restored.company.stock("Marte", Product.IRON_ORE) == pytest.approx(
        state.company.stock("Marte", Product.IRON_ORE)
    )
    assert restored.company.facilities[0].kind == state.company.facilities[0].kind
    assert restored.markets[("Marte", Product.IRON_ORE)].price == pytest.approx(
        state.markets[("Marte", Product.IRON_ORE)].price
    )
    assert len(restored.transports) == len(state.transports)
    assert list(restored.events) == list(state.events)
    assert restored.history == state.history
    assert restored.price_history == state.price_history


def test_save_load_preserves_random_generator(state):
    restored = load_state(dump_state(state))
    assert restored.rng.random() == pytest.approx(state.rng.random())


def test_save_load_rejects_invalid_json():
    with pytest.raises(ValueError, match="Não foi possível ler"):
        load_state("{not valid json")


def test_save_load_rejects_unsupported_version(state):
    import json

    data = json.loads(dump_state(state))
    data["version"] = 999
    with pytest.raises(ValueError, match="Versão de save não suportada"):
        load_state(json.dumps(data))
