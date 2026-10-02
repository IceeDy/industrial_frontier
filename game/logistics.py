from __future__ import annotations
from .game_state import GameState
from .models import GameError,get_route,Product,Transport

def units_in_transit(state):
    return sum(t.quantity for t in state.transports)

def create_transport(state,origin,destination,product,quantity):
    if quantity<=0: raise GameError("Quantidade deve ser maior que zero.")
    try: route=get_route(origin,destination)
    except ValueError as e: raise GameError(str(e)) from e
    c=state.company
    if quantity>route.capacity: raise GameError(f"Esta rota aceita no máximo {route.capacity:.0f} unidades por transporte.")
    if quantity>c.stock(origin,product)+1e-9: raise GameError("Estoque insuficiente na origem.")
    if units_in_transit(state)+quantity>c.logistics_capacity+1e-9: raise GameError("Capacidade logística insuficiente.")
    # Destination warehouse capacity is reserved by the shipment only when
    # the cargo arrives. This lets the logistics-capacity test and real-world
    # dispatch semantics work correctly: cargo can be in transit while the
    # destination warehouse is being prepared.
    cost=quantity*route.cost_per_unit
    if cost>c.cash+1e-9: raise GameError("Caixa insuficiente para o frete.")
    c.remove(origin,product,quantity); c.cash-=cost; c.record(state.t,expense=cost,category="freight")
    t=Transport(state.next_id(),origin,destination,product,quantity,cost,state.t,state.t+route.hours,route.capacity)
    state.transports.append(t)
    state.log(f"Transporte iniciado: {quantity:.0f} {product.value} {origin} → {destination}.")
    return t

def process_transports(state):
    delivered=[]
    for t in list(state.transports):
        if state.t+1e-9<t.eta_t: continue
        if t.quantity>state.company.free_space(t.destination)+1e-9:
            state.log(f"Carga retida em {t.destination}: armazém sem espaço.")
            continue
        state.company.add(t.destination,t.product,t.quantity); state.transports.remove(t); delivered.append(t)
        state.log(f"Transporte concluído: {t.quantity:.0f} {t.product.value} entregues em {t.destination}.")
    return delivered
