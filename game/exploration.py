"""Exploration and expansion actions for Industrial Frontier."""
from __future__ import annotations

from .game_state import MARKET_SEED
from .models import EXPANSION_LOCATIONS, GameError, Product, Market

SURVEY_COSTS = {"Ceres": 12_000}
COLONY_CAPACITY = 500.0


def survey_location(state, location: str) -> None:
    """Pay for a survey and unlock a new market/logistics destination."""
    company = state.company
    if location not in EXPANSION_LOCATIONS:
        raise GameError("Destino de exploração inválido.")
    if location in company.discovered_locations:
        raise GameError(f"{location} já foi explorado.")
    cost = SURVEY_COSTS[location]
    if company.cash < cost:
        raise GameError(f"Caixa insuficiente. A exploração de {location} custa ₡{cost:,.0f}.")
    # Build all destination data before charging so failures cannot partially
    # mutate the company state.
    market_data = MARKET_SEED[location]
    new_markets = {
        (location, product): Market(
            location=location,
            product=product,
            base_price=price,
            base_demand_h=demand,
            stock=demand * 24,
            price=price,
            npc_supply_h=demand * 0.95,
        )
        for product, (price, demand) in market_data.items()
    }
    company.cash -= cost
    company.record(state.t, expense=cost, category="exploration")
    company.discovered_locations.append(location)
    company.inventory[location] = {product: 0.0 for product in Product}
    company.warehouse_capacity[location] = COLONY_CAPACITY
    state.markets.update(new_markets)
    state.log(f"Expedição concluída: {location} mapeado. Mercado e entreposto logístico desbloqueados.")
