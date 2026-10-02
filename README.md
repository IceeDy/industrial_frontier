# Industrial Frontier (nome provisório)

> YOU DON'T FLY THE SHIP. YOU RUN THE COMPANY.

Protótipo jogável de gestão econômica/industrial espacial. Você administra uma pequena corporação:
minera, refina, fabrica, transporta e vende — a empresa trabalha sozinha enquanto você decide.

## Instalação e execução
```bash
pip install -r requirements.txt
streamlit run app.py
pytest
```

## Arquitetura
- `game/models.py` — dataclasses, constantes, rotas
- `game/game_state.py` — `GameState`, relógio, log, `new_game()`
- `game/economy.py` — preço por oferta/demanda e dinâmica dos mercados
- `game/market.py` — `buy` / `sell`
- `game/industry.py` — mina, refinaria, fábrica, expansões
- `game/logistics.py` — transportes
- `game/simulation.py` — `advance_simulation()` (único ponto do tempo) e finanças
- `app.py` — interface Streamlit, sem regras econômicas

Automação futura: `GameState.hooks` recebe funções chamadas a cada passo da simulação.
Para PostgreSQL, basta persistir `Company`, `Facility`, `Transport` e `MarketEntry` (dataclasses simples).

## Mecânicas atuais
- Começa com ₡10.000, mina em Marte (100 min./h) e armazém de 1.000 em Marte (Terra e Lua: 300).
- Cadeia: minério → (refinaria 10→8) → ferro refinado → (fábrica 10→1) → componentes.
- Preço = f(estoque ÷ estoque-alvo); vender derruba o preço, comprar sobe; demanda oscila e há choques aleatórios.
- Logística abstrata: capacidade de 1.000 un. em trânsito, frete por unidade e tempo por rota
  (Terra–Lua ₡5/6h, Terra–Marte ₡10/24h, Lua–Marte ₡8/18h).
- Relógio: o tempo real vira tempo de jogo (velocidade ajustável); botões +1h/+6h/+24h.
- Expansões: refinaria ₡5.000, fábrica ₡15.000, segunda mina ₡20.000, armazém ₡10.000, logística ₡5.000.

## Limitações
Estado só em memória (perde ao recarregar a sessão), um único preço por mercado (sem order book),
sem NPCs concorrentes, contabilidade simplificada (compras entram como custo), um recurso.

## Próximos passos
Order book, mais recursos, frotas próprias, compra/venda automática (hooks), persistência, agentes de IA.
