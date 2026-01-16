# Archived TODOs - 2026-01-15

**Status:** Implementation paused for strategic reorientation
**Context:** Mid-implementation of Seed Graph feature (Gemini v2.0 schema)

---

## Completed Work

### ✅ Backend Infrastructure
1. **Updated Seed Graph Schema** - Created comprehensive schema in `docs/SEED_GRAPH_SCHEMA.md` based on Gemini's refined design
   - Simplified node types: `concept`, `technical`, `alternative`
   - Node status: `defined`, `gap`, `potential_conflict`
   - Edge relations: `supports`, `requires`, `conflicts_with`, `enables`, `informs`, `constrains`, `risks`
   - Value tensions integration

2. **Updated UnifiedSession Model** - Extended `src/models/unified_session.py`
   - Added `SeedGraphMetadata`, `SeedGraphNode`, `SeedGraphEdge`, `ValueTension` dataclasses
   - Updated `GraphStructure` to support Gemini v2.0 schema
   - Backward compatibility with NetworkX legacy graph

3. **Implemented Graph Generator** - Created `src/core/graph_generator.py`
   - LLM-based extraction from research descriptions
   - Prompt engineering for node/edge identification
   - JSON parsing with fallback handling
   - Graph validation and enhancement

4. **Created Backend Endpoint** - `POST /api/v2/sessions/{id}/graph/generate-seed`
   - Integrated with SessionManager
   - Uses ModelOrchestrator for LLM access
   - Returns Gemini v2.0 schema JSON

---

## Pending Work (when resuming)

### 🔄 Testing & Validation
- **Test backend endpoint** - Initial test returned 0 nodes (needs debugging)
  - Check LLM provider integration
  - Verify JSON parsing
  - Test with mock/real LLM responses

### 📊 Frontend Implementation
- **Install D3.js** - `cd gui && npm install d3`
- **Create SeedGraphEditor.vue** - D3.js force-directed graph visualization
  - Interactive node/edge editing
  - Coverage color coding
  - Value tensions highlighting
- **Integrate into ResearchCreator** - Replace Step 1 hierarchy with graph editor
- **Implement relation color coding** - Visual distinction for edge types
- **Add value tensions to Working State widget**

---

## Technical Context

### Key Files Modified
- `docs/SEED_GRAPH_SCHEMA.md` - Complete schema documentation
- `src/models/unified_session.py` - Extended with graph dataclasses
- `src/core/graph_generator.py` - LLM-based graph extraction
- `api_server.py` - New endpoint at line 782

### Architecture Decisions
- **Graph-first approach**: Relationships as first-class citizens
- **Force-directed D3.js layout**: Interactive physics simulation
- **Flat session data model**: No nested metadata/context
- **All sessions = "unified" mode**: User decides workflow during research

### Integration Points
- ResearchCreator Step 0 → Generate Graph button → Step 1 Graph Editor
- Graph nodes → Prompt generation (Step 2)
- Responses pinned to nodes → Coverage updates (Step 3)

---

## Notes for Future Resume

1. **LLM Provider Issue**: Check `orchestrator.llm_manager.provider` access - may need to use `orchestrator.query()` directly
2. **Mock Mode**: Server running in mock mode - consider testing with real LLM first
3. **D3.js Version**: Use latest D3 v7 (force simulation API)
4. **Value Profiles**: Optional feature - can be implemented later

---

**Archived by:** Claude Code
**Reason:** Strategic reorientation - new concepts defined during planning week
