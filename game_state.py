from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field
from typing import Callable

from .models import (COMPONENTS, LOCATIONS, ORE, PRODUCTS, REFINED, START_CASH, START_MINE_VALUE,
                     TARGET_COVER_H, Company, Facility, MarketEntry, Transport)

# (preço base, demanda base/h) por local e produto
MARKET_SEED = {
    "Terra": {ORE: (12, 80), REFINED: (30, 60), COMPONENTS: (450, 8)},
    "Lua": {ORE: (9, 120), REFINED: (26, 30), COMPONENTS: (420, 4)},
    "Marte": {ORE: (8, 40), REFINED: (34, 50), COMPONENTS: (520, 12)},
}
START_CAPACITY = {"Terra": 300.0, "Lua": 300.0, "Marte": 1000.0}


def format_clock(t: float) -> str:
    minutes = int(round(8 * 60 + t * 60))
    return f"Dia {minutes // 1440 + 1} — {minutes % 1440 // 60:02d}:{minutes % 60:02d}"


@dataclass
class GameState:
    company: Company
    markets: dict[tuple[str, str], MarketEntry]
    t: float = 0.0  # horas desde o início (Dia 1 — 08:00)
    transports: list[Transport] = field(default_factory=list)
    events: deque = field(default_factory=lambda: deque(maxlen=300))
    history: list[dict] = field(default_factory=list)
    price_history: list[dict] = field(default_factory=list)
    hooks: list[Callable[["GameState"], None]] = field(default_factory=list)  # automação futura
    rng: random.Random = field(default_factory=random.Random)
    _next_id: int = 1

    def next_id(self) -> int:
        self._next_id += 1
        return self._next_id

    def log(self, message: str) -> None:
        self.events.appendleft((format_clock(self.t), message))


def new_game(seed: int | None = None) -> GameState:
    company = Company(
        cash=START_CASH,
        inventory={loc: {p: 0.0 for p in PRODUCTS} for loc in LOCATIONS},
        capacity=dict(START_CAPACITY),
        logistics_capacity=1000.0,
    )
    company.facilities.append(Facility(id=1, kind="mine", location="Marte", value=START_MINE_VALUE))
    markets = {
        (loc, p): MarketEntry(loc, p, base_price=price, base_demand=demand,
                              stock=demand * TARGET_COVER_H, price=price)
        for loc, items in MARKET_SEED.items() for p, (price, demand) in items.items()
    }
    state = GameState(company=company, markets=markets, rng=random.Random(seed))
    state.log("Empresa fundada. Mina de ferro operando em Marte.")
    return state
