from __future__ import annotations

from . import economy, industry, logistics
from .game_state import GameState
from .models import PRODUCT_NAMES, PRODUCTS

STEP_HOURS = 0.25
VERBS = {"mine": "produziu", "refinery": "refinou", "factory": "fabricou"}


def advance_simulation(state: GameState, hours: float) -> None:
    """Único ponto de passagem do tempo: produção, transportes, mercado, custos e estatísticas."""
    totals: dict[int, list] = {}
    remaining = hours
    while remaining > 1e-9:
        dt = min(STEP_HOURS, remaining)
        remaining -= dt
        previous_hour = int(state.t)
        state.t += dt
        for hook in state.hooks:  # ponto de extensão: automação / agentes / gerentes
            hook(state)
        for facility, product, amount in industry.run_production(state, dt):
            entry = totals.setdefault(facility.id, [facility, product, 0.0])
            entry[2] += amount
        logistics.process_transports(state)
        economy.update_markets(state, dt)
        _charge_upkeep(state, dt)
        if int(state.t) > previous_hour:
            _snapshot(state)
    for facility, product, amount in totals.values():
        state.log(f"{facility.label} de {facility.location} {VERBS[facility.kind]} "
                  f"{amount:.0f} {PRODUCT_NAMES[product].lower()}.")


def _charge_upkeep(state: GameState, dt: float) -> None:
    cost = sum(f.spec.upkeep for f in state.company.facilities) * dt
    state.company.cash -= cost
    state.company.record(state.t, cost=cost)


def finance_summary(state: GameState) -> dict[str, float]:
    c = state.company
    inventory = sum(q * state.markets[(loc, p)].price for loc, items in c.inventory.items() for p, q in items.items())
    cargo = sum(t.quantity * state.markets[(t.destination, t.product)].price for t in state.transports)
    assets = sum(f.value for f in c.facilities) + c.infrastructure_value + inventory + cargo
    window = min(max(state.t, 1.0), 24.0)
    revenue = sum(r for t, r, _ in c.ledger if t > state.t - window) / window
    costs = sum(k for t, _, k in c.ledger if t > state.t - window) / window
    return {"cash": c.cash, "assets": assets, "revenue_h": revenue, "cost_h": costs,
            "profit_h": revenue - costs, "value": c.cash + assets}


def _snapshot(state: GameState) -> None:
    hour, f = int(state.t), finance_summary(state)
    state.history.append({"Hora": hour, "Caixa": f["cash"], "Valor da empresa": f["value"],
                          **{PRODUCT_NAMES[p]: state.company.produced[p] for p in PRODUCTS}})
    for (loc, product), e in state.markets.items():
        state.price_history.append({"Hora": hour, "Local": loc, "Produto": PRODUCT_NAMES[product],
                                    "Preço": round(e.price, 2)})
    del state.history[:-2000], state.price_history[:-9000]
