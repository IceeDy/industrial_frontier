# Industrial Frontier

> **YOU DON'T FLY THE SHIP. YOU RUN THE COMPANY.**

Industrial Frontier is a space-industry management simulator. The player does not pilot ships or control a character: the company executes operations while the player decides what to build, buy, sell, refine, manufacture and transport.

## Playable core

**Mining → Refining → Manufacturing → Transport → Market → Revenue → Expansion**

The current engine includes:
- continuous and manual time advancement;
- mining, refining, manufacturing and fuel production;
- local warehouses and inventory capacity;
- interplanetary transport with route time, capacity and freight cost;
- dynamic regional markets with supply, demand, NPC supply and price pressure;
- market buy/sell transactions;
- random economic demand shocks;
- facility maintenance and company accounting;
- financial history and price history;
- Streamlit management dashboard;
- automated tests for the economic loop.

## Architecture

- game/models.py — domain entities, products, recipes, facilities and routes.
- game/game_state.py — complete runtime state and new-game setup.
- game/economy.py — demand, NPC supply, shocks and price formation.
- game/market.py — player market transactions.
- game/industry.py — production and expansion.
- game/logistics.py — cargo in transit.
- game/simulation.py — the single point where game time advances.
- app.py — Streamlit presentation and player actions.
- tests/ — regression tests for the core loop.

The domain engine is intentionally independent from Streamlit so future interfaces, persistence and automation can be added without rewriting the rules.

## Run

    pip install -r requirements.txt
    streamlit run app.py
    pytest -q

## Design direction

The game borrows concepts, not content, from economic and industrial space games: logistics, production chains, markets, regional specialization and corporate expansion. The progression philosophy also takes inspiration from incremental games: automation and scale should gradually replace manual intervention.

## Roadmap

1. Order book with NPC and player buy/sell orders.
2. More resources and production chains.
3. Fleet classes, cargo capacity, fuel and operating costs.
4. Contracts and recurring procurement/sales.
5. Company automation and managers.
6. Corporate finance, debt and acquisitions.
7. Persistent storage and offline simulation.
8. System specialization and a larger galaxy.
9. Long-term corporate competition and deeper economic simulation.

The first goal is to make the industrial loop itself fun and economically coherent before expanding the world dramatically.
