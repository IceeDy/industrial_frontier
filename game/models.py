from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum

class Product(str, Enum):
    IRON_ORE = "iron_ore"
    REFINED_IRON = "refined_iron"
    INDUSTRIAL_COMPONENT = "industrial_component"
    FUEL = "fuel"

PRODUCT_NAMES = {
    Product.IRON_ORE: "Minério de ferro", Product.REFINED_IRON: "Ferro refinado",
    Product.INDUSTRIAL_COMPONENT: "Componentes industriais", Product.FUEL: "Combustível",
}
LOCATIONS = ("Terra", "Lua", "Marte")

@dataclass(frozen=True)
class Recipe:
    inputs: dict[Product, float]
    output: Product
    output_qty: float
    hours: float

@dataclass(frozen=True)
class FacilitySpec:
    name: str
    cost: float
    upkeep_h: float
    rate_h: float
    recipe: Recipe | None = None

FACILITY_SPECS = {
    "mine": FacilitySpec("Mina de ferro", 20_000, 40, 100),
    "refinery": FacilitySpec("Refinaria", 5_000, 60, 50, Recipe({Product.IRON_ORE: 10}, Product.REFINED_IRON, 8, 0.2)),
    "factory": FacilitySpec("Fábrica", 15_000, 120, 10, Recipe({Product.REFINED_IRON: 10}, Product.INDUSTRIAL_COMPONENT, 1, 1.0)),
    "fuel_plant": FacilitySpec("Planta de combustível", 25_000, 180, 8, Recipe({Product.IRON_ORE: 4}, Product.FUEL, 1, 0.5)),
}

@dataclass(frozen=True)
class Route:
    hours: float
    cost_per_unit: float
    capacity: float

ROUTES = {
    frozenset(("Terra", "Lua")): Route(6, 5, 1000),
    frozenset(("Terra", "Marte")): Route(24, 10, 1000),
    frozenset(("Lua", "Marte")): Route(18, 8, 1000),
}

def get_route(origin: str, destination: str) -> Route:
    if origin == destination or origin not in LOCATIONS or destination not in LOCATIONS:
        raise ValueError("Rota inválida.")
    try: return ROUTES[frozenset((origin, destination))]
    except KeyError as exc: raise ValueError("Rota inexistente.") from exc

def money(v: float) -> str: return f"₡{v:,.0f}".replace(",", ".")

@dataclass
class Facility:
    id: int
    kind: str
    location: str
    produced: float = 0.0
    active: bool = True
    @property
    def spec(self) -> FacilitySpec: return FACILITY_SPECS[self.kind]

@dataclass
class Transport:
    id: int
    origin: str
    destination: str
    product: Product
    quantity: float
    cost: float
    start_t: float
    eta_t: float
    capacity: float
    def progress(self, now: float) -> float:
        span=max(self.eta_t-self.start_t,1e-9); return max(0.0,min(1.0,(now-self.start_t)/span))

@dataclass
class Market:
    location: str
    product: Product
    base_price: float
    base_demand_h: float
    stock: float
    demand_mult: float = 1.0
    volatility: float = 0.02
    price: float = 0.0
    npc_supply_h: float = 0.0
    def __post_init__(self):
        if self.price<=0: self.price=self.base_price
    @property
    def demand_h(self): return self.base_demand_h*self.demand_mult
    @property
    def target_stock(self): return self.demand_h*24

@dataclass
class Company:
    cash: float
    inventory: dict[str, dict[Product,float]]
    warehouse_capacity: dict[str,float]
    logistics_capacity: float
    facilities: list[Facility]=field(default_factory=list)
    infrastructure_value: float=0.0
    revenue_total: float=0.0
    expense_total: float=0.0
    produced: dict[Product,float]=field(default_factory=lambda:{p:0.0 for p in Product})
    ledger: list[tuple[float,float,float,str]]=field(default_factory=list)
    def stock(self,location,product): return self.inventory[location][product]
    def used_space(self,location): return sum(self.inventory[location].values())
    def free_space(self,location): return self.warehouse_capacity[location]-self.used_space(location)
    def add(self,location,product,qty):
        if qty<0 or qty>self.free_space(location)+1e-9: raise ValueError(f"Armazém de {location} sem espaço suficiente.")
        self.inventory[location][product]+=qty
    def remove(self,location,product,qty):
        if qty<0 or qty>self.stock(location,product)+1e-9: raise ValueError(f"Estoque insuficiente em {location}.")
        self.inventory[location][product]=max(0.0,self.stock(location,product)-qty)
    def record(self,t,revenue=0,expense=0,category=""):
        self.revenue_total+=revenue; self.expense_total+=expense; self.ledger.append((t,revenue,expense,category))
        if len(self.ledger)>5000: self.ledger=self.ledger[-5000:]

class GameError(Exception): pass
