from __future__ import annotations

from dataclasses import dataclass, field

ORE, REFINED, COMPONENTS = "iron_ore", "refined_iron", "components"
PRODUCTS = (ORE, REFINED, COMPONENTS)
PRODUCT_NAMES = {ORE: "Minério de ferro", REFINED: "Ferro refinado", COMPONENTS: "Componentes industriais"}
LOCATIONS = ("Terra", "Lua", "Marte")

TARGET_COVER_H = 24.0      # horas de demanda que o mercado "quer" ter em estoque
MAX_STOCK_FACTOR = 3.0     # saturação: acima de 3x o estoque-alvo o mercado não absorve mais
REFINERY_RATIO = 0.8       # 10 minério -> 8 ferro refinado
FACTORY_INPUT = 10.0       # 10 ferro refinado -> 1 componente
WAREHOUSE_COST, WAREHOUSE_SIZE = 10_000.0, 1_000.0
LOGISTICS_COST, LOGISTICS_SIZE = 5_000.0, 1_000.0
START_CASH, START_MINE_VALUE = 10_000.0, 5_000.0


class GameError(Exception):
    """Erro de regra de negócio (mostrado ao jogador)."""


def money(value: float) -> str:
    return "₡" + f"{value:,.0f}".replace(",", ".")


@dataclass(frozen=True)
class Route:
    cost_per_unit: float
    hours: float


ROUTES = {
    ("Lua", "Terra"): Route(5, 6),
    ("Marte", "Terra"): Route(10, 24),
    ("Lua", "Marte"): Route(8, 18),
}


def get_route(origin: str, destination: str) -> Route:
    key = tuple(sorted((origin, destination)))
    if origin == destination or key not in ROUTES:
        raise GameError("Rota inválida: origem e destino devem ser locais diferentes.")
    return ROUTES[key]  # type: ignore[index]


@dataclass(frozen=True)
class FacilitySpec:
    label: str
    cost: float
    rate: float    # mina: minério/h | refinaria: minério/h consumido | fábrica: componentes/h
    upkeep: float  # custo operacional por hora
    recipe: str


SPECS = {
    "mine": FacilitySpec("Mina de ferro", 20_000, 100, 40, "→ Minério de ferro"),
    "refinery": FacilitySpec("Refinaria", 5_000, 50, 60, "10 minério → 8 ferro refinado"),
    "factory": FacilitySpec("Fábrica", 15_000, 10, 120, "10 ferro refinado → 1 componente"),
}


@dataclass
class Facility:
    id: int
    kind: str
    location: str
    value: float
    produced: float = 0.0

    @property
    def spec(self) -> FacilitySpec:
        return SPECS[self.kind]

    @property
    def label(self) -> str:
        return self.spec.label


@dataclass
class Transport:
    id: int
    origin: str
    destination: str
    product: str
    quantity: float
    cost: float
    start_t: float
    eta_t: float

    def progress(self, now: float) -> float:
        span = max(self.eta_t - self.start_t, 1e-9)
        return min(max((now - self.start_t) / span, 0.0), 1.0)


@dataclass
class MarketEntry:
    location: str
    product: str
    base_price: float
    base_demand: float          # unidades/hora
    stock: float
    price: float
    demand_mult: float = 1.0

    @property
    def demand(self) -> float:
        return self.base_demand * self.demand_mult

    @property
    def target_stock(self) -> float:
        return self.demand * TARGET_COVER_H


@dataclass
class Company:
    cash: float
    inventory: dict[str, dict[str, float]]
    capacity: dict[str, float]
    logistics_capacity: float
    facilities: list[Facility] = field(default_factory=list)
    infrastructure_value: float = 0.0
    revenue_total: float = 0.0
    cost_total: float = 0.0
    produced: dict[str, float] = field(default_factory=lambda: {p: 0.0 for p in PRODUCTS})
    ledger: list[tuple[float, float, float]] = field(default_factory=list)  # (t, receita, custo)

    def stock(self, location: str, product: str) -> float:
        return self.inventory[location][product]

    def used_space(self, location: str) -> float:
        return sum(self.inventory[location].values())

    def free_space(self, location: str) -> float:
        return self.capacity[location] - self.used_space(location)

    def add(self, location: str, product: str, qty: float) -> None:
        if qty > self.free_space(location) + 1e-6:
            raise GameError(f"Armazém de {location} sem espaço.")
        self.inventory[location][product] += qty

    def remove(self, location: str, product: str, qty: float) -> None:
        if qty > self.stock(location, product) + 1e-6:
            raise GameError(f"Estoque insuficiente em {location}.")
        self.inventory[location][product] = max(0.0, self.stock(location, product) - qty)

    def record(self, t: float, revenue: float = 0.0, cost: float = 0.0) -> None:
        self.revenue_total += revenue
        self.cost_total += cost
        self.ledger.append((t, revenue, cost))
        if self.ledger[0][0] < t - 24:
            self.ledger = [e for e in self.ledger if e[0] >= t - 24]
