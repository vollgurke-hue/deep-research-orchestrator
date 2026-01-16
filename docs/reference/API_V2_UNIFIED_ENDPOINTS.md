# API v2 - Unified Research Endpoints

**Version:** 2.0
**Base URL:** `http://localhost:5000/api/v2`
**Status:** Production Ready

## Übersicht

API v2 vereint Product Research, Sovereign Research und Legacy Orchestrator in ein einheitliches Session-Management-System mit Persistenz.

### Was ist neu in v2?

- ✅ **Unified Session Object** - Ein Datenmodell für alle Research-Modi
- ✅ **Persistenz** - Sessions werden auf Disk gespeichert (`data/sessions/*.json`)
- ✅ **Keine Naming-Konflikte mehr** - SessionManager ersetzt alte globale Variablen
- ✅ **Flexible Modi** - Thematic, ToT, Unified in einem System
- ✅ **Export/Import** - Sessions können exportiert und wiederhergestellt werden

---

## Session Management

### 1. Create Session

**Endpoint:** `POST /api/v2/sessions`

**Erstellt eine neue Research-Session in einem von drei Modi:**

- **thematic**: Product Research (Wizard-driven, Coverage-fokussiert)
- **tot**: Sovereign Research (ToT/Graph/MCTS-Exploration)
- **unified**: Hybrid-Modus (kombiniert beide)

**Request Body:**

```json
{
  "mode": "unified",
  "title": "E-Commerce Nischen-Analyse 2026",
  "goal": "Identifiziere profitable Micro-SaaS Nischen im E-Commerce",
  "description": "Detaillierte Analyse von unerschlossenen Märkten...",
  "axioms": ["opportunity_cost", "risk_tolerance"],
  "research_type": "product"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mode` | string | Yes | `"thematic"` \| `"tot"` \| `"unified"` |
| `title` | string | Yes | Session title (user-facing) |
| `goal` | string | Yes | Primary research goal/question |
| `description` | string | No | Detailed description (for thematic) |
| `axioms` | array | No | Axiom IDs to activate (for tot/unified) |
| `research_type` | string | No | `"product"` \| `"market"` \| `"scientific"` (default: `"product"`) |

**Response:**

```json
{
  "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "mode": "unified",
  "status": "wizard",
  "created_at": "2026-01-09T14:32:15.123Z",
  "message": "Session created successfully"
}
```

---

### 2. List Sessions

**Endpoint:** `GET /api/v2/sessions`

**Query Parameters:**

- `?mode=thematic|tot|unified` (optional filter)

**Response:**

```json
{
  "sessions": [
    {
      "session_id": "f47ac10b...",
      "title": "E-Commerce Nischen-Analyse 2026",
      "mode": "unified",
      "status": "exploring",
      "created_at": "2026-01-09T14:32:15.123Z",
      "goal": "Identifiziere profitable Micro-SaaS Nischen...",
      "current_phase": 1,
      "responses_count": 12,
      "prompts_count": 8,
      "coverage_metrics": {
        "thematic_coverage": 0.75,
        "tot_exploration": 0.45,
        "avg_relevance": 0.82,
        "avg_confidence": 0.87
      },
      "axiom_alignment": {
        "overall_score": 0.88,
        "supports": 10,
        "contradicts": 1,
        "neutral": 1
      }
    }
  ],
  "total": 1
}
```

---

### 3. Get Session Details

**Endpoint:** `GET /api/v2/sessions/{session_id}`

**Response:**

