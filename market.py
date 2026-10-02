from __future__ import annotations

from .economy import price_for
from .game_state import GameState
from .models import MAX_STOCK_FACTOR, PRODUCT_NAMES, GameError, MarketEntry, money


def _entry(state: GameState, location: str, product: str) -> MarketEntry:
    try:
        return state.markets[(location, product)]
    except KeyError:
        raise GameError("Mercado inexistente.") from None


def _check_qty(quantity: float) -> None:
    if quantity <= 0:
        raise GameError("Quantidade deve ser maior que zero.")


def _log_price_move(state: GameState, e: MarketEntry, before: float) -> None:
    pct = (e.price / before - 1) * 100
    if abs(pct) >= 1:
        state.log(f"Preço de {PRODUCT_NAMES[e.product].lower()} em {e.location} "
                  f"{'subiu' if pct > 0 else 'caiu'} {abs(pct):.0f}%.")


def sell(state: GameState, location: str, product: str, quantity: float) -> float:
    """Vende do estoque da empresa para o mercado local. Retorna a receita."""
    _check_qty(quantity)
    c, e = state.company, _entry(state, location, product)
    if quantity > c.stock(location, product) + 1e-9:
        raise GameError(f"Estoque insuficiente em {location}: {c.stock(location, product):.0f} un.")
    room = e.target_stock * MAX_STOCK_FACTOR - e.stock
    if quantity > room:
        raise GameError(f"Mercado saturado em {location}: só absorve mais {max(room, 0):.0f} un.")
    before, after = e.price, price_for(e, e.stock + quantity)
    revenue = quantity * (before + after) / 2
    c.remove(location, product, quantity)
    e.stock += quantity
    e.price = after
    c.cash += revenue
    c.record(state.t, revenue=revenue)
    state.log(f"Venda de {quantity:.0f} {PRODUCT_NAMES[product].lower()} em {location}: {money(revenue)}.")
    _log_price_move(state, e, before)
    return revenue


def buy(state: GameState, location: str, product: str, quantity: float) -> float:
    """Compra da oferta do mercado local. Retorna o custo."""
    _check_qty(quantity)
    c, e = state.company, _entry(state, location, product)
    if quantity > e.stock - 1:
        raise GameError(f"Oferta insuficiente em {location}: {max(e.stock - 1, 0):.0f} un.")
    if quantity > c.free_space(location) + 1e-9:
        raise GameError(f"Armazém de {location} sem espaço: {c.free_space(location):.0f} un. livres.")
    before, after = e.price, price_for(e, e.stock - quantity)
    cost = quantity * (before + after) / 2
    if cost > c.cash:
        raise GameError(f"Caixa insuficiente: custo {money(cost)}, caixa {money(c.cash)}.")
    c.cash -= cost
    c.add(location, product, quantity)
    e.stock -= quantity
    e.price = after
    c.record(state.t, cost=cost)
    state.log(f"Compra de {quantity:.0f} {PRODUCT_NAMES[product].lower()} em {location}: {money(cost)}.")
    _log_price_move(state, e, before)
    return cost
