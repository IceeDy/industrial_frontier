"""Versioned JSON persistence for Industrial Frontier game states."""
from __future__ import annotations

import json
import random
from collections import deque
from dataclasses import asdict
from typing import Any

from .game_state import GameState
from .models import Company, Facility, Market, Product, Transport

SAVE_FORMAT = "industrial-frontier-save"
SAVE_VERSION = 1


def _jsonable_rng(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable_rng(item) for item in value]
    if isinstance(value, list):
        return [_jsonable_rng(item) for item in value]
    return value


def _tuple_tree(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_tuple_tree(item) for item in value)
    return value


def state_to_dict(state: GameState) -> dict[str, Any]:
    company = state.company
    return {
        "format": SAVE_FORMAT,
        "version": SAVE_VERSION,
        "time": state.t,
        "speed": state.speed,
        "next_id_value": state.next_id_value,
        "rng_state": _jsonable_rng(state.rng.getstate()),
        "company": {
            "cash": company.cash,
            "inventory": {
                location: {product.value: quantity for product, quantity in stock.items()}
                for location, stock in company.inventory.items()
            },
            "warehouse_capacity": company.warehouse_capacity,
            "logistics_capacity": company.logistics_capacity,
            "facilities": [asdict(facility) for facility in company.facilities],
            "infrastructure_value": company.infrastructure_value,
            "revenue_total": company.revenue_total,
            "expense_total": company.expense_total,
            "produced": {product.value: quantity for product, quantity in company.produced.items()},
            "ledger": [list(entry) for entry in company.ledger],
            "discovered_locations": list(company.discovered_locations),
        },
        "markets": [
            {
                "location": market.location,
                "product": market.product.value,
                "base_price": market.base_price,
                "base_demand_h": market.base_demand_h,
                "stock": market.stock,
                "demand_mult": market.demand_mult,
                "volatility": market.volatility,
                "price": market.price,
                "npc_supply_h": market.npc_supply_h,
            }
            for market in state.markets.values()
        ],
        "transports": [
            {
                **asdict(transport),
                "product": transport.product.value,
            }
            for transport in state.transports
        ],
        "events": [list(event) for event in state.events],
        "history": state.history,
        "price_history": state.price_history,
    }


def dump_state(state: GameState) -> str:
    """Serialize a state as portable, human-readable UTF-8 JSON."""
    return json.dumps(state_to_dict(state), ensure_ascii=False, indent=2, allow_nan=False)


def state_from_dict(data: dict[str, Any]) -> GameState:
    if not isinstance(data, dict) or data.get("format") != SAVE_FORMAT:
        raise ValueError("Este arquivo não é um save válido do Industrial Frontier.")
    if data.get("version") != SAVE_VERSION:
        raise ValueError(
            f"Versão de save não suportada: {data.get('version')!r}. "
            f"Esta versão aceita {SAVE_VERSION}."
        )

    try:
        raw_company = data["company"]
        inventory = {
            location: {Product(product): float(quantity) for product, quantity in stock.items()}
            for location, stock in raw_company["inventory"].items()
        }
        produced = {
            Product(product): float(quantity)
            for product, quantity in raw_company["produced"].items()
        }
        facilities = [Facility(**item) for item in raw_company["facilities"]]
        company = Company(
            cash=float(raw_company["cash"]),
            inventory=inventory,
            warehouse_capacity={key: float(value) for key, value in raw_company["warehouse_capacity"].items()},
            logistics_capacity=float(raw_company["logistics_capacity"]),
            facilities=facilities,
            infrastructure_value=float(raw_company["infrastructure_value"]),
            revenue_total=float(raw_company["revenue_total"]),
            expense_total=float(raw_company["expense_total"]),
            produced=produced,
            ledger=[(float(t), float(revenue), float(expense), str(category))
                    for t, revenue, expense, category in raw_company["ledger"]],
            discovered_locations=list(raw_company.get("discovered_locations", inventory.keys())),
        )
        markets = {}
        for item in data["markets"]:
            market = Market(
                location=item["location"],
                product=Product(item["product"]),
                base_price=float(item["base_price"]),
                base_demand_h=float(item["base_demand_h"]),
                stock=float(item["stock"]),
                demand_mult=float(item["demand_mult"]),
                volatility=float(item["volatility"]),
                price=float(item["price"]),
                npc_supply_h=float(item["npc_supply_h"]),
            )
            markets[(market.location, market.product)] = market
        transports = [
            Transport(
                id=int(item["id"]),
                origin=item["origin"],
                destination=item["destination"],
                product=Product(item["product"]),
                quantity=float(item["quantity"]),
                cost=float(item["cost"]),
                start_t=float(item["start_t"]),
                eta_t=float(item["eta_t"]),
                capacity=float(item["capacity"]),
            )
            for item in data["transports"]
        ]
        rng = random.Random()
        rng.setstate(_tuple_tree(data["rng_state"]))
        state = GameState(
            company=company,
            markets=markets,
            t=float(data["time"]),
            transports=transports,
            events=deque(
                ((str(when), str(message)) for when, message in data["events"]),
                maxlen=500,
            ),
            history=list(data["history"]),
            price_history=list(data["price_history"]),
            rng=rng,
            next_id_value=int(data["next_id_value"]),
            speed=float(data["speed"]),
        )
    except (KeyError, TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"Save inválido ou corrompido: {error}") from error

    if not all(quantity >= 0 for stock in company.inventory.values() for quantity in stock.values()):
        raise ValueError("Save inválido: o inventário contém quantidade negativa.")
    if not all(market.price >= 0 and market.stock >= 0 for market in markets.values()):
        raise ValueError("Save inválido: mercado contém preço ou estoque negativo.")
    return state


def load_state(contents: str | bytes) -> GameState:
    """Load a state from JSON text or bytes, with readable validation errors."""
    try:
        data = json.loads(contents)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError) as error:
        raise ValueError(f"Não foi possível ler o arquivo de save: {error}") from error
    return state_from_dict(data)
