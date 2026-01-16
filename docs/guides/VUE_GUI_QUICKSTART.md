# 🚀 Vue GUI Quick Start

## Was wurde implementiert?

Eine vollständige **Vue 3 GUI** für den Deep Research Orchestrator mit:

### ✅ Fertige Features:

1. **Dashboard** (`/`)
   - Übersicht aller Frameworks
   - Status-Anzeige (Anzahl Frameworks, Workflows, Techniques)
   - Framework-Auswahl für Editor

2. **Framework Tree** (Sidebar im Editor)
   - Hierarchische Darstellung: Framework → Phases → Workflows → Techniques
   - Expand/Collapse Funktionalität
   - Active-State Highlighting
   - "Edit"-Button für Techniques

3. **Prompt Editor** (Hauptbereich im Editor)
   - Technique-Informationen
   - Prompt-Textfeld (editierbar)
   - Settings (Temperature, Max Tokens, Agent Role)
   - Save/Reset Buttons
   - Echtzeit-Speicherung in JSON-Files

4. **Pinia State Management**
   - Zentraler State für alle Orchestrator-Daten
   - Actions für CRUD-Operationen
   - Computed Properties für Hierarchie

5. **Flask API Erweiterung**
   - `PATCH /api/technique/<id>` - Technique update
   - `PATCH /api/workflow/<id>` - Workflow update
   - `PATCH /api/phase/<id>` - Phase update
   - `POST /api/orchestrator/reload` - Orchestrator reload

---

## 🎯 Wie starte ich die GUI?

### Option 1: Alles zusammen (empfohlen)

```bash
./start_dev.sh
```

Das startet:
- Flask Backend auf Port 8002
- Vue Frontend auf Port 5173

**URLs:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8002/api/

### Option 2: Separat starten

**Terminal 1 - Backend:**
```bash
./start_gui.sh --port 8002 --host 0.0.0.0
```

**Terminal 2 - Frontend:**
```bash
cd gui
npm run dev
```

---

## 📖 Workflow zum Prompts editieren

1. **Dashboard öffnen**: http://localhost:5173
2. **Framework auswählen**: Klick auf Framework-Karte (z.B. "Product Research")
3. **Editor öffnet sich**: Links siehst du den Framework-Tree
4. **Navigiere zur Technique**:
   - Klick auf Phase (z.B. "Base Research")
   - Klick auf Workflow (z.B. "Market Research Collection")
   - Klick auf "Edit" bei einer Technique (z.B. "Contradiction Check")
5. **Prompt editieren**:
   - Ändere den Prompt-Text
   - Passe Temperature/Max Tokens an
   - Klick "Save Changes"
6. **Fertig**: Änderungen sind in `config/techniques/contradiction.json` gespeichert!

---

## 🗂️ Dateistruktur

```
gui/
├── src/
│   ├── components/
│   │   ├── FrameworkTree.vue       ✅ Hierarchische Tree-Ansicht
│   │   └── PromptEditor.vue        ✅ Prompt-Editor mit Settings
│   ├── views/
│   │   ├── Dashboard.vue           ✅ Haupt-Dashboard
│   │   ├── EditorView.vue          ✅ Editor-Ansicht
│   │   └── VisualizerView.vue      🚧 Workflow-Visualisierung (Placeholder)
│   ├── stores/
│   │   └── orchestrator.js         ✅ Pinia Store
│   ├── router/
│   │   └── index.js                ✅ Vue Router
│   ├── api/
│   │   └── client.js               ✅ API Client
│   ├── App.vue                     ✅ Root Component
│   └── main.js                     ✅ Entry Point
├── package.json                    ✅
├── vite.config.js                  ✅ Mit Proxy zu Flask
└── README.md                       ✅ Dokumentation
```

---

## 🎨 Screenshots (Konzept)

### Dashboard
```
┌─────────────────────────────────────────┐
│  🎯 Deep Research Orchestrator          │
│     Visual Workflow Editor              │
├─────────────────────────────────────────┤
│  Frameworks: 1 │ Workflows: 7 │ ...     │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐       │
│  │ 📦 Product  │  │ ➕ Create   │       │
│  │  Research   │  │    New      │       │
│  │             │  │             │       │
│  │ 3 phases    │  │             │       │
│  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────┘
```

