import pytest
from game.game_state import new_game
from game.models import Product,GameError
from game import industry,logistics,market
from game.simulation import advance_simulation
@pytest.fixture
def state(): return new_game(seed=1)
def test_mining(state): advance_simulation(state,1); assert state.company.stock("Marte",Product.IRON_ORE)==pytest.approx(100)
def test_refining(state):
    state.company.cash=50000; state.company.add("Marte",Product.IRON_ORE,100); industry.buy_facility(state,"refinery","Marte"); advance_simulation(state,1); assert state.company.stock("Marte",Product.IRON_ORE)==pytest.approx(50); assert state.company.stock("Marte",Product.REFINED_IRON)==pytest.approx(40)
def test_manufacturing(state):
    state.company.cash=100000; state.company.add("Marte",Product.REFINED_IRON,200); industry.buy_facility(state,"factory","Marte"); advance_simulation(state,1); assert state.company.stock("Marte",Product.REFINED_IRON)==pytest.approx(100); assert state.company.stock("Marte",Product.INDUSTRIAL_COMPONENT)==pytest.approx(10)
def test_market(state):
    cash=state.company.cash; market.buy(state,"Terra",Product.IRON_ORE,100); assert state.company.cash<cash; state.company.add("Marte",Product.IRON_ORE,100); cash=state.company.cash; market.sell(state,"Marte",Product.IRON_ORE,50); assert state.company.cash>cash
def test_transport(state):
    state.company.add("Marte",Product.REFINED_IRON,500); logistics.create_transport(state,"Marte","Terra",Product.REFINED_IRON,200); advance_simulation(state,25); assert state.company.stock("Terra",Product.REFINED_IRON)==pytest.approx(200); assert not state.transports
def test_logistics_capacity(state):
    state.company.add("Marte",Product.IRON_ORE,1000); logistics.create_transport(state,"Marte","Terra",Product.IRON_ORE,1000)
    with pytest.raises(GameError): logistics.create_transport(state,"Marte","Terra",Product.IRON_ORE,1)
def test_price_moves(state):
    m=state.markets[("Marte",Product.IRON_ORE)]; base=m.price; m.stock*=4; advance_simulation(state,.25); low=m.price; m.stock=m.target_stock/4; advance_simulation(state,.25); assert low<base and m.price>low
def test_time_history(state): advance_simulation(state,10); assert state.t==pytest.approx(10); assert state.history; assert state.company.produced[Product.IRON_ORE]>0
