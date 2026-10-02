from __future__ import annotations

import time

import pandas as pd
import plotly.express as px
import streamlit as st

from game import industry, logistics, market
from game.game_state import format_clock, new_game
from game.models import (LOCATIONS, LOGISTICS_COST, PRODUCT_NAMES, PRODUCTS, SPECS, WAREHOUSE_COST,
                         GameError, money)
from game.simulation import advance_simulation, finance_summary

st.set_page_config(page_title="Industrial Frontier", layout="wide")


def run_action(fn) -> None:
    """Executa uma ação de domínio, guarda o feedback e recarrega a tela."""
    try:
        st.session_state.flash = ("success", fn())
    except GameError as err:
        st.session_state.flash = ("error", str(err))
    st.rerun()


def product_select(label: str, key: str) -> str:
    return st.selectbox(label, PRODUCTS, format_func=PRODUCT_NAMES.get, key=key)


def corporation(state) -> None:
    f = finance_summary(state)
    cols = st.columns(6)
    for col, (label, value) in zip(cols, [("Caixa", f["cash"]), ("Ativos", f["assets"]), ("Receita/h", f["revenue_h"]),
                                          ("Custos/h", f["cost_h"]), ("Lucro/h", f["profit_h"]),
                                          ("Valor da empresa", f["value"])]):
        col.metric(label, money(value))
    if len(state.history) > 1:
        df = pd.DataFrame(state.history)
        left, right = st.columns(2)
        left.plotly_chart(px.line(df, x="Hora", y=["Caixa", "Valor da empresa"], title="Caixa e valor da empresa"))
        right.plotly_chart(px.line(df, x="Hora", y=[PRODUCT_NAMES[p] for p in PRODUCTS],
                                   title="Produção acumulada"))
    else:
        st.info("Os gráficos aparecem após a primeira hora de simulação.")


def operations(state) -> None:
    c = state.company
    counts = {k: sum(1 for x in c.facilities if x.kind == k) for k in SPECS}
    cols = st.columns(4)
    cols[0].metric("Minas", counts["mine"])
    cols[1].metric("Refinarias", counts["refinery"])
    cols[2].metric("Fábricas", counts["factory"])
    cols[3].metric("Transportes ativos", len(state.transports))
    st.subheader("Expansão")
    loc = st.selectbox("Local da instalação / armazém", LOCATIONS, index=2, key="build_loc")
    options = [
        ("Refinaria", SPECS["refinery"].cost, lambda: (industry.buy_facility(state, "refinery", loc), f"Refinaria construída em {loc}.")[1]),
        ("Fábrica", SPECS["factory"].cost, lambda: (industry.buy_facility(state, "factory", loc), f"Fábrica construída em {loc}.")[1]),
        ("Segunda mina", SPECS["mine"].cost, lambda: (industry.buy_facility(state, "mine", loc), f"Mina construída em {loc}.")[1]),
        ("Armazém maior (+1.000)", WAREHOUSE_COST, lambda: (industry.buy_warehouse(state, loc), f"Armazém de {loc} ampliado.")[1]),
        ("Capacidade logística (+1.000)", LOGISTICS_COST, lambda: (industry.buy_logistics(state), "Capacidade logística ampliada.")[1]),
    ]
    for col, (label, cost, action) in zip(st.columns(5), options):
        if col.button(f"{label} — {money(cost)}", key=f"buy_{label}", disabled=c.cash < cost):
            run_action(action)


def market_tab(state) -> None:
    rows = [{"Produto": PRODUCT_NAMES[p], "Local": loc, "Preço": round(e.price, 2),
             "Oferta (estoque)": round(e.stock), "Demanda (un/h)": round(e.demand, 1)}
            for (loc, p), e in state.markets.items()]
    st.dataframe(pd.DataFrame(rows), hide_index=True)
    st.subheader("Ordem de mercado")
    a, b, q = st.columns(3)
    loc = a.selectbox("Local", LOCATIONS, key="trade_loc")
    prod = b.selectbox("Produto", PRODUCTS, format_func=PRODUCT_NAMES.get, key="trade_prod")
    qty = q.number_input("Quantidade", min_value=1, value=100, step=10, key="trade_qty")
    e = state.markets[(loc, prod)]
    st.caption(f"Preço atual: {e.price:.2f} · Em estoque: {state.company.stock(loc, prod):.0f} · "
               f"Espaço livre: {state.company.free_space(loc):.0f}")
    buy_col, sell_col, _ = st.columns([1, 1, 4])
    if buy_col.button("BUY"):
        run_action(lambda: f"Compra concluída: {money(market.buy(state, loc, prod, qty))}.")
    if sell_col.button("SELL"):
        run_action(lambda: f"Venda concluída: {money(market.sell(state, loc, prod, qty))}.")
    if state.price_history:
        fig = px.line(pd.DataFrame(state.price_history), x="Hora", y="Preço", color="Local",
                      facet_row="Produto", height=600, title="Preços ao longo do tempo")
        fig.update_yaxes(matches=None)
        st.plotly_chart(fig)


