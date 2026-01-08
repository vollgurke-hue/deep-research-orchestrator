# Critical Gaps & Solutions

**Version:** 1.0
**Date:** 2026-01-08
**Purpose:** Identify and solve critical problems in the architecture

---

## Overview: Die 7 kritischen Lücken

Nach gründlicher Analyse haben wir **7 kritische Schwachstellen** identifiziert, die das System in der Praxis scheitern lassen könnten:

| # | Problem | Impact | Lösung | Sprint |
|---|---------|--------|--------|--------|
| 1 | Graph-to-Prompt Übersetzung fehlt | ⚠️ HIGH | Context Compression Module | Sprint 1 |
| 2 | Keine Konflikt-Auflösung bei Widersprüchen | ⚠️ HIGH | Conflict Resolution System | Sprint 1 |
| 3 | RAM-Falle (32B + Graph + GUI = >16GB) | 🔴 CRITICAL | Resource Orchestrator | Sprint 1 |
| 4 | Blind development (keine Graph-Visualisierung) | ⚠️ HIGH | Graph Viewer → Sprint 1 | Sprint 1 |
| 5 | MCTS Utility Function zu simpel | ⚠️ MEDIUM | Enhanced Scoring (Ertrag/Zeit) | Sprint 2 |
| 6 | Keine Output-Veredlung | ⚠️ MEDIUM | Business Format Exporter | Sprint 4 |
| 7 | Human-in-the-Loop unklar | ⚠️ MEDIUM | Intervention Interface | Sprint 3 |

---

## 1. Graph-to-Prompt Serialisierung (CRITICAL)

### Das Problem

```python
# Was wir HABEN:
graph = nx.DiGraph()
graph.add_node("Tesla", type="company")
graph.add_node("Rivian", type="company")
graph.add_edge("Tesla", "Rivian", predicate="competes_with", weight=0.75)

# Was das LLM BRAUCHT:
prompt = "Analyze market competition..."  # ← Wie kommt der Graph hier rein?
```

**Der Fehler in den Docs:** Wir beschreiben, dass der Graph in Prompts übersetzt wird, aber **nicht WIE**.

### Die Herausforderung

- **Problem:** NetworkX Graph ist Python-Objekt, LLM braucht Text
- **Constraint:** Kontext-Fenster ist begrenzt (4096 tokens bei 8B Modellen)
- **Realität:** Ein Graph mit 1000 Nodes kann nicht komplett serialisiert werden

### Die Lösung: Context Compression Module

