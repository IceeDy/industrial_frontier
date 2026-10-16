from __future__ import annotations

from .game_state import GameState
from .models import FACILITY_SPECS, Facility, GameError, LOCATIONS, Product


def _facilities(state, kind):
    return [
        facility
        for facility in state.company.facilities
        if facility.kind == kind and facility.active
    ]


def run_production(state, dt):
    reports = []
    company = state.company
    for facility in _facilities(state, "mine"):
        quantity = min(
            facility.spec.rate_h * dt,
            company.free_space(facility.location),
        )
        if quantity > 0:
            company.add(facility.location, Product.IRON_ORE, quantity)
            facility.produced += quantity
            company.produced[Product.IRON_ORE] += quantity
            reports.append((facility, Product.IRON_ORE, quantity))
    for kind in ("refinery", "factory", "fuel_plant"):
        for facility in _facilities(state, kind):
            recipe = facility.spec.recipe
            if not recipe:
                continue
            cycles = facility.spec.rate_h * dt
            cycles = min(
                cycles,
                *(company.stock(facility.location, product) / quantity
                  for product, quantity in recipe.inputs.items()),
            )
            output = cycles * recipe.output_qty
            if output <= 0 or output > company.free_space(facility.location) + 1e-9:
                continue
            for product, quantity in recipe.inputs.items():
                company.remove(facility.location, product, cycles * quantity)
            company.add(facility.location, recipe.output, output)
            facility.produced += output
            company.produced[recipe.output] += output
            reports.append((facility, recipe.output, output))
    return reports


def _pay(state, amount):
    if amount < 0:
        raise GameError("O valor da compra não pode ser negativo.")
    if amount > state.company.cash + 1e-9:
        raise GameError("Caixa insuficiente.")
    state.company.cash -= amount
    state.company.record(state.t, expense=amount, category="capex")


def buy_facility(state, kind, location):
    if kind not in FACILITY_SPECS or location not in state.company.discovered_locations:
        raise GameError("Instalação ou local inválido.")
    _pay(state, FACILITY_SPECS[kind].cost)
    facility = Facility(state.next_id(), kind, location)
    state.company.facilities.append(facility)
    # Facility value is calculated from active facilities in finance_summary.
    # Do not also add its purchase price to infrastructure_value.
    state.log(f"{facility.spec.name} construída em {location}.")
    return facility


def buy_warehouse(state, location, amount=1000):
    if location not in state.company.discovered_locations:
        raise GameError("Local inválido.")
    if amount <= 0:
        raise GameError("A expansão do armazém deve ser maior que zero.")
    cost = amount * 10
    _pay(state, cost)
    state.company.warehouse_capacity[location] += amount
    state.company.infrastructure_value += cost
    state.log(f"Armazém de {location} ampliado em {amount:.0f} unidades.")


def buy_logistics(state, amount=1000):
    if amount <= 0:
        raise GameError("A expansão logística deve ser maior que zero.")
    cost = amount * 5
    _pay(state, cost)
    state.company.logistics_capacity += amount
    state.company.infrastructure_value += cost
    state.log(f"Capacidade logística ampliada em {amount:.0f} unidades.")
