from __future__ import annotations

from .game_state import GameState
from .models import GameError, get_route, Product, Transport


def units_in_transit(state):
    return sum(transport.quantity for transport in state.transports)


def _reserved_destination_space(state, destination):
    return sum(
        transport.quantity
        for transport in state.transports
        if transport.destination == destination
    )


def create_transport(state, origin, destination, product, quantity):
    if quantity <= 0:
        raise GameError("Quantidade deve ser maior que zero.")
    try:
        route = get_route(origin, destination)
    except ValueError as error:
        raise GameError(str(error)) from error
    company = state.company
    if quantity > route.capacity:
        raise GameError(
            f"Esta rota aceita no máximo {route.capacity:.0f} unidades por transporte."
        )
    if quantity > company.stock(origin, product) + 1e-9:
        raise GameError("Estoque insuficiente na origem.")
    if units_in_transit(state) + quantity > company.logistics_capacity + 1e-9:
        raise GameError("Capacidade logística insuficiente.")
    available_at_destination = (
        company.free_space(destination)
        - _reserved_destination_space(state, destination)
    )
    if quantity > available_at_destination + 1e-9:
        raise GameError(
            "Espaço insuficiente no armazém de destino, considerando cargas já enviadas."
        )
    cost = quantity * route.cost_per_unit
    if cost > company.cash + 1e-9:
        raise GameError("Caixa insuficiente para o frete.")

    # Validate all constraints before mutating state.
    company.remove(origin, product, quantity)
    company.cash -= cost
    company.record(state.t, expense=cost, category="freight")
    transport = Transport(
        state.next_id(),
        origin,
        destination,
        product,
        quantity,
        cost,
        state.t,
        state.t + route.hours,
        route.capacity,
    )
    state.transports.append(transport)
    state.log(
        f"Transporte iniciado: {quantity:.0f} {product.value} "
        f"{origin} → {destination}."
    )
    return transport


def process_transports(state):
    delivered = []
    for transport in list(state.transports):
        if state.t + 1e-9 < transport.eta_t:
            continue
        if transport.quantity > state.company.free_space(transport.destination) + 1e-9:
            # Protect older saves or manually modified states; do not delete cargo.
            state.log(
                f"Carga retida em {transport.destination}: armazém sem espaço."
            )
            continue
        state.company.add(
            transport.destination, transport.product, transport.quantity
        )
        state.transports.remove(transport)
        delivered.append(transport)
        state.log(
            f"Transporte concluído: {transport.quantity:.0f} "
            f"{transport.product.value} entregues em {transport.destination}."
        )
    return delivered