def inventory_tab(state) -> None:
    c = state.company
    rows = [{"Local": loc, "Produto": PRODUCT_NAMES[p], "Quantidade": round(c.stock(loc, p)),
             "Capacidade do armazém": round(c.capacity[loc])} for loc in LOCATIONS for p in PRODUCTS]
    st.dataframe(pd.DataFrame(rows), hide_index=True)


def logistics_tab(state) -> None:
    st.caption(f"Capacidade logística: {logistics.units_in_transit(state):.0f} / "
               f"{state.company.logistics_capacity:.0f} em uso")
    a, b, c_, d = st.columns(4)
    origin = a.selectbox("Origem", LOCATIONS, index=2, key="lg_o")
    dest = b.selectbox("Destino", LOCATIONS, index=0, key="lg_d")
    prod = c_.selectbox("Carga", PRODUCTS, format_func=PRODUCT_NAMES.get, key="lg_p")
    qty = d.number_input("Quantidade", min_value=1, value=500, step=50, key="lg_q")
    if st.button("Criar transporte"):
        run_action(lambda: (logistics.create_transport(state, origin, dest, prod, qty), "Transporte iniciado.")[1])
    rows = [{"Origem": t.origin, "Destino": t.destination, "Carga": PRODUCT_NAMES[t.product],
             "Quantidade": round(t.quantity), "Progresso": t.progress(state.t), "ETA": format_clock(t.eta_t),
             "Custo": money(t.cost)} for t in state.transports]
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True,
                     column_config={"Progresso": st.column_config.ProgressColumn(min_value=0, max_value=1)})
    else:
        st.info("Nenhum transporte ativo.")


def industry_tab(state) -> None:
    rows = [{"Instalação": f.label, "Local": f.location, "Receita": f.spec.recipe,
             "Capacidade/h": f.spec.rate, "Manutenção/h": money(f.spec.upkeep),
             "Produzido (total)": round(f.produced)} for f in state.company.facilities]
    st.dataframe(pd.DataFrame(rows), hide_index=True)


def log_tab(state) -> None:
    st.dataframe(pd.DataFrame(list(state.events), columns=["Quando", "Evento"]), hide_index=True)


def main() -> None:
    if "state" not in st.session_state:
        st.session_state.state = new_game()
        st.session_state.last_real = time.time()
    state = st.session_state.state

    now = time.time()
    elapsed = min(now - st.session_state.last_real, 600)
    st.session_state.last_real = now
    speed = st.session_state.get("speed", 5)  # minutos de jogo por segundo real
    advance_simulation(state, elapsed * speed / 60)

    with st.sidebar:
        st.title("Industrial Frontier")
        st.subheader(format_clock(state.t))
        st.slider("Velocidade (min de jogo / s)", 0, 30, 5, key="speed", help="0 = pausado")
        st.toggle("Atualização automática", value=True, key="auto")
        for label, hours in (("+1h", 1), ("+6h", 6), ("+24h", 24)):
            if st.button(label, key=f"adv_{hours}"):
                advance_simulation(state, hours)
                st.rerun()
        if st.button("Reiniciar jogo"):
            del st.session_state["state"]
            st.rerun()

    if "flash" in st.session_state:
        kind, msg = st.session_state.pop("flash")
        (st.success if kind == "success" else st.error)(msg)

    names = ["Corporation", "Operations", "Market", "Inventory", "Logistics", "Industry", "Events / Log"]
    for tab, fn in zip(st.tabs(names), [corporation, operations, market_tab, inventory_tab,
                                        logistics_tab, industry_tab, log_tab]):
        with tab:
            fn(state)

    if st.session_state.get("auto", True) and speed > 0:
        time.sleep(2)
        st.rerun()


main()