```json
{
  "session": {
    "metadata": {
      "session_id": "f47ac10b...",
      "title": "E-Commerce Nischen-Analyse 2026",
      "created_at": "2026-01-09T14:32:15.123Z",
      "updated_at": "2026-01-09T15:45:32.456Z",
      "status": "exploring",
      "mode": "unified",
      "creator": "user"
    },
    "context": {
      "goal": "Identifiziere profitable Micro-SaaS Nischen...",
      "description": "...",
      "research_type": "product",
      "axioms": ["opportunity_cost", "risk_tolerance"],
      "constraints": {}
    },
    "thematic": {
      "themes": [
        {
          "id": "t1",
          "label": "Wettbewerbsanalyse",
          "coverage": 0.85,
          "children": []
        }
      ],
      "coverage_percentage": 75.0,
      "missing_aspects": ["Preismodelle"]
    },
    "tot": {
      "root_node_id": "node_abc123",
      "total_nodes": 12,
      "max_depth": 3,
      "branching_factor": 3,
      "active_leaves": ["node_xyz"],
      "pruned_branches": []
    },
    "graph": {
      "graph_file": "data/graphs/f47ac10b.json",
      "node_count": 45,
      "edge_count": 78,
      "density": 0.38,
      "max_nodes": 10000
    },
    "state": {
      "current_phase": 1,
      "active_nodes": ["node_xyz"],
      "completed_nodes": ["node_abc", "node_def"],
      "mcts_stats": {
        "iterations": 50,
        "best_path_score": 0.87
      },
      "technique_stack": [],
      "progress_metrics": {}
    },
    "responses": [
      {
        "response_id": "resp_001",
        "node_id": "node_abc",
        "source": "claude-opus",
        "content": "...",
        "timestamp": "2026-01-09T14:45:00.000Z",
        "relevance_score": 0.85,
        "accuracy_score": 0.90,
        "confidence": 0.88,
        "entities_extracted": ["entity1", "entity2"],
        "triplets_extracted": true,
        "graph_facts_added": ["fact1", "fact2"],
        "axiom_evaluation": {
          "scores": {"opportunity_cost": 0.9},
          "compatible": true
        },
        "axiom_compatible": true,
        "strengths": ["Well researched", "Specific examples"],
        "weaknesses": []
      }
    ],
    "prompts": [
      {
        "prompt_id": "prompt_001",
        "node_id": "node_abc",
        "text": "Analyze the competitive landscape...",
        "created_at": "2026-01-09T14:40:00.000Z"
      }
    ]
  }
}
```

---

### 4. Delete Session

**Endpoint:** `DELETE /api/v2/sessions/{session_id}`

**Response:**

```json
{
  "message": "Session f47ac10b... deleted successfully"
}
```

---

## Session Operations

### 5. Initialize Session Components

**Endpoint:** `POST /api/v2/sessions/{session_id}/initialize`

**Initialisiert Runtime-Komponenten (ToT Manager, Graph Manager, MCTS Engine, etc.)**

**Request Body:**

```json
{
  "branching_factor": 3,
  "max_depth": 3
}
```

**Response:**

```json
{
  "session_id": "f47ac10b...",
  "components_initialized": [
    "graph",
    "tot",
    "axiom_mgr",
    "mcts",
    "orchestrator"
  ],
  "status": "exploring",
  "root_node_id": "node_abc123"
}
```

---

### 6. Add Response

**Endpoint:** `POST /api/v2/sessions/{session_id}/responses`

**Fügt eine AI-Antwort zur Session hinzu (unified format für alle Modi)**

**Request Body:**

```json
{
  "node_id": "node_abc123",
  "source": "claude-opus",
  "content": "Based on market analysis, the top 3 viable niches are...",
  "relevance_score": 0.85,
  "accuracy_score": 0.90,
  "confidence": 0.88
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `node_id` | string | No | ToT/Thematic node ID (optional) |
| `source` | string | Yes | `"claude-opus"` \| `"gpt-4"` \| `"gemini-pro"` \| `"local-llm"` |
| `content` | string | Yes | Full response text |
| `relevance_score` | float | No | 0-1 (Product Research) |
| `accuracy_score` | float | No | 0-1 (Product Research) |
| `confidence` | float | No | 0-1 (Sovereign Research) |

**Response:**

```json
{
  "response_id": "resp_001",
  "entities_extracted": 12,
  "axiom_evaluation": {
    "scores": {
      "opportunity_cost": 0.9,
      "risk_tolerance": 0.85
    },
    "compatible": true
  },
  "axiom_compatible": true
}
```

---

### 7. Export Session

**Endpoint:** `GET /api/v2/sessions/{session_id}/export`

**Exportiert Session als JSON-Datei (zum Download)**

**Response:**

File download: `session_f47ac10b.json`

---

### 8. Session Statistics

**Endpoint:** `GET /api/v2/sessions/stats`

**Response:**

```json
{
  "total_sessions": 15,
  "by_mode": {
    "thematic": 5,
    "tot": 7,
    "unified": 3
  },
  "by_status": {
    "wizard": 2,
    "exploring": 8,
    "validating": 3,
    "synthesis": 1,
    "complete": 1
  },
  "storage_path": "data/sessions"
}
```

---

## Session Status Flow

```
wizard → exploring → validating → synthesis → complete
  ↓          ↓           ↓            ↓
  (User defines goal)
             (ToT/Thematic expansion)
                        (Axiom checks)
                                     (Final report)
