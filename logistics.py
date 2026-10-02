from __future__ import annotations

from .game_state import GameState
from .models import PRODUCT_NAMES, GameError, Transport, get_route, money


def units_in_transit(state: GameState, destination: str | None = None) -> float:
    return sum(t.quantity for t in state.transports if destination in (None, t.destination))


def free_logistics(state: GameState) -> float:
    return state.company.logistics_capacity - units_in_transit(state)


def create_transport(state: GameState, origin: str, destination: str, product: str, quantity: float) -> Transport:
    if quantity <= 0:
        raise GameError("Quantidade deve ser maior que zero.")
    route, c = get_route(origin, destination), state.company
    cost = quantity * route.cost_per_unit
    if quantity > c.stock(origin, product) + 1e-9:
        raise GameError(f"Estoque insuficiente em {origin}: {c.stock(origin, product):.0f} un.")
    if quantity > free_logistics(state) + 1e-9:
        raise GameError(f"Capacidade logística livre: {free_logistics(state):.0f} un.")
    if quantity > c.free_space(destination) - units_in_transit(state, destination) + 1e-9:
        raise GameError(f"Armazém de {destination} sem espaço para receber a carga.")
    if cost > c.cash:
        raise GameError(f"Caixa insuficiente: frete {money(cost)}.")
    c.remove(origin, product, quantity)
    c.cash -= cost
    c.record(state.t, cost=cost)
    transport = Transport(state.next_id(), origin, destination, product, quantity, cost,
                          state.t, state.t + route.hours)
    state.transports.append(transport)
    state.log(f"Transporte {origin} → {destination} iniciado: {quantity:.0f} {PRODUCT_NAMES[product].lower()}.")
    return transport


def process_transports(state: GameState) -> list[Transport]:
    delivered = []
    for t in list(state.transports):
        if state.t + 1e-9 >= t.eta_t and state.company.free_space(t.destination) + 1e-9 >= t.quantity:
            state.company.add(t.destination, t.product, t.quantity)
            state.transports.remove(t)
            delivered.append(t)
            state.log(f"Transporte {t.origin} → {t.destination} concluído: "
                      f"{t.quantity:.0f} {PRODUCT_NAMES[t.product].lower()} entregues.")
    return delivered
