from __future__ import annotations
from . import economy,industry,logistics
from .game_state import GameState
from .models import Product
STEP_HOURS=.25
def _upkeep(state,dt):
    cost=sum(f.spec.upkeep_h for f in state.company.facilities if f.active)*dt; state.company.cash-=cost; state.company.record(state.t,expense=cost,category="upkeep")
def finance_summary(state):
    c=state.company; inventory=sum(q*state.markets[(loc,p)].price for loc,items in c.inventory.items() for p,q in items.items()); cargo=sum(t.quantity*state.markets[(t.destination,t.product)].price for t in state.transports); facilities=sum(f.spec.cost for f in c.facilities if f.active); assets=inventory+cargo+facilities+c.infrastructure_value; window=min(max(state.t,1),24); rev=sum(x[1] for x in c.ledger if x[0]>state.t-window)/window; costs=sum(x[2] for x in c.ledger if x[0]>state.t-window)/window
    return {"cash":c.cash,"assets":assets,"revenue_h":rev,"cost_h":costs,"profit_h":rev-costs,"value":c.cash+assets}
def _snapshot(state):
    f=finance_summary(state); state.history.append({"Hora":round(state.t,2),"Caixa":f["cash"],"Valor da empresa":f["value"],**{p.value:state.company.produced[p] for p in Product}})
    for (loc,p),m in state.markets.items(): state.price_history.append({"Hora":round(state.t,2),"Local":loc,"Produto":p.value,"Preço":m.price})
    state.history=state.history[-1000:]; state.price_history=state.price_history[-5000:]
def advance_simulation(state,hours):
    if hours<0: raise ValueError("O tempo não pode ser negativo.")
    remaining=hours
    while remaining>1e-9:
        dt=min(STEP_HOURS,remaining); remaining-=dt; state.t+=dt; industry.run_production(state,dt); logistics.process_transports(state); economy.update_markets(state,dt); _upkeep(state,dt)
        if abs(state.t-round(state.t))<1e-8: _snapshot(state)
