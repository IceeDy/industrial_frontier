from __future__ import annotations

import math
from typing import TYPE_CHECKING

from .models import PRODUCT_NAMES, MarketEntry

if TYPE_CHECKING:
    from .game_state import GameState

ELASTICITY = 0.6
MIN_MULT, MAX_MULT = 0.3, 3.0


def price_for(entry: MarketEntry, stock: float | None = None) -> float:
    """Mais estoque que o alvo -> preço cai; menos -> sobe. Alvo cresce com a demanda."""
    s = max(entry.stock if stock is None else stock, 1.0)
    mult = (s / entry.target_stock) ** -ELASTICITY
    return entry.base_price * min(max(mult, MIN_MULT), MAX_MULT)


def update_market(entry: MarketEntry, dt: float, rng) -> str | None:
    """Avança um mercado: demanda oscila, consumo e produção NPC mexem no estoque."""
    entry.demand_mult += (1 - entry.demand_mult) * min(1.0, 0.03 * dt) + rng.gauss(0, 0.02) * math.sqrt(dt)
    event = None
    if rng.random() < 0.01 * dt:
        factor = rng.choice((1.6, 0.6))
        entry.demand_mult *= factor
        event = (f"Demanda por {PRODUCT_NAMES[entry.product].lower()} em {entry.location} "
                 f"{'disparou' if factor > 1 else 'despencou'}.")
    entry.demand_mult = min(max(entry.demand_mult, 0.4), 2.5)
    supply = entry.base_demand * (entry.price / entry.base_price) ** 1.5 * dt
    consumption = min(entry.stock, entry.demand * dt)
    entry.stock = max(0.0, entry.stock + supply - consumption)
    entry.price = price_for(entry)
    return event


def update_markets(state: "GameState", dt: float) -> None:
    for entry in state.markets.values():
        event = update_market(entry, dt, state.rng)
        if event:
            state.log(event)