```

---

## Migration von Legacy Endpoints

### Legacy → v2 Mapping

| Legacy Endpoint | v2 Endpoint | Status |
|----------------|-------------|--------|
| `POST /api/sovereign/research/start` | `POST /api/v2/sessions` (mode=tot) | ✅ Ersetzt |
| `GET /api/sovereign/research/{id}/tot-tree` | `GET /api/v2/sessions/{id}` | ✅ Vereint |
| `POST /api/sovereign/research/{id}/add-response` | `POST /api/v2/sessions/{id}/responses` | ✅ Vereint |
| Product Research Endpoints | `POST /api/v2/sessions` (mode=thematic) | 🔄 In Arbeit |

---

## Beispiel: Unified Workflow

### 1. Session erstellen (Unified Mode)

```bash
curl -X POST http://localhost:5000/api/v2/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "unified",
    "title": "E-Commerce Nischen-Analyse",
    "goal": "Finde profitable Micro-SaaS Nischen",
    "axioms": ["opportunity_cost"]
  }'
```

### 2. Components initialisieren

```bash
curl -X POST http://localhost:5000/api/v2/sessions/f47ac10b.../initialize \
  -H "Content-Type: application/json" \
  -d '{
    "branching_factor": 3,
    "max_depth": 3
  }'
```

### 3. Response hinzufügen

```bash
curl -X POST http://localhost:5000/api/v2/sessions/f47ac10b.../responses \
  -H "Content-Type: application/json" \
  -d '{
    "node_id": "node_abc123",
    "source": "claude-opus",
    "content": "Top 3 Nischen: 1. AI-powered inventory mgmt..."
  }'
```

### 4. Session exportieren

```bash
curl http://localhost:5000/api/v2/sessions/f47ac10b.../export \
  -o session_export.json
```

---

## Vorteile von API v2

| Feature | Legacy API | API v2 |
|---------|-----------|--------|
| **Session Persistenz** | ❌ In-memory only | ✅ Disk-backed |
| **Naming Conflicts** | ❌ `research_sessions` kollidiert | ✅ SessionManager |
| **Unified Response Format** | ❌ Unterschiedliche Formate | ✅ Unified Response Object |
| **Export/Import** | ❌ Nicht vorhanden | ✅ JSON Export/Import |
| **Multi-Mode Support** | ❌ Separate APIs | ✅ Ein API für alle Modi |
| **Coverage Metrics** | ❌ Nur in Product Research | ✅ Für alle Modi verfügbar |
| **Axiom Alignment** | ❌ Nur in Sovereign | ✅ Für alle Modi verfügbar |

---

## Nächste Schritte

1. ✅ **Phase 1 (Complete):** Core API v2 Endpoints implementiert
2. 🔄 **Phase 2 (In Progress):** Frontend Migration
   - Update `ResearchCreator.vue` um v2 zu verwenden
   - Update `SovereignResearch.vue` um v2 zu verwenden
   - Neues Unified Dashboard
3. 📋 **Phase 3 (Planned):** Legacy API Deprecation
   - Deprecation Warnings zu alten Endpoints hinzufügen
   - Migration Guide für Benutzer
4. 🚀 **Phase 4 (Planned):** Advanced Features
   - Coverage Analysis in MCTS integrieren
   - Unified ResponseCollection Component
   - Thematic → ToT Workflow Übergang

---

## Support

**Fragen?** Siehe `docs/WORKFLOW_ANALYSIS_AND_UNIFICATION.md` für Details über die Vereinheitlichung der Systeme.
