from __future__ import annotations
from .game_state import GameState
from .models import FACILITY_SPECS,Facility,GameError,LOCATIONS,Product

def _facilities(state,kind):
    return [f for f in state.company.facilities if f.kind==kind and f.active]

def run_production(state,dt):
    reports=[]; c=state.company
    for f in _facilities(state,"mine"):
        qty=min(f.spec.rate_h*dt,c.free_space(f.location))
        if qty>0:
            c.add(f.location,Product.IRON_ORE,qty); f.produced+=qty; c.produced[Product.IRON_ORE]+=qty
            reports.append((f,Product.IRON_ORE,qty))
    for kind in ("refinery","factory","fuel_plant"):
        for f in _facilities(state,kind):
            recipe=f.spec.recipe
            if not recipe: continue
            cycles=f.spec.rate_h*dt
            cycles=min(cycles,*(c.stock(f.location,p)/q for p,q in recipe.inputs.items()))
            out=cycles*recipe.output_qty
            if out<=0 or out>c.free_space(f.location)+1e-9: continue
            for p,q in recipe.inputs.items(): c.remove(f.location,p,cycles*q)
            c.add(f.location,recipe.output,out); f.produced+=out; c.produced[recipe.output]+=out
            reports.append((f,recipe.output,out))
    return reports

def _pay(state,amount):
    if amount>state.company.cash+1e-9: raise GameError("Caixa insuficiente.")
    state.company.cash-=amount; state.company.record(state.t,expense=amount,category="capex")

def buy_facility(state,kind,location):
    if kind not in FACILITY_SPECS or location not in LOCATIONS: raise GameError("Instalação ou local inválido.")
    _pay(state,FACILITY_SPECS[kind].cost)
    f=Facility(state.next_id(),kind,location); state.company.facilities.append(f)
    state.log(f"{f.spec.name} construída em {location}.")
    return f

def buy_warehouse(state,location,amount=1000):
    if location not in LOCATIONS: raise GameError("Local inválido.")
    cost=amount*10; _pay(state,cost); state.company.warehouse_capacity[location]+=amount; state.company.infrastructure_value+=cost
    state.log(f"Armazém de {location} ampliado em {amount:.0f} unidades.")

def buy_logistics(state,amount=1000):
    cost=amount*5; _pay(state,cost); state.company.logistics_capacity+=amount; state.company.infrastructure_value+=cost
    state.log(f"Capacidade logística ampliada em {amount:.0f} unidades.")
