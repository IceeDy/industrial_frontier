from __future__ import annotations
import random
from collections import deque
from dataclasses import dataclass,field
from .models import Company,LOCATIONS,Product,Facility,Market,Transport
MARKET_SEED={
"Terra":{Product.IRON_ORE:(12,80),Product.REFINED_IRON:(30,60),Product.INDUSTRIAL_COMPONENT:(450,8),Product.FUEL:(75,35)},
"Lua":{Product.IRON_ORE:(9,120),Product.REFINED_IRON:(26,30),Product.INDUSTRIAL_COMPONENT:(420,4),Product.FUEL:(68,25)},
"Marte":{Product.IRON_ORE:(8,40),Product.REFINED_IRON:(34,50),Product.INDUSTRIAL_COMPONENT:(520,12),Product.FUEL:(92,18)}}
START_CAPACITY={"Terra":300.0,"Lua":300.0,"Marte":1000.0}
@dataclass
class GameState:
    company:Company
    markets:dict[tuple[str,Product],Market]
    t:float=0.0
    transports:list[Transport]=field(default_factory=list)
    events:deque=field(default_factory=lambda:deque(maxlen=500))
    history:list[dict]=field(default_factory=list)
    price_history:list[dict]=field(default_factory=list)
    rng:random.Random=field(default_factory=random.Random)
    next_id_value:int=10
    speed:float=5.0
    def next_id(self): self.next_id_value+=1; return self.next_id_value
    def log(self,message): self.events.appendleft((format_clock(self.t),message))
def format_clock(t):
    total=8*60+int(round(t*60)); day,minute=divmod(total,1440); return f"Dia {day+1} — {minute//60:02d}:{minute%60:02d}"
def new_game(seed=None):
    inventory={loc:{p:0.0 for p in Product} for loc in LOCATIONS}
    company=Company(10000.0,inventory,dict(START_CAPACITY),1000.0)
    company.facilities.append(Facility(1,"mine","Marte"))
    markets={}
    for loc,products in MARKET_SEED.items():
        for product,(price,demand) in products.items(): markets[(loc,product)]=Market(loc,product,price,demand,demand*24,price=price,npc_supply_h=demand*.95)
    state=GameState(company,markets,rng=random.Random(seed))
    state.log("Empresa fundada. Mina de ferro operando em Marte.")
    state.log("Objetivo: minério → refino → componentes → logística → mercado → expansão.")
    return state
