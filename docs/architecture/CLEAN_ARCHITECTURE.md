# Clean Architecture - API + Vue Frontend

## 🎯 Aktuelle Architektur (Stand: 2026-01-04)

**Alte System (Port 8002) - NICHT MEHR VERWENDET:**
- ❌ `viewer/` - Altes livereload-basiertes System
- ❌ `start_gui.sh` - Startet altes System

**Neue Architektur:**
- ✅ **API Server** (Port 5000) - `api_server.py`
- ✅ **Vue Frontend** (Port 5173) - `gui/`
- ✅ **Mock Mode** - Keine llama-server nötig

## 🚀 Starten

```bash
./start_clean.sh
```

Das startet:
1. API Server auf http://localhost:5000
2. Vue Frontend auf http://localhost:5173

## 📡 API Endpunkte

### Status Check
```bash
curl http://localhost:5000/api/status
```

### Step 0: Quality Evaluation
```bash
curl -X POST http://localhost:5000/api/research/evaluate-input-quality \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Deine Forschungsbeschreibung",
    "goal": "Dein Forschungsziel",
    "research_type": "product"
  }'
```

### Step 1: Theme Generation
```bash
curl -X POST http://localhost:5000/api/research/generate/structure \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Deine Beschreibung",
    "research_goal": "Dein Ziel",
    "research_type": "product"
  }'
```

### Blindspot Detection
```bash
curl -X POST http://localhost:5000/api/research/detect-blindspots \
  -H "Content-Type: application/json" \
  -d '{
    "thematic_hierarchy": [...],
    "user_context": "..."
  }'
```

### Deep Research Prompts
```bash
curl -X POST http://localhost:5000/api/research/generate-deep-prompts \
  -H "Content-Type: application/json" \
  -d '{
    "selected_themes": [...],
    "research_context": "..."
  }'
```

## 🎨 Vue Frontend

### Entwicklung
```bash
cd gui
npm run dev
```

Öffne http://localhost:5173

### Build
```bash
cd gui
npm run build
```

## 📁 Dateistruktur

```
.
├── api_server.py           # Flask API Server (Port 5000)
├── start_clean.sh          # Sauberer Start (API + Vue)
├── gui/                    # Vue 3 Frontend
│   ├── src/
│   │   ├── views/
│   │   │   └── ResearchCreator.vue  # Haupt-Workflow
│   │   ├── api/
│   │   │   └── client.js   # API Client
│   │   └── router/
│   └── vite.config.js      # Proxy: /api → localhost:5000
├── src/                    # Python Backend Services
│   ├── services/
│   │   ├── research_quality_helper.py  # Step 0
│   │   └── research_generator.py        # Step 1+
│   └── models/
│       └── llama_cpp_client.py
└── viewer/                 # ❌ ALT - Nicht mehr verwenden!
    └── serve_gui.py        # ❌ Port 8002 - Veraltet
```

## 🔄 Migration: 8002 → 5173

### Was wurde geändert:

1. **Proxy in `gui/vite.config.js`:**
   ```js
   proxy: {
     '/api': {
       target: 'http://localhost:5000',  // Vorher: 8002
       changeOrigin: true
     }
   }
   ```

2. **Neuer API Server:**
   - Keine livereload
   - Keine viewer templates
   - Nur Flask + CORS + API Endpoints

3. **Mock Mode:**
   - `ResearchQualityHelper(use_mock=True)`
   - `ResearchGenerator(use_mock=True)`

## 🛑 Stoppen

```bash
# Alle Prozesse beenden
pkill -f api_server.py
pkill -f 'npm run dev'

# Nur API stoppen
pkill -f api_server.py

# Nur Vue stoppen
pkill -f 'npm run dev'
```

## 📊 Port-Übersicht

| Service | Port | Status | Verwendung |
|---------|------|--------|------------|
| API Server | 5000 | ✅ Aktiv | Flask Backend (Mock Mode) |
| Vue Frontend | 5173 | ✅ Aktiv | Vue 3 + Vite Dev Server |
| Viewer (Alt) | 8002 | ❌ Veraltet | NICHT MEHR VERWENDEN |

## 🔧 Troubleshooting

### Vue Frontend lädt nicht

```bash
cd gui
npm install  # Dependencies installieren
npm run dev  # Neu starten
```

### API Server antwortet nicht

```bash
# Log checken
tail -f /tmp/api_server.log

# Neu starten
pkill -f api_server.py
./viewer/venv/bin/python3 api_server.py &
```

### Port bereits belegt

```bash
# Port 5000 freigeben
fuser -k 5000/tcp

# Port 5173 freigeben
fuser -k 5173/tcp
```

## 📝 Logs

```bash
# API Server
tail -f /tmp/api_server.log

# Vue Frontend
tail -f /tmp/vue_frontend.log
```

## ✅ Nächste Schritte

1. Öffne http://localhost:5173
2. Gehe zu "Research Creator"
3. Teste Step 0 (Quality Check)
4. Teste Step 1 (Theme Generation)
5. Mock-Daten werden sofort zurückgegeben

## 🚀 Später: Real Mode

Wenn du bessere Hardware hast:

1. Ändere in `api_server.py`:
   ```python
   helper = ResearchQualityHelper(use_mock=False)
   generator = ResearchGenerator(use_mock=False)
   ```

2. Stelle sicher, dass llama-server läuft
3. Nutze stärkere Modelle (Mixtral, Llama 3, etc.)

---

**Dokumentation erstellt:** 2026-01-04
**Mock Mode:** AKTIV
**System:** Sauber und getrennt (API + Vue)