```python
class GraphToPromptSerializer:
    """
    Intelligente Kompression: Nur relevanter Sub-Graph wird serialisiert
    """

    def __init__(self, max_tokens=2000):
        self.max_tokens = max_tokens
        self.formats = {
            "markdown": self._to_markdown,
            "json": self._to_json,
            "narrative": self._to_narrative
        }

    def serialize(self, graph, focus_entity=None, depth=2, format="markdown"):
        """
        Extrahiere relevanten Sub-Graph und konvertiere zu Text

        Strategie:
        1. Wenn focus_entity gegeben: Ego-Graph mit Tiefe N
        2. Wenn kein focus: Top-K wichtigste Nodes (PageRank)
        3. Komprimiere zu lesbarlem Text
        """
        # 1. Extrahiere relevanten Sub-Graph
        if focus_entity:
            subgraph = nx.ego_graph(graph, focus_entity, radius=depth)
        else:
            # Nutze PageRank für wichtigste Nodes
            important_nodes = self._get_important_nodes(graph, top_k=20)
            subgraph = graph.subgraph(important_nodes)

        # 2. Konvertiere zu gewähltem Format
        text = self.formats[format](subgraph)

        # 3. Token-Budget prüfen
        tokens = self._estimate_tokens(text)
        if tokens > self.max_tokens:
            # Fallback: Reduziere Tiefe oder Top-K
            return self.serialize(graph, focus_entity, depth=depth-1, format=format)

        return text

    def _to_markdown(self, subgraph):
        """
        Markdown-Format: Am lesbarsten für LLMs

        Output:
        ## Entities
        - **Tesla** (company, confidence: 0.95)
        - **Rivian** (company, confidence: 0.85)

        ## Relationships
        - Tesla → competes_with → Rivian (weight: 0.75, source: reddit.com)
        - Tesla → produces → Model 3 (weight: 0.90, source: tesla.com)
        """
        lines = ["## Entities\n"]

        for node_id, data in subgraph.nodes(data=True):
            confidence = data.get('confidence', 0.0)
            node_type = data.get('type', 'unknown')
            lines.append(f"- **{node_id}** ({node_type}, confidence: {confidence:.2f})")

        lines.append("\n## Relationships\n")

        for source, target, data in subgraph.edges(data=True):
            predicate = data.get('predicate', 'related_to')
            weight = data.get('weight', 0.0)
            source_url = data.get('source', 'unknown')
            lines.append(
                f"- {source} → {predicate} → {target} "
                f"(weight: {weight:.2f}, source: {source_url})"
            )

        return "\n".join(lines)

    def _to_narrative(self, subgraph):
        """
        Narratives Format: Natürliche Sprache (für finale Synthese)

        Output:
        "Based on the knowledge graph, Tesla is a company that competes with
        Rivian. Tesla produces the Model 3. This information comes from
        reddit.com with a confidence of 0.75..."
        """
        sentences = []

        # Gruppiere nach Subjekt
        for node_id in subgraph.nodes():
            edges = list(subgraph.edges(node_id, data=True))

            if edges:
                node_data = subgraph.nodes[node_id]
                node_type = node_data.get('type', 'entity')

                # Erstelle Satz
                predicates = []
                for _, target, data in edges:
                    predicate = data.get('predicate', 'is related to')
                    predicates.append(f"{predicate} {target}")

                sentence = f"{node_id} ({node_type}) {', '.join(predicates)}."
                sentences.append(sentence)

        return " ".join(sentences)

    def _get_important_nodes(self, graph, top_k=20):
        """
        Finde wichtigste Nodes via PageRank

        Wichtigkeit = Wie zentral im Netzwerk?
        """
        pagerank = nx.pagerank(graph)
        sorted_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
        return [node for node, score in sorted_nodes[:top_k]]

    def _estimate_tokens(self, text):
        """
        Rough estimation: 1 token ≈ 4 characters
        """
        return len(text) // 4

    def serialize_with_context(self, graph, question, focus_entities=None):
        """
        HAUPT-METHODE: Serialisiere Graph mit Kontext für spezifische Frage

        Beispiel:
        Question: "Ist Tesla ein gutes Investment?"
        → Fokus auf Tesla + alle Nodes mit 'investment' relevanten Edges
        """
        # 1. Wenn focus_entities gegeben, nutze diese
        if focus_entities:
            subgraph_parts = [
                nx.ego_graph(graph, entity, radius=2)
                for entity in focus_entities
            ]
            subgraph = nx.compose_all(subgraph_parts)

        # 2. Sonst: Keyword-basierte Extraktion
        else:
            keywords = self._extract_keywords(question)
            relevant_nodes = self._find_nodes_by_keywords(graph, keywords)
            subgraph = graph.subgraph(relevant_nodes)

        # 3. Serialisiere
        return self._to_markdown(subgraph)

    def _extract_keywords(self, question):
        """Extrahiere Keywords aus Frage"""
        # Simple implementation (kann später mit NER erweitert werden)
        import re
        words = re.findall(r'\w+', question.lower())
        stopwords = {'ist', 'ein', 'der', 'die', 'das', 'und', 'oder'}
        return [w for w in words if w not in stopwords and len(w) > 3]

    def _find_nodes_by_keywords(self, graph, keywords):
        """Finde Nodes, die Keywords enthalten"""
        matching_nodes = []

        for node_id, data in graph.nodes(data=True):
            node_text = f"{node_id} {data.get('description', '')}".lower()

            if any(kw in node_text for kw in keywords):
                matching_nodes.append(node_id)

        # Wenn zu wenige: Nutze PageRank Fallback
        if len(matching_nodes) < 5:
            matching_nodes = self._get_important_nodes(graph, top_k=10)

        return matching_nodes
```

### Integration in Workflow

```python
# Im Orchestrator
class SovereignOrchestrator:
    def __init__(self):
        self.graph = GraphManager()
        self.serializer = GraphToPromptSerializer(max_tokens=2000)

    def run_mcts_evaluation(self, node_id):
        """
        MCTS Simulation braucht Graph-Kontext
        """
        # 1. Hole relevanten Sub-Graph
        focus_entity = self.tot_tree[node_id].main_entity
        graph_context = self.serializer.serialize_with_context(
            graph=self.graph.graph,
            question=self.tot_tree[node_id].question,
            focus_entities=[focus_entity]
        )

        # 2. Baue Prompt
        prompt = f"""
        # Research Question
        {self.tot_tree[node_id].question}

        # Relevant Knowledge Graph
        {graph_context}

        # Task
        Evaluate the success probability of pursuing this research path.
        Consider the facts above and simulate likely outcomes.
        """

        # 3. LLM Reasoning
        result = self.llm.generate(prompt)

        return result
```

