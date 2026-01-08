# Deep Research Orchestrator - Architektur

## Aktuelle Architektur (2026-01-04)

### System-Übersicht

```
┌─────────────────────────────────────────────────────────┐
│                    Benutzer (Browser)                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ http://localhost:5173
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Vue 3 Frontend (Vite Dev Server)              │
│                   Port: 5173                             │
│                                                          │
│  - Research Creator (Haupt-Feature)                     │
│  - Dashboard (für andere Features)                      │
│  - Builder, Execution, Docs Views                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Proxy: /api/* → localhost:5000
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Flask API Server (Python)                   │
│                   Port: 5000                             │
│                                                          │
│  Research Endpoints (Mock Mode):                        │
│  - POST /api/research/evaluate-input-quality            │
│  - POST /api/research/generate/structure                │
│  - POST /api/research/detect-blindspots                 │
│  - POST /api/research/generate-deep-prompts             │
│                                                          │
│  Stub Endpoints (für Dashboard):                        │
│  - GET /api/frameworks                                  │
│  - GET /api/workflows                                   │
│  - GET /api/techniques                                  │
└─────────────────────────────────────────────────────────┘
```

## Warum 2 getrennte Server?

### Vorteile

1. **Hot Reload**: Frontend-Änderungen laden sofort neu ohne Backend-Neustart
2. **Entwicklung**: Frontend und Backend können unabhängig entwickelt werden
3. **Skalierung**: Später kann das Frontend auf CDN deployed werden
4. **Debugging**: Einfacher zu debuggen wenn Fehler isoliert werden können
5. **Mock Mode**: Backend kann in Mock Mode laufen ohne echte LLMs

### Ports

| Service | Port | Beschreibung |
|---------|------|--------------|
| **API Server** | 5000 | Flask Backend (Mock Mode aktiv) |
| **Vue Frontend** | 5173 | Vite Dev Server mit Hot Reload |
| ~~Old Viewer~~ | ~~8002~~ | **VERALTET - NICHT MEHR NUTZEN** |

## Starten des Systems

### Entwicklungsmodus (empfohlen)

```bash
./start_dev.sh
```

Das startet:
1. API Server auf Port 5000 (Mock Mode)
2. Vue Frontend auf Port 5173
3. Killt automatisch Port 8002 (alte GUI)

### Manuell starten

```bash
# Terminal 1: API Server
./viewer/venv/bin/python3 api_server.py

# Terminal 2: Vue Frontend
cd gui && npm run dev
```

## Mock Mode vs. Real Mode

### Mock Mode (Standard)

**Aktiv per default** - Keine lokalen LLMs nötig!

```python
# In api_server.py
helper = ResearchQualityHelper(use_mock=True)
generator = ResearchGenerator(use_mock=True)
```

**Vorteile:**
- Funktioniert auf schwacher Hardware
- Instant Response (keine LLM-Wartezeit)
- Keine llama-server Installation nötig
- Perfekt für Frontend-Entwicklung

### Real Mode

Für Produktion mit echten LLMs:

```python
# In api_server.py - ändern zu:
helper = ResearchQualityHelper(use_mock=False)
generator = ResearchGenerator(use_mock=False)
```

**Benötigt:**
- llama.cpp server läuft auf Port 8081
- Modell geladen (z.B. Mixtral, Llama 3)
- Genug RAM/VRAM für das Modell

## API Endpoints

### Research Endpoints (Funktional)

```bash
# Step 0: Quality Check
curl -X POST http://localhost:5000/api/research/evaluate-input-quality \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Deine Forschungsbeschreibung",
    "goal": "Dein Ziel",
    "research_type": "product"
  }'

# Step 1: Theme Generation
curl -X POST http://localhost:5000/api/research/generate/structure \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "...",
    "research_goal": "...",
    "research_type": "product"
  }'

# Step 2: Blindspot Detection
curl -X POST http://localhost:5000/api/research/detect-blindspots \
  -H "Content-Type: application/json" \
  -d '{
    "thematic_hierarchy": [...],
    "user_context": "..."
  }'

# Step 3: Deep Research Prompts
curl -X POST http://localhost:5000/api/research/generate-deep-prompts \
  -H "Content-Type: application/json" \
  -d '{
    "selected_themes": [...],
    "research_context": "..."
  }'
```

### Dashboard Endpoints (Stubs)

Diese Endpoints geben leere Arrays zurück - für zukünftige Features:

```bash
GET /api/frameworks   → []
GET /api/workflows    → []
GET /api/techniques   → []
```

## Frontend Struktur

```
gui/
├── src/
│   ├── views/
│   │   ├── ResearchCreator.vue    # Haupt-Feature (6-Step Workflow)
│   │   ├── Dashboard.vue          # Übersicht
│   │   ├── BuilderView.vue        # Logic Builder
│   │   ├── ExecutionView.vue      # Workflow Execution
│   │   └── DocsView.vue           # Dokumentation
│   ├── components/
│   │   ├── ThemeNode.vue          # Themen-Hierarchie
│   │   ├── FrameworkTree.vue      # Framework Editor
│   │   └── ...
│   ├── api/
│   │   └── client.js              # API Client Functions
│   └── router/
│       └── index.js               # Vue Router Config
└── vite.config.js                 # Proxy: /api → 5000
```

## Backend Struktur

```
.
├── api_server.py                  # Neuer API Server (Port 5000)
├── src/
│   ├── services/
│   │   ├── research_quality_helper.py    # Step 0
│   │   └── research_generator.py         # Steps 1-3
│   └── models/
│       └── llama_cpp_client.py           # LLM Client (optional)
└── viewer/                                # ALT - Nur für Dependencies
    ├── venv/                             # Python Virtual Env
    └── serve_gui.py                      # ❌ VERALTET
```

## Alte Dateien (NICHT MEHR NUTZEN)

```
❌ viewer/serve_gui.py          # Alte GUI (Port 8002)
❌ start_gui.sh                  # Startet alte GUI
❌ start_clean.sh                # Legacy Script
```

## Logs

```bash
# API Server
tail -f /tmp/api_server.log

# Vue Frontend
tail -f /tmp/vue_frontend.log  # Falls via start_dev.sh gestartet
```

## Troubleshooting

### Vue Frontend lädt nicht

```bash
cd gui
npm install
npm run dev
```

### API Server antwortet nicht

```bash
# Check Log
tail -f /tmp/api_server.log

# Neustart
fuser -k 5000/tcp
./viewer/venv/bin/python3 api_server.py
```

### Port 8002 läuft noch

```bash
# Alte GUI killen
fuser -k 8002/tcp
pkill -9 -f "serve_gui"
pkill -9 -f "start_gui"
```

### Alles neu starten

```bash
# Alle Ports freigeben
fuser -k 5000/tcp 5173/tcp 8002/tcp

# System neu starten
./start_dev.sh
```

## Nächste Schritte

1. **Jetzt testen**: `./start_dev.sh` ausführen
2. **Research Creator nutzen**: http://localhost:5173 → "Research Creator"
3. **Mock Mode testen**: Alle 6 Steps durchgehen
4. **Später Real Mode**: Wenn bessere Hardware verfügbar

---

**Dokumentation erstellt:** 2026-01-04
**Mock Mode:** AKTIV
**Architektur:** 2-Server (API + Frontend)
**Status:** READY FOR TESTING
