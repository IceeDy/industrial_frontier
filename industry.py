from __future__ import annotations

from .game_state import GameState
from .models import (COMPONENTS, FACTORY_INPUT, LOCATIONS, LOGISTICS_COST, LOGISTICS_SIZE, ORE, REFINED,
                     REFINERY_RATIO, SPECS, WAREHOUSE_COST, WAREHOUSE_SIZE, Facility, GameError)

Report = tuple[Facility, str, float]  # (instalação, produto, quantidade produzida)


def _facilities(state: GameState, kind: str) -> list[Facility]:
    return [f for f in state.company.facilities if f.kind == kind]


def run_mines(state: GameState, dt: float) -> list[Report]:
    c, reports = state.company, []
    for f in _facilities(state, "mine"):
        amount = min(f.spec.rate * dt, c.free_space(f.location))
        if amount > 1e-9:
            c.add(f.location, ORE, amount)
            f.produced += amount
            c.produced[ORE] += amount
            reports.append((f, ORE, amount))
    return reports


def run_refineries(state: GameState, dt: float) -> list[Report]:
    c, reports = state.company, []
    for f in _facilities(state, "refinery"):
        ore_in = min(f.spec.rate * dt, c.stock(f.location, ORE))
        if ore_in > 1e-9:
            out = ore_in * REFINERY_RATIO
            c.remove(f.location, ORE, ore_in)
            c.add(f.location, REFINED, out)
            f.produced += out
            c.produced[REFINED] += out
            reports.append((f, REFINED, out))
    return reports


def run_factories(state: GameState, dt: float) -> list[Report]:
    c, reports = state.company, []
    for f in _facilities(state, "factory"):
        refined_in = min(f.spec.rate * FACTORY_INPUT * dt, c.stock(f.location, REFINED))
        if refined_in > 1e-9:
            out = refined_in / FACTORY_INPUT
            c.remove(f.location, REFINED, refined_in)
            c.add(f.location, COMPONENTS, out)
            f.produced += out
            c.produced[COMPONENTS] += out
            reports.append((f, COMPONENTS, out))
    return reports


def run_production(state: GameState, dt: float) -> list[Report]:
    return run_mines(state, dt) + run_refineries(state, dt) + run_factories(state, dt)


def _pay(state: GameState, cost: float) -> None:
    if cost > state.company.cash:
        raise GameError("Caixa insuficiente.")
    state.company.cash -= cost


def buy_facility(state: GameState, kind: str, location: str) -> Facility:
    if kind not in SPECS or location not in LOCATIONS:
        raise GameError("Instalação ou local inválido.")
    _pay(state, SPECS[kind].cost)
    facility = Facility(id=state.next_id(), kind=kind, location=location, value=SPECS[kind].cost)
    state.company.facilities.append(facility)
    state.log(f"{facility.label} construída em {location}.")
    return facility


def buy_warehouse(state: GameState, location: str) -> None:
    if location not in LOCATIONS:
        raise GameError("Local inválido.")
    _pay(state, WAREHOUSE_COST)
    state.company.capacity[location] += WAREHOUSE_SIZE
    state.company.infrastructure_value += WAREHOUSE_COST
    state.log(f"Armazém de {location} ampliado em {WAREHOUSE_SIZE:.0f} un.")


def buy_logistics(state: GameState) -> None:
    _pay(state, LOGISTICS_COST)
    state.company.logistics_capacity += LOGISTICS_SIZE
    state.company.infrastructure_value += LOGISTICS_COST
    state.log(f"Capacidade logística ampliada em {LOGISTICS_SIZE:.0f} un.")