---

## 2. Conflict Resolution System (CRITICAL)

### Das Problem

```python
# Szenario: Widersprüchliche Fakten
graph.add_edge("Market X", "is", "growing", source="forbes.com", confidence=0.85)
graph.add_edge("Market X", "is", "shrinking", source="reuters.com", confidence=0.80)

# Was jetzt? Beide im Graph? Welcher ist "wahr"?
```

**Der Fehler in den Docs:** Wir erwähnen Contradiction Check, aber nicht die **Auflösungs-Strategie**.

### Die Lösung: 3-Stufen Conflict Resolution

```python
class ConflictResolver:
    """
    Löst Widersprüche im Knowledge Graph
    """

    def __init__(self, graph_manager, tot_manager, scraper):
        self.graph = graph_manager
        self.tot = tot_manager
        self.scraper = scraper
        self.conflict_threshold = 0.5  # Unterschied >50% = Konflikt

    def detect_conflicts(self):
        """
        Finde widersprüchliche Edges im Graph

        Konflikt = Zwei Edges mit gleichem Subjekt + ähnlichem Prädikat
                   aber konträren Objekten
        """
        conflicts = []

        # Gruppiere Edges nach Subjekt
        edges_by_subject = defaultdict(list)
        for source, target, data in self.graph.graph.edges(data=True):
            edges_by_subject[source].append((target, data))

        # Prüfe auf Konflikte
        for subject, edges in edges_by_subject.items():
            for i, (target1, data1) in enumerate(edges):
                for target2, data2 in edges[i+1:]:
                    if self._is_contradictory(target1, target2, data1, data2):
                        conflicts.append({
                            "subject": subject,
                            "claim_1": (target1, data1),
                            "claim_2": (target2, data2),
                            "severity": self._calculate_severity(data1, data2)
                        })

        return conflicts

    def _is_contradictory(self, target1, target2, data1, data2):
        """
        Prüfe ob zwei Aussagen widersprüchlich sind

        Methoden:
        1. Antonyme (growing ↔ shrinking)
        2. Numerische Widersprüche (profitable ↔ unprofitable)
        3. LLM-basiert (für komplexe Fälle)
        """
        # 1. Einfache Antonyme
        antonym_pairs = [
            ("growing", "shrinking"),
            ("profitable", "unprofitable"),
            ("safe", "risky"),
            ("high", "low"),
            ("increasing", "decreasing")
        ]

        for word1, word2 in antonym_pairs:
            if (word1 in target1.lower() and word2 in target2.lower()) or \
               (word2 in target1.lower() and word1 in target2.lower()):
                return True

        # 2. Numerische Widersprüche
        # Beispiel: "growth rate 5%" vs "growth rate -3%"
        import re
        nums1 = re.findall(r'-?\d+\.?\d*', target1)
        nums2 = re.findall(r'-?\d+\.?\d*', target2)

        if nums1 and nums2:
            try:
                val1 = float(nums1[0])
                val2 = float(nums2[0])
                # Unterschiedliche Vorzeichen = Konflikt
                if (val1 > 0 and val2 < 0) or (val1 < 0 and val2 > 0):
                    return True
            except ValueError:
                pass

        # 3. LLM-Fallback (nur wenn unklar)
        # TODO: Implementieren wenn nötig

        return False

    def _calculate_severity(self, data1, data2):
        """
        Wie schwerwiegend ist der Konflikt?

        Severity = Durchschnittliche Confidence der beiden Quellen
        Hohe Confidence beider Seiten = Schwerer Konflikt
        """
        conf1 = data1.get('confidence', 0.5)
        conf2 = data2.get('confidence', 0.5)
        return (conf1 + conf2) / 2

    # === STUFE 1: Source Weighting ===
    def resolve_by_source_authority(self, conflict):
        """
        Löse Konflikt durch Quellen-Autorität

        Hierarchie (kann konfiguriert werden):
        1. Primärquellen (Geschäftsberichte, offizielle Statistiken)
        2. Etablierte Medien (Reuters, Bloomberg)
        3. Fachmedien (TechCrunch, etc.)
        4. Social Media (Reddit, Twitter)
        """
        source_authority = {
            # Tier 1: Höchste Autorität
            "sec.gov": 1.0,
            "statista.com": 0.95,
            "bloomberg.com": 0.90,
            "reuters.com": 0.85,

            # Tier 2: Etablierte Medien
            "forbes.com": 0.75,
            "techcrunch.com": 0.70,
            "wsj.com": 0.80,

            # Tier 3: Social / Community
            "reddit.com": 0.50,
            "twitter.com": 0.40,
            "medium.com": 0.45
        }

        claim1, data1 = conflict["claim_1"]
        claim2, data2 = conflict["claim_2"]

        source1 = data1.get('source', 'unknown')
        source2 = data2.get('source', 'unknown')

        # Extrahiere Domain
        domain1 = self._extract_domain(source1)
        domain2 = self._extract_domain(source2)

        auth1 = source_authority.get(domain1, 0.5)
        auth2 = source_authority.get(domain2, 0.5)

        # Kombiniere mit Confidence
        score1 = auth1 * data1.get('confidence', 0.5)
        score2 = auth2 * data2.get('confidence', 0.5)

        if abs(score1 - score2) > 0.2:  # Klarer Sieger
            winner = claim1 if score1 > score2 else claim2
            return {
                "resolution": "source_authority",
                "winner": winner,
                "confidence": max(score1, score2)
            }

        # Kein klarer Sieger → Stufe 2
        return None

    # === STUFE 2: Temporal Resolution ===
    def resolve_by_recency(self, conflict):
        """
        Löse durch Aktualität (neuere Daten gewinnen)

        Besonders relevant für Märkte (Daten von 2025 > Daten von 2023)
        """
        claim1, data1 = conflict["claim_1"]
        claim2, data2 = conflict["claim_2"]

        timestamp1 = data1.get('timestamp', datetime.min)
        timestamp2 = data2.get('timestamp', datetime.min)

        # Wenn >6 Monate Unterschied: Neuere Quelle gewinnt
        time_diff = abs((timestamp1 - timestamp2).days)

        if time_diff > 180:  # 6 Monate
            winner = claim1 if timestamp1 > timestamp2 else claim2
            return {
                "resolution": "recency",
                "winner": winner,
                "confidence": 0.7
            }

        return None

    # === STUFE 3: Active Resolution (ToT Expansion) ===
    def resolve_by_research(self, conflict):
        """
        Kann nicht automatisch gelöst werden
        → Erstelle neuen ToT-Branch für Recherche

        Dies ist der KERN der souveränen Logik:
        Statt zu raten, wird aktiv geforscht!
        """
        subject = conflict["subject"]
        claim1, data1 = conflict["claim_1"]
        claim2, data2 = conflict["claim_2"]

        # Erstelle Research-Frage
        research_question = f"""
        CONFLICT DETECTED:
        Source 1 ({data1.get('source')}): {subject} → {claim1}
        Source 2 ({data2.get('source')}): {subject} → {claim2}

        Research Task: Find primary source data or additional evidence
        to resolve this contradiction.
        """

        # Erstelle neuen ToT-Branch
        conflict_branch = self.tot.create_branch(
            parent_id="root",
            question=research_question,
            priority="high",  # Konflikte haben Priorität!
            metadata={
                "type": "conflict_resolution",
                "conflicting_claims": [claim1, claim2]
            }
        )

        # Triggere gezieltes Scraping
        self.scraper.targeted_search(
            query=f"{subject} recent data",
            sources=["statista.com", "sec.gov", "official statistics"],
            result_callback=lambda results: self._integrate_conflict_resolution(
                conflict_branch,
                results
            )
        )

        return {
            "resolution": "active_research",
            "branch_id": conflict_branch.node_id,
            "status": "pending"
        }

    def resolve_all(self):
        """
        Haupt-Methode: Löse alle Konflikte
        """
        conflicts = self.detect_conflicts()

        resolutions = []
        for conflict in conflicts:
            # Versuchs-Reihenfolge
            resolution = (
                self.resolve_by_source_authority(conflict) or
                self.resolve_by_recency(conflict) or
                self.resolve_by_research(conflict)
            )

            resolutions.append(resolution)

            # Update Graph basierend auf Lösung
            if resolution["resolution"] != "active_research":
                self._apply_resolution(conflict, resolution)

        return resolutions

    def _apply_resolution(self, conflict, resolution):
        """
        Wende Auflösung an: Markiere verlierende Edge als "disputed"
        """
        winner = resolution["winner"]
        claim1, data1 = conflict["claim_1"]
        claim2, data2 = conflict["claim_2"]

        loser = claim2 if winner == claim1 else claim1
        loser_data = data2 if winner == claim1 else data1

        # Markiere Loser als "disputed" (nicht löschen!)
        subject = conflict["subject"]
        self.graph.graph.edges[subject, loser]["disputed"] = True
        self.graph.graph.edges[subject, loser]["disputed_reason"] = resolution["resolution"]

        # Erhöhe Weight des Winners
        self.graph.graph.edges[subject, winner]["weight"] *= 1.2
```

