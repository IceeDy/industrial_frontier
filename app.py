from __future__ import annotations
import time
import pandas as pd
import plotly.express as px
import streamlit as st
from game.game_state import format_clock,new_game
from game.models import FACILITY_SPECS,LOCATIONS,PRODUCT_NAMES,Product,GameError,money
from game import industry,logistics,market
from game.simulation import advance_simulation,finance_summary
st.set_page_config(page_title="Industrial Frontier",page_icon="🚀",layout="wide")
def flash_action(fn):
    try: st.session_state.flash=("success",fn())
    except (GameError,ValueError) as e: st.session_state.flash=("error",str(e))
    st.rerun()
def fmt_product(p): return PRODUCT_NAMES[p]
def corporation(s):
    f=finance_summary(s); cols=st.columns(6)
    for col,(name,val) in zip(cols,[("Caixa",f["cash"]),("Ativos",f["assets"]),("Receita/h",f["revenue_h"]),("Custos/h",f["cost_h"]),("Lucro/h",f["profit_h"]),("Valor",f["value"])]): col.metric(name,money(val))
    if s.history:
        df=pd.DataFrame(s.history)
        st.plotly_chart(px.line(df,x="Hora",y=["Caixa","Valor da empresa"],title="Evolução financeira"),use_container_width=True)
        st.plotly_chart(px.line(df,x="Hora",y=[p.value for p in Product],title="Produção acumulada"),use_container_width=True)
def operations(s):
    counts={k:sum(f.kind==k for f in s.company.facilities) for k in FACILITY_SPECS}; cols=st.columns(4)
    for col,k in zip(cols,("mine","refinery","factory","fuel_plant")): col.metric(FACILITY_SPECS[k].name,counts[k])
    st.subheader("Construção"); loc=st.selectbox("Local",LOCATIONS,index=2,key="build_loc")
    for k,spec in FACILITY_SPECS.items():
        if st.button(f"Construir {spec.name} — {money(spec.cost)}",key=f"build_{k}",disabled=s.company.cash<spec.cost): flash_action(lambda k=k:f"{industry.buy_facility(s,k,loc).spec.name} construída em {loc}.")
    if st.button("Expandir armazém +1.000 — ₡10.000",disabled=s.company.cash<10000): flash_action(lambda:(industry.buy_warehouse(s,loc),"Armazém ampliado.")[1])
    if st.button("Expandir logística +1.000 — ₡5.000",disabled=s.company.cash<5000): flash_action(lambda:(industry.buy_logistics(s),"Logística ampliada.")[1])
def market_tab(s):
    rows=[{"Local":loc,"Produto":PRODUCT_NAMES[p],"Preço":round(m.price,2),"Oferta":round(m.stock),"Demanda/h":round(m.demand_h,1)} for (loc,p),m in s.markets.items()]
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
    st.subheader("Negociação"); a,b,c=st.columns(3)
    loc=a.selectbox("Local",LOCATIONS,key="trade_loc"); p=b.selectbox("Produto",list(Product),format_func=fmt_product,key="trade_prod"); qty=c.number_input("Quantidade",1,100000,100,10,key="trade_qty")
    st.caption(f"Preço {money(s.markets[(loc,p)].price)} · Seu estoque {s.company.stock(loc,p):.0f} · Espaço {s.company.free_space(loc):.0f}")
    x,y=st.columns(2)
    if x.button("COMPRAR",use_container_width=True): flash_action(lambda:f"Compra concluída: {money(market.buy(s,loc,p,qty))}.")
    if y.button("VENDER",use_container_width=True): flash_action(lambda:f"Venda concluída: {money(market.sell(s,loc,p,qty))}.")
    if s.price_history:
        df=pd.DataFrame(s.price_history); fig=px.line(df,x="Hora",y="Preço",color="Local",facet_row="Produto",height=650,title="Histórico de preços"); fig.update_yaxes(matches=None); st.plotly_chart(fig,use_container_width=True)
def inventory_tab(s):
    rows=[{"Local":loc,"Produto":PRODUCT_NAMES[p],"Quantidade":round(s.company.stock(loc,p),1),"Capacidade":round(s.company.warehouse_capacity[loc])} for loc in LOCATIONS for p in Product]
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
def logistics_tab(s):
    st.metric("Capacidade em trânsito",f"{logistics.units_in_transit(s):.0f} / {s.company.logistics_capacity:.0f}")
    a,b,c,d=st.columns(4); o=a.selectbox("Origem",LOCATIONS,index=2,key="lg_o"); dest=b.selectbox("Destino",LOCATIONS,index=0,key="lg_d"); p=c.selectbox("Carga",list(Product),format_func=fmt_product,key="lg_p"); q=d.number_input("Quantidade",1,100000,500,50,key="lg_q")
    if st.button("Enviar carga",use_container_width=True): flash_action(lambda:(logistics.create_transport(s,o,dest,p,q),"Transporte iniciado.")[1])
    rows=[{"Origem":t.origin,"Destino":t.destination,"Produto":PRODUCT_NAMES[t.product],"Qtd":round(t.quantity),"Progresso":t.progress(s.t),"ETA":format_clock(t.eta_t),"Frete":money(t.cost)} for t in s.transports]
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True) if rows else st.info("Nenhum transporte em andamento.")
def industry_tab(s):
    st.dataframe(pd.DataFrame([{"Instalação":f.spec.name,"Local":f.location,"Manutenção/h":money(f.spec.upkeep_h),"Produção":round(f.produced,1),"Ativa":f.active} for f in s.company.facilities]),hide_index=True,use_container_width=True)
def events_tab(s): st.dataframe(pd.DataFrame(list(s.events),columns=["Quando","Evento"]),hide_index=True,use_container_width=True)
def main():
    if "state" not in st.session_state: st.session_state.state=new_game(); st.session_state.last_real=time.time()
    s=st.session_state.state; now=time.time(); elapsed=min(now-st.session_state.last_real,600); st.session_state.last_real=now
    speed=st.sidebar.slider("Velocidade (min jogo/s)",0,60,5,key="speed"); s.speed=speed
    if speed: advance_simulation(s,elapsed*speed/60)
    with st.sidebar:
        st.title("🚀 Industrial Frontier"); st.subheader(format_clock(s.t)); st.caption("YOU DON'T FLY THE SHIP. YOU RUN THE COMPANY.")
        for label,h in (("+1h",1),("+6h",6),("+24h",24)):
            if st.button(label,use_container_width=True): advance_simulation(s,h); st.rerun()
        if st.button("Novo jogo",use_container_width=True): st.session_state.clear(); st.rerun()
    if "flash" in st.session_state:
        kind,msg=st.session_state.pop("flash"); (st.success if kind=="success" else st.error)(msg)
    tabs=st.tabs(["Corporation","Operations","Market","Inventory","Logistics","Industry","Events"])
    for tab,fn in zip(tabs,(corporation,operations,market_tab,inventory_tab,logistics_tab,industry_tab,events_tab)):
        with tab: fn(s)
    if speed>0: time.sleep(1.5); st.rerun()
main()
