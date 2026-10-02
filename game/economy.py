from __future__ import annotations
import math
from .models import Market
from .game_state import GameState
MIN_PRICE,MAX_PRICE=.25,4.0
def calculate_price(market):
    ratio=max(market.stock/max(market.target_stock,1.0),.01); pressure=ratio**-.60; demand_pressure=market.demand_mult**.35
    return max(market.base_price*MIN_PRICE,min(market.base_price*MAX_PRICE,market.base_price*pressure*demand_pressure))
def update_market(market,dt,rng):
    market.demand_mult=max(.35,min(2.8,market.demand_mult+(1-market.demand_mult)*min(1,.04*dt)+rng.gauss(0,market.volatility)*math.sqrt(max(dt,0))))
    event=None
    if rng.random()<.008*dt:
        factor=rng.choice((.65,1.5)); market.demand_mult=max(.35,min(2.8,market.demand_mult*factor)); event=f"Choque de demanda em {market.location}: {'alta' if factor>1 else 'baixa'} para {market.product.value}."
    consumption=min(market.stock,market.demand_h*dt); supply=market.npc_supply_h*dt*(.8+.4*rng.random()); market.stock=max(0,market.stock+ supply-consumption); market.price=calculate_price(market)
    return event
def update_markets(state,dt):
    for market in state.markets.values():
        event=update_market(market,dt,state.rng)
        if event: state.log(event)