---

## 3. Resource Orchestrator (CRITICAL - RAM-Falle)

### Das Problem

```
Szenario bei 16GB RAM + 11GB VRAM:

Gleichzeitig aktiv:
- Qwen 32B Q4_K_M: ~18GB (!) → SWAP hell
- NetworkX Graph (10k nodes): ~500MB
- Vue GUI + Vite: ~1GB
- Python Backend: ~500MB
- Browser (Chrome): ~2GB

Total: ~22GB → 6GB im SWAP → System crawls
```

**Der Fehler in den Docs:** Wir planen 32B Modell, aber rechnen nicht die Realität.

### Die Lösung: Dynamic Resource Orchestrator

```python
class ResourceOrchestrator:
    """
    Dynamisches Management von RAM/VRAM unter Hardware-Constraints

    Ziel: Niemals SWAP thrashing!
    """

    def __init__(self, vram_limit_gb=11, ram_limit_gb=16):
        self.vram_limit = vram_limit_gb
        self.ram_limit = ram_limit_gb
        self.active_services = {}
        self.model_tier_preference = "adaptive"  # or "force_tier1" / "force_tier2"

    def check_resources(self):
        """
        Prüfe aktuelle RAM/VRAM Nutzung
        """
        import psutil
        import torch

        ram_used = psutil.virtual_memory().used / (1024**3)  # GB
        ram_percent = psutil.virtual_memory().percent

        vram_used = 0
        if torch.cuda.is_available():
            vram_used = torch.cuda.memory_allocated() / (1024**3)  # GB

        return {
            "ram_used_gb": ram_used,
            "ram_percent": ram_percent,
            "vram_used_gb": vram_used,
            "swap_used": psutil.swap_memory().used / (1024**3)
        }

    def can_load_model(self, model_tier):
        """
        Prüfe ob Modell geladen werden kann ohne SWAP

        Model Tiers:
        - tier1 (8B): ~5-6GB VRAM
        - tier2 (32B): ~18GB VRAM → PROBLEM!
        - tier2_reduced (14B): ~9GB VRAM → OK
        """
        model_requirements = {
            "tier1": {"vram": 6, "ram": 2},
            "tier2": {"vram": 18, "ram": 4},  # NICHT MÖGLICH bei 11GB!
            "tier2_reduced": {"vram": 9, "ram": 3}  # DeepSeek-R1-14B
        }

        req = model_requirements[model_tier]
        current = self.check_resources()

        vram_available = self.vram_limit - current["vram_used_gb"]
        ram_available = self.ram_limit - current["ram_used_gb"]

        # Sicherheits-Puffer: 2GB RAM für System
        ram_safe = ram_available - 2

        return {
            "can_load": vram_available >= req["vram"] and ram_safe >= req["ram"],
            "vram_shortfall": max(0, req["vram"] - vram_available),
            "ram_shortfall": max(0, req["ram"] - ram_safe)
        }

    def select_optimal_model(self, task_type):
        """
        Wähle bestes verfügbares Modell für Task

        Adaptives Downgrading:
        - Wenn 32B nicht passt → 14B
        - Wenn 14B nicht passt → 8B
        """
        ideal_model = {
            "synthesis": "tier2",
            "final_report": "tier2",
            "axiom_critical": "tier2",
            "reasoning": "tier2_reduced",
            "extraction": "tier1"
        }.get(task_type, "tier1")

        # Prüfe ob ideal model möglich
        if self.can_load_model(ideal_model)["can_load"]:
            return ideal_model

        # Downgrade-Kette
        if ideal_model == "tier2":
            if self.can_load_model("tier2_reduced")["can_load"]:
                logging.warning(f"Downgrading {task_type}: tier2 → tier2_reduced (RAM constraint)")
                return "tier2_reduced"
            else:
                logging.warning(f"Downgrading {task_type}: tier2 → tier1 (RAM constraint)")
                return "tier1"

        elif ideal_model == "tier2_reduced":
            if not self.can_load_model("tier2_reduced")["can_load"]:
                logging.warning(f"Downgrading {task_type}: tier2_reduced → tier1")
                return "tier1"

        return "tier1"  # Fallback

    def pause_non_essential_services(self):
        """
        Pausiere GUI und andere Services für Heavy Tasks

        Use Case: Wenn 14B Modell für finale Synthese läuft
        → GUI kann kurz pausieren
        """
        services_to_pause = ["gui", "docs_viewer", "background_scrapers"]

        for service in services_to_pause:
            if service in self.active_services:
                self.active_services[service].pause()
                logging.info(f"Paused {service} to free RAM")

    def resume_services(self):
        """
        Reaktiviere pausierte Services
        """
        for service in self.active_services.values():
            if hasattr(service, 'paused') and service.paused:
                service.resume()

    def execute_with_resource_management(self, task_type, task_func):
        """
        Wrapper: Führe Task mit Resource-Management aus

        Ablauf:
        1. Prüfe Resources
        2. Wähle optimales Modell
        3. Pausiere Services wenn nötig
        4. Führe Task aus
        5. Reaktiviere Services
        """
        # 1. Prüfe
        resources = self.check_resources()
        if resources["swap_used"] > 1:  # >1GB SWAP = Problem
            logging.error("System already swapping! Aborting heavy task.")
            return None

        # 2. Wähle Modell
        model_tier = self.select_optimal_model(task_type)

        # 3. Pausiere wenn Tier 2
        if model_tier in ["tier2", "tier2_reduced"]:
            self.pause_non_essential_services()

        # 4. Führe aus
        try:
            result = task_func(model_tier)
        finally:
            # 5. Reaktiviere
            self.resume_services()

        return result
```

