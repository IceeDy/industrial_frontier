from __future__ import annotations
from .economy import calculate_price
from .game_state import GameState
from .models import GameError

def _market(state,location,product):
    try: return state.markets[(location,product)]
    except KeyError as e: raise GameError("Mercado inexistente.") from e
def buy(state,location,product,quantity):
    if quantity<=0: raise GameError("Quantidade inválida.")
    m=_market(state,location,product); c=state.company; quantity=min(quantity,m.stock)
    if quantity<=0: raise GameError("Mercado sem oferta.")
    if quantity>c.free_space(location): raise GameError("Armazém sem espaço.")
    before=m.price; old=m.stock; m.stock-=quantity; after=calculate_price(m); m.stock=old; cost=quantity*(before+after)/2
    if cost>c.cash: raise GameError("Caixa insuficiente.")
    c.cash-=cost; c.add(location,product,quantity); m.stock=old-quantity; m.price=after; c.record(state.t,expense=cost,category="market_buy"); state.log(f"Compra: {quantity:.0f} {product.value} em {location} por ₡{cost:,.0f}."); return cost
def sell(state,location,product,quantity):
    if quantity<=0: raise GameError("Quantidade inválida.")
    m=_market(state,location,product); c=state.company
    if quantity>c.stock(location,product): raise GameError("Estoque insuficiente.")
    max_sell=max(0,m.target_stock*3-m.stock)
    if quantity>max_sell+1e-9: raise GameError(f"Mercado absorve no máximo {max_sell:.0f} unidades agora.")
    before=m.price; m.stock+=quantity; after=calculate_price(m); m.stock-=quantity; revenue=quantity*(before+after)/2
    c.remove(location,product,quantity); c.cash+=revenue; m.stock+=quantity; m.price=after; c.record(state.t,revenue=revenue,category="market_sell"); state.log(f"Venda: {quantity:.0f} {product.value} em {location} por ₡{revenue:,.0f}."); return revenue