### Editor View
```
┌─────────────┬──────────────────────────┐
│ 📦 Framework│ 🎯 Contradiction Check   │
│   ▾ Base    │ ┌──────────────────────┐ │
│     ▾ Market│ │ Prompt:              │ │
│       🎯 Con│ │ Analyze the...       │ │
│       🎯 Bli│ │                      │ │
│   ▸ Validat │ │                      │ │
│   ▸ Synthes │ └──────────────────────┘ │
│             │ Temperature: [0.3]       │
│             │ Max Tokens:  [2000]      │
│             │ [Save] [Reset]           │
└─────────────┴──────────────────────────┘
```

---

## 🔧 API Endpoints (Backend)

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| GET | `/api/frameworks` | Liste aller Frameworks |
| GET | `/api/framework/<id>` | Framework mit Hierarchie |
| GET | `/api/techniques` | Liste aller Techniques |
| GET | `/api/technique/<id>` | Einzelne Technique |
| PATCH | `/api/technique/<id>` | Technique aktualisieren |
| POST | `/api/orchestrator/reload` | Orchestrator neu laden |

---

## 🐛 Troubleshooting

### Problem: "Port already in use"

```bash
fuser -k 8002/tcp  # Flask
fuser -k 5173/tcp  # Vue
```

### Problem: "Cannot connect to API"

1. Prüfe ob Flask läuft: http://localhost:8002/api/status
2. Prüfe Vite Proxy in `gui/vite.config.js`:
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8002',
    changeOrigin: true
  }
}
```

### Problem: "Module not found"

```bash
cd gui
npm install
```

### Problem: "Framework not loading"

1. Prüfe ob Framework-JSON existiert:
```bash
ls -la config/frameworks/
```

2. Prüfe ob Orchestrator läuft:
```bash
curl http://localhost:8002/api/frameworks
```

---

## 📋 Nächste Schritte

### Sofort verfügbar:
- ✅ Prompts editieren und speichern
- ✅ Framework-Hierarchie durchsuchen
- ✅ Settings anpassen (Temperature, Max Tokens)

### Nächste Features (optional):
- 🚧 Monaco Editor für besseres Prompt-Editing
- 🚧 Vue Flow für visuellen Workflow-Builder
- 🚧 Create/Delete Funktionalität
- 🚧 Drag & Drop für Workflow-Komposition

---

## 💡 Tipps

1. **Speichern nicht vergessen**: Die GUI speichert nicht automatisch - immer "Save Changes" klicken!

2. **Orchestrator Reload**: Nach Änderungen wird der Orchestrator automatisch neu geladen

3. **JSON-Files**: Alle Änderungen werden direkt in die JSON-Config-Files geschrieben:
   - `config/techniques/*.json`
   - `config/workflows/sequential/*.json`
   - `config/phases/*.json`

4. **Browser DevTools**: Bei Problemen: F12 → Console → Fehler prüfen

5. **Kakao Theme**: Die GUI nutzt dasselbe Farbschema wie die Dokumentation

---

## 🎓 Lernen & Erweitern

### Component hinzufügen:

1. Erstelle neue `.vue` Datei in `gui/src/components/`
2. Importiere in Parent-Component
3. Nutze Pinia Store für State
4. Folge Kakao Theme (siehe CSS Variables in `App.vue`)

### API Endpoint hinzufügen:

1. Füge Route in `viewer/serve_gui.py` hinzu
2. Erstelle Funktion in `gui/src/api/client.js`
3. Nutze im Pinia Store Action

### State erweitern:

1. Öffne `gui/src/stores/orchestrator.js`
2. Füge neue `ref()` für State hinzu
3. Erstelle Action für Updates
4. Nutze in Components via `storeToRefs()`

---

## 📚 Dokumentation

- **Vue GUI Guide**: `docs/VUE_GUI_IMPLEMENTATION_GUIDE.md`
- **GUI README**: `gui/README.md`
- **This Quickstart**: `VUE_GUI_QUICKSTART.md`

---

**Viel Erfolg beim Editieren deiner Workflows! 🚀**