### Hardware-Realistische Empfehlung

```python
# NEUE Model-Konfiguration (realitätstauglich)
RECOMMENDED_MODELS = {
    "tier1_extraction": {
        "model": "llama-3.1-8b-instruct-q4_k_m",
        "vram": 5,
        "ram": 2,
        "speed": "fast",
        "use_cases": ["extraction", "entity_recognition", "simple_reasoning"]
    },

    "tier2_quality": {
        # NICHT Qwen 32B, sondern DeepSeek-R1-14B!
        "model": "deepseek-r1-distill-qwen-14b-q4_k_m",
        "vram": 9,  # Passt in 11GB mit Puffer
        "ram": 3,
        "speed": "medium",
        "use_cases": ["synthesis", "complex_reasoning", "final_report"]
    },

    # Backup für extreme RAM-Knappheit
    "tier1_reasoning": {
        "model": "deepseek-r1-distill-qwen-7b-q4_k_m",
        "vram": 6,
        "ram": 2,
        "speed": "fast",
        "use_cases": ["reasoning", "axiom_evaluation", "tot_decomposition"]
    }
}

# 32B Modelle NUR via External API!
EXTERNAL_TIER = {
    "tier3_giants": {
        "models": ["claude-3.5-sonnet", "gpt-4o", "gemini-1.5-pro"],
        "cost_per_1k_tokens": 0.015,
        "use_cases": ["exploration", "creative_ideation", "multi_perspective"]
    }
}
```

