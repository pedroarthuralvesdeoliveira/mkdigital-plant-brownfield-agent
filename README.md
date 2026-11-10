# MKdigital — Plant Brownfield Reconstruction Agent (Project B)

[![CI](https://github.com/pedroarthuralvesdeoliveira/mkdigital-plant-brownfield-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/pedroarthuralvesdeoliveira/mkdigital-plant-brownfield-agent/actions)

Clean-architecture GraphDB backend and interactive topology inspector for **MKdigital Project B (Plant Brownfield Reconstruction Agent — P&ID + E&I → GraphDB)**, built by **Pedro Arthur Alves de Oliveira**.

- **🌐 Live Cloudflare URL (Project B):** [https://mkdigital-plant-brownfield.pedroarthuralvesdeoliveira1.workers.dev](https://mkdigital-plant-brownfield.pedroarthuralvesdeoliveira1.workers.dev)
- **🔗 Companion Project A (AI Bookkeeping Assistant):** [https://mkdigital-bookkeeping-assistant.pedroarthuralvesdeoliveira1.workers.dev](https://mkdigital-bookkeeping-assistant.pedroarthuralvesdeoliveira1.workers.dev) ([GitHub Repo](https://github.com/pedroarthuralvesdeoliveira/mkdigital-bookkeeping-assistant))
- **🤖 Complementary Open-Source LLM Pipeline:** [AI-Contract-Risk-Analysis-Agent](https://github.com/pedroarthuralvesdeoliveira/AI-Contract-Risk-Analysis-Agent)

---

## 🏗️ Software Engineering & Backend Design Principles

- **Clean Architecture, Data Structures & SOLID:**
  - `domain/models.py`: Directed **Adjacency-List Property Graph** (`PlantGraph`) providing $O(1)$ tag lookup, incident edge indexing (`_outgoing` / `_incoming`), **BFS** reachability (`deque`), and an **explicit state machine** (`RAW_DOCUMENTS_LOADED → ENTITIES_EXTRACTED → TOPOLOGY_LINKED → ANOMALIES_EVALUATED → CYPHER_EXPORTED`).
  - `domain/rules.py`: **Specification Pattern** (`BrownfieldAnomalyRule` protocol) evaluating cross-document engineering rules (`UnwiredInstrumentRule` and `MetallurgyTransitionRule`) plus deterministic **Neo4j / Memgraph Cypher** export.
  - `application/use_cases.py`: Stateless use case (`ReconstructPlantUseCase`) decoupled from storage via `PlantTopologyRepository` protocol.
  - `infrastructure/repositories.py` & `api/app.py`: FastAPI adapter with Dependency Injection (`Depends`).
- **UI Palette:** Authentic **MKdigital (`mkdigital.ch`)** design tokens (`#0a0a0a`, `#0f0f0f`, `#161616`, `#222222`, `#ffffff`, `#9c9c9c`, `#70befa`, `Inter Tight`).

## ⚡ Quick Start

```bash
PYTHONPATH=src uv run --with fastapi --with pydantic --with pytest --with httpx pytest -v
PYTHONPATH=src uv run --with fastapi --with pydantic --with uvicorn uvicorn brownfield.api.app:app --reload
```
