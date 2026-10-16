from __future__ import annotations

from . import economy, industry, logistics
from .game_state import GameState
from .models import Product

STEP_HOURS = 0.25


def _upkeep(state: GameState, dt: float) -> None:
    """Charge maintenance; deactivate facilities if the company cannot pay."""
    company = state.company
    for facility in company.facilities:
        if not facility.active:
            continue
        cost = facility.spec.upkeep_h * dt
        if cost > company.cash + 1e-9:
            facility.active = False
            state.log(
                f"{facility.spec.name} em {facility.location} desativada: "
                "caixa insuficiente para manutenção."
            )
            continue
        company.cash -= cost
        company.record(state.t, expense=cost, category="upkeep")


def finance_summary(state: GameState) -> dict[str, float]:
    company = state.company
    inventory = sum(
        quantity * state.markets[(location, product)].price
        for location, items in company.inventory.items()
        for product, quantity in items.items()
    )
    cargo = sum(
        transport.quantity
        * state.markets[(transport.destination, transport.product)].price
        for transport in state.transports
    )
    facilities = sum(
        facility.spec.cost
        for facility in company.facilities
        if facility.active
    )
    # infrastructure_value tracks warehouse/logistics upgrades. Facility
    # purchase costs are represented by facilities, not both fields.
    assets = inventory + cargo + facilities + company.infrastructure_value
    window = min(max(state.t, 1), 24)
    revenue = sum(
        entry[1] for entry in company.ledger if entry[0] > state.t - window
    ) / window
    costs = sum(
        entry[2] for entry in company.ledger if entry[0] > state.t - window
    ) / window
    return {
        "cash": company.cash,
        "assets": assets,
        "revenue_h": revenue,
        "cost_h": costs,
        "profit_h": revenue - costs,
        "value": company.cash + assets,
    }


def _snapshot(state: GameState) -> None:
    finance = finance_summary(state)
    state.history.append(
        {
            "Hora": round(state.t, 2),
            "Caixa": finance["cash"],
            "Valor da empresa": finance["value"],
            **{product.value: state.company.produced[product] for product in Product},
        }
    )
    for (location, product), market in state.markets.items():
        state.price_history.append(
            {
                "Hora": round(state.t, 2),
                "Local": location,
                "Produto": product.value,
                "Preço": market.price,
            }
        )
    state.history = state.history[-1000:]
    state.price_history = state.price_history[-5000:]


def advance_simulation(state: GameState, hours: float) -> None:
    if hours < 0:
        raise ValueError("O tempo não pode ser negativo.")
    remaining = hours
    while remaining > 1e-9:
        dt = min(STEP_HOURS, remaining)
        remaining -= dt
        state.t += dt
        industry.run_production(state, dt)
        logistics.process_transports(state)
        economy.update_markets(state, dt)
        _upkeep(state, dt)
        if abs(state.t - round(state.t)) < 1e-8:
            _snapshot(state)