---

## 4. Graph Viewer → Sprint 1 (CRITICAL)

### Das Problem

**Original Roadmap:** Graph Viewer in Sprint 3
**Realität:** Du baust ein komplexes Graph-System blind!

### Die Lösung: Minimal Viable Graph Viewer in Sprint 1

```python
# Sprint 1 Ziel: Einfacher, aber funktionaler Viewer

# NICHT: Fancy D3.js mit Animationen
# SONDERN: Simple, aber nützlich

class MinimalGraphViewer:
    """
    Sprint 1: ASCII-basierter Graph Viewer für Terminal

    Sprint 3: Upgrade zu D3.js GUI
    """

    def print_graph_summary(self, graph):
        """
        Terminal-Output:

        === Knowledge Graph Summary ===
        Nodes: 47
        Edges: 123
        Top Entities (by PageRank):
          1. Tesla (0.15)
          2. Market X (0.12)
          3. ...

        Recent Additions:
          - [2026-01-08 14:32] Tesla → competes_with → Rivian
          - [2026-01-08 14:30] Market X → is → growing
        """
        import networkx as nx

        print("\n=== Knowledge Graph Summary ===")
        print(f"Nodes: {graph.number_of_nodes()}")
        print(f"Edges: {graph.number_of_edges()}")

        # PageRank
        pagerank = nx.pagerank(graph)
        top_entities = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]

        print("\nTop Entities (by importance):")
        for i, (entity, score) in enumerate(top_entities, 1):
            print(f"  {i}. {entity} ({score:.3f})")

        # Recent additions
        edges_with_time = [
            (s, t, d) for s, t, d in graph.edges(data=True)
            if 'timestamp' in d
        ]
        edges_with_time.sort(key=lambda x: x[2]['timestamp'], reverse=True)

        print("\nRecent Additions:")
        for s, t, d in edges_with_time[:5]:
            pred = d.get('predicate', '→')
            ts = d['timestamp'].strftime("%Y-%m-%d %H:%M")
            print(f"  - [{ts}] {s} → {pred} → {t}")

    def visualize_subgraph_ascii(self, graph, focus_entity, depth=2):
        """
        ASCII-Tree Visualisierung (wie `tree` command)

        Tesla
        ├── competes_with → Rivian
        ├── produces → Model 3
        │   └── has_price → $45,000
        └── based_in → USA
        """
        import networkx as nx

        subgraph = nx.ego_graph(graph, focus_entity, radius=depth)

        def print_tree(node, prefix="", visited=None):
            if visited is None:
                visited = set()

            if node in visited:
                return

            visited.add(node)
            print(prefix + str(node))

            children = list(subgraph.neighbors(node))
            for i, child in enumerate(children):
                edge_data = subgraph.edges[node, child]
                predicate = edge_data.get('predicate', '→')

                is_last = i == len(children) - 1
                connector = "└──" if is_last else "├──"
                child_prefix = "    " if is_last else "│   "

                print(f"{prefix}{connector} {predicate} → {child}")

                # Rekursiv (nur 1 Ebene tiefer um Übersicht zu behalten)
                if depth > 1:
                    print_tree(child, prefix + child_prefix, visited)

        print(f"\n=== Subgraph: {focus_entity} (depth={depth}) ===")
        print_tree(focus_entity)
```

---

## 5. Enhanced MCTS Utility Function

### Das Problem

**Aktuell:** `Q(node) = confidence_score`
**Real:** Wirtschaftliche Bewertung braucht **Ertrag/Zeit-Verhältnis**!

### Die Lösung: Multi-Dimensional Utility

```python
class EnhancedMCTSUtility:
    """
    Utility Function für wirtschaftliche Bewertung

    Dimensionen:
    1. Confidence (Wie sicher sind die Daten?)
    2. Potential Return (Wie hoch ist der Ertrag?)
    3. Time Investment (Wie viel Zeit kostet es?)
    4. Risk (Wie hoch ist das Risiko?)
    5. Axiom Alignment (Passt es zu meinen Werten?)
    """

    def calculate_utility(self, node, graph, axioms):
        """
        Utility Score = Weighted combination

        U = w1*Confidence + w2*(Return/Time) + w3*(1-Risk) + w4*AxiomScore
        """
        weights = {
            "confidence": 0.15,
            "roi_per_hour": 0.35,  # WICHTIGSTER Faktor!
            "risk_inverse": 0.20,
            "axiom_alignment": 0.30
        }

        # 1. Confidence (aus Graph)
        confidence = self._get_node_confidence(node, graph)

        # 2. ROI per Hour (simuliert oder geschätzt)
        roi_per_hour = self._estimate_roi_per_hour(node, graph)
        roi_normalized = min(1.0, roi_per_hour / 100)  # €100/h = 1.0

        # 3. Risk (inverse - niedriges Risiko = gut)
        risk = self._assess_risk(node, graph)
        risk_inverse = 1.0 - risk

        # 4. Axiom Alignment
        axiom_score = self._evaluate_axioms(node, graph, axioms)

        # Kombiniere
        utility = (
            weights["confidence"] * confidence +
            weights["roi_per_hour"] * roi_normalized +
            weights["risk_inverse"] * risk_inverse +
            weights["axiom_alignment"] * axiom_score
        )

        return utility, {
            "confidence": confidence,
            "roi_per_hour": roi_per_hour,
            "risk": risk,
            "axiom_alignment": axiom_score
        }

    def _estimate_roi_per_hour(self, node, graph):
        """
        Schätze ROI/Stunde aus Graph-Daten

        Wenn vorhanden:
        - Profit-Schätzung
        - Zeit-Investition-Schätzung
        → ROI/h = Profit / Zeit

        Sonst: LLM-basierte Schätzung
        """
        # Suche nach relevanten Edges
        profit_edges = [
            (s, t, d) for s, t, d in graph.edges(data=True)
            if 'profit' in d or 'revenue' in str(t).lower()
        ]

        time_edges = [
            (s, t, d) for s, t, d in graph.edges(data=True)
            if 'time' in d or 'hours' in str(t).lower()
        ]

        if profit_edges and time_edges:
            # Extrahiere Werte
            # ... (vereinfacht)
            return 75  # €75/h

        # Fallback: 0 (unbekannt)
        return 0
```

---

## 6. Output Veredler (Business Formats)

### Das Problem

**Aktuell:** Output = JSON + Markdown
**Real:** Kunden wollen **Pitch Decks, Investment Memos, GTM Strategien**

### Die Lösung: Template-basierter Export

```python
class OutputVeredler:
    """
    Wandelt Graph + Synthese in Business-Formate um
    """

    def export_investment_memo(self, graph, synthesis, template="standard"):
        """
        Investment Memo Format:

        ## Executive Summary
        - Opportunity: ...
        - Market Size: ...
        - Competitive Advantage: ...
        - Risk Factors: ...

        ## Market Analysis
        (Graph-basiert)

        ## Financial Projections
        (aus Simulationen)

        ## Risks & Mitigation
        (aus Contradiction Check)
        """
        pass

    def export_pitch_deck(self, graph, synthesis):
        """
        Generiere Markdown → PowerPoint-ready

        Slides:
        1. Problem
        2. Solution
        3. Market Size
        4. Business Model
        5. Competition
        6. Traction
        7. Ask
        """
        pass
```

---

## 7. Human Intervention Interface

### Die Lösung: Intervention Points

```python
class HumanInterventionInterface:
    """
    Definierte Punkte, an denen User eingreifen kann
    """

    def request_intervention(self, type, context):
        """
        Intervention Types:
        - "conflict": Widerspruch kann nicht automatisch gelöst werden
        - "axiom_violation": Path widerspricht kritischem Axiom
        - "uncertainty": MCTS kann nicht entscheiden
        - "manual_pruning": User will Branch manuell schneiden
        """
        # GUI zeigt Popup mit Optionen
        # User wählt: Continue / Prune / Research More
        pass
```

---

## Zusammenfassung: Änderungen am Roadmap

### Sprint 1 Updates (KRITISCH)

```diff
+ GraphToPromptSerializer implementieren
+ ConflictResolver (Basic) implementieren
+ ResourceOrchestrator implementieren
+ MinimalGraphViewer (ASCII) implementieren
- Graph Viewer D3.js (→ Sprint 3)
```

### Model Tier Changes

```diff
- Tier 2: Qwen 32B Q4_K_M (18GB VRAM - UNMÖGLICH!)
+ Tier 2: DeepSeek-R1-14B Q4_K_M (9GB VRAM - OK!)
+ Tier 3: External APIs für 32B+ Modelle
```

### Neue Module

1. `src/core/graph_serializer.py` (Sprint 1)
2. `src/core/conflict_resolver.py` (Sprint 1)
3. `src/core/resource_orchestrator.py` (Sprint 1)
4. `src/utils/minimal_graph_viewer.py` (Sprint 1)
5. `src/core/enhanced_mcts_utility.py` (Sprint 2)
6. `src/export/output_veredler.py` (Sprint 4)
7. `src/ui/intervention_interface.py` (Sprint 3)

---

## Nächste Schritte

1. **Roadmap updaten** mit neuen Modulen
2. **Schemas erstellen** für Conflict Resolution, Resource Management
3. **Sprint 1 Tasks** neu priorisieren (Graph Viewer FIRST!)

Willst du, dass ich den `IMPLEMENTATION_ROADMAP.md` jetzt mit diesen Fixes update?
