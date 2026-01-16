#!/usr/bin/env python3
"""
Simple Flask API Server (without viewer/livereload)
Only serves API endpoints for the Vue frontend
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

app = Flask(__name__)
CORS(app)  # Enable CORS for Vue frontend

# Import Sovereign Research components
from src.core.graph_manager import GraphManager
from src.core.axiom_manager import AxiomManager
from src.core.tot_manager import ToTManager
from src.core.mcts_engine import MCTSEngine
from src.core.model_orchestrator import ModelOrchestrator
from src.core.coverage_analyzer import CoverageAnalyzer
from src.core.graph_generator import GraphGenerator

# Import Unified Session Management
from src.core.session_manager import SessionManager
from src.models.unified_session import UnifiedSession, Response

# Global state - LEGACY (deprecated, use SessionManager instead)
# Separated to avoid conflicts between Product & Sovereign Research
legacy_product_sessions = {}  # For old Product Research endpoints (if needed)
legacy_sovereign_sessions = {}  # For old Sovereign Research endpoints

# NEW: Unified Session Manager (with persistence)
session_manager = SessionManager(sessions_dir="data/sessions")


@app.route('/api/status', methods=['GET'])
def api_status():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "mode": "mock",
        "version": "1.0"
    })


# ============================================================================
# SOVEREIGN RESEARCH API ENDPOINTS (Sprint 3)
# ============================================================================

@app.route('/api/sovereign/research/start', methods=['POST'])
def api_sovereign_research_start():
    """
    Start new sovereign research session with ToT/Graph/MCTS.

    Body: {
        "question": "What e-commerce niche should I explore?",
        "axiom_filters": ["opportunity_cost", "risk_tolerance"]  # optional
    }

    Returns: {
        "session_id": "uuid",
        "status": "exploring",
        "tot_root_id": "node_xyz"
    }
    """
    try:
        data = request.json
        question = data.get('question', '')
        axiom_filters = data.get('axiom_filters', None)

        if not question:
            return jsonify({"error": "question is required"}), 400

        # Create new session
        import uuid
        session_id = str(uuid.uuid4())

        # Initialize components
        graph = GraphManager()
        axiom_mgr = AxiomManager(axiom_dir="config/axioms")

        # Filter axioms if specified
        if axiom_filters:
            axiom_mgr.set_active_axioms(axiom_filters)

        orchestrator = ModelOrchestrator(profile="standard")
        tot = ToTManager(graph, axiom_mgr, orchestrator)
        mcts = MCTSEngine(tot, graph, axiom_mgr)

        # Create root ToT node
        root_node = tot.create_root(question)

        # Store session (LEGACY - will migrate to SessionManager)
        legacy_sovereign_sessions[session_id] = {
            "question": question,
            "graph": graph,
            "axiom_mgr": axiom_mgr,
            "tot": tot,
            "mcts": mcts,
            "status": "exploring",
            "created_at": time.time()
        }

        return jsonify({
            "session_id": session_id,
            "status": "exploring",
            "tot_root_id": root_node.node_id,
            "message": "Session created. Call /expand to decompose the question."
        }), 200

    except Exception as e:
        print(f"Error in sovereign_research_start: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/sovereign/research/<session_id>/tot-tree', methods=['GET'])
def api_sovereign_tot_tree(session_id):
    """
    Get current ToT tree structure.

    Returns: {
        "nodes": [{node_id, question, depth, status, confidence, axiom_scores}],
        "edges": [{parent_id, child_id}],
        "active_leaves": [node_ids]
    }
    """
    try:
        if session_id not in legacy_sovereign_sessions:
            return jsonify({"error": "Session not found"}), 404

        session = legacy_sovereign_sessions[session_id]
        tot = session["tot"]

        # Export tree
        nodes = []
        edges = []

        for node_id, node in tot.tree.items():
            nodes.append({
                "node_id": node.node_id,
                "parent_id": node.parent_id,
                "question": node.question,
                "answer": node.answer,
                "depth": node.depth,
                "status": node.status,
                "confidence": node.confidence,
                "axiom_scores": node.axiom_scores,
                "visits": node.visits,
                "value": node.value,
                "graph_entities": node.graph_entities
            })

            if node.parent_id:
                edges.append({
                    "parent_id": node.parent_id,
                    "child_id": node.node_id
                })

        active_leaves = [n.node_id for n in tot.get_active_leaves()]

        return jsonify({
            "nodes": nodes,
            "edges": edges,
            "active_leaves": active_leaves,
            "total_nodes": len(nodes)
        }), 200

    except Exception as e:
        print(f"Error in tot_tree: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/sovereign/research/<session_id>/graph', methods=['GET'])
def api_sovereign_graph(session_id):
    """
    Get knowledge graph (full or subgraph).

    Query params:
        ?focus=entity_id&depth=2  # Optional: Get subgraph around entity

    Returns: {
        "nodes": [{id, label, type, metadata}],
        "edges": [{source, target, relation, confidence}],
        "stats": {node_count, edge_count, density}
    }
    """
    try:
        if session_id not in legacy_sovereign_sessions:
            return jsonify({"error": "Session not found"}), 404

        session = legacy_sovereign_sessions[session_id]
        graph = session["graph"]

        focus = request.args.get('focus', None)
        depth = int(request.args.get('depth', 2))

        # Export graph
        if focus:
            subgraph = graph.get_subgraph(focus, depth=depth)
            export = graph.export_graph(subgraph)
        else:
            export = graph.export_graph()

        return jsonify(export), 200

    except Exception as e:
        print(f"Error in sovereign_graph: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/sovereign/research/<session_id>/expand', methods=['POST'])
def api_sovereign_expand(session_id):
    """
    Expand a ToT node (decompose question or send to external model).

    Body: {
        "node_id": "xyz",
        "method": "decompose" | "external",
        "external_model": "claude-opus"  # If method=external
    }

    Returns: {
        "node_id": "xyz",
        "children": [node_ids],
        "status": "expanded"
    }
    """
    try:
        if session_id not in legacy_sovereign_sessions:
            return jsonify({"error": "Session not found"}), 404

        data = request.json
        node_id = data.get('node_id', '')
        method = data.get('method', 'decompose')

        if not node_id:
            return jsonify({"error": "node_id is required"}), 400

        session = legacy_sovereign_sessions[session_id]
        tot = session["tot"]

        if method == "decompose":
            # Decompose with local LLM
            children = tot.decompose_question(node_id, branching_factor=3)

            return jsonify({
                "node_id": node_id,
                "children": [c.node_id for c in children],
                "status": "expanded",
                "method": "decompose"
            }), 200

        elif method == "external":
            external_model = data.get('external_model', 'claude-opus')

            # Generate prompt for external model (user copies manually)
            node = tot.tree[node_id]
            prompt = tot.generate_external_prompt(node)

            return jsonify({
                "node_id": node_id,
                "prompt": prompt,
                "instruction": f"Copy this prompt to {external_model}, then paste response back via /add-response",
                "status": "awaiting_response"
            }), 200

        else:
            return jsonify({"error": f"Unknown method: {method}"}), 400

    except Exception as e:
        print(f"Error in sovereign_expand: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/sovereign/research/<session_id>/add-response', methods=['POST'])
def api_sovereign_add_response(session_id):
    """
    Add external model response to ToT node.

    Body: {
        "node_id": "xyz",
        "response_text": "...",
        "model_name": "claude-opus" | "gpt-4" | "gemini-pro"
    }

    Returns: {
        "node_id": "xyz",
        "status": "evaluated",
        "confidence": 0.85,
        "entities_extracted": 15,
        "axiom_scores": {...}
    }
    """
    try:
        if session_id not in legacy_sovereign_sessions:
            return jsonify({"error": "Session not found"}), 404

        data = request.json
        node_id = data.get('node_id', '')
        response_text = data.get('response_text', '')
        model_name = data.get('model_name', 'external')

        if not node_id or not response_text:
            return jsonify({"error": "node_id and response_text required"}), 400

        session = legacy_sovereign_sessions[session_id]
        tot = session["tot"]

        # Add external response
        success = tot.add_external_response(node_id, response_text, model_name)

        if not success:
            return jsonify({"error": "Failed to add response"}), 500

        # Get updated node
        node = tot.tree[node_id]

        return jsonify({
            "node_id": node_id,
            "status": node.status,
            "confidence": node.confidence,
            "entities_extracted": len(node.graph_entities),
            "axiom_scores": node.axiom_scores,
            "axiom_compatible": node.axiom_compatible
        }), 200

    except Exception as e:
        print(f"Error in add_response: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/sovereign/research/<session_id>/prune', methods=['POST'])
def api_sovereign_prune(session_id):
    """
    Manually prune a ToT branch.

    Body: {
        "node_id": "xyz",
        "reason": "Low friction" | "Axiom conflict" | "User decision"
    }

    Returns: {
        "node_id": "xyz",
        "status": "pruned",
        "affected_descendants": [node_ids]
    }
    """
    try:
        if session_id not in legacy_sovereign_sessions:
            return jsonify({"error": "Session not found"}), 404

        data = request.json
        node_id = data.get('node_id', '')
        reason = data.get('reason', 'User decision')

        if not node_id:
            return jsonify({"error": "node_id is required"}), 400

        session = legacy_sovereign_sessions[session_id]
        tot = session["tot"]

        # Prune branch
        affected = tot.prune_branch(node_id, reason)

        return jsonify({
            "node_id": node_id,
            "status": "pruned",
            "reason": reason,
            "affected_descendants": affected
        }), 200

    except Exception as e:
        print(f"Error in sovereign_prune: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/sovereign/research/<session_id>/mcts-step', methods=['POST'])
def api_sovereign_mcts_step(session_id):
    """
    Run one MCTS iteration (select -> simulate -> backpropagate).

    Body: {
        "num_steps": 10  # Optional: Run multiple iterations
    }

    Returns: {
        "iterations": 10,
        "best_path": [node_ids],
        "best_value": 0.85,
        "status": "converged" | "exploring"
    }
    """
    try:
        if session_id not in legacy_sovereign_sessions:
            return jsonify({"error": "Session not found"}), 404

        data = request.json
        num_steps = data.get('num_steps', 1)

        session = legacy_sovereign_sessions[session_id]
        mcts = session["mcts"]

        # Run MCTS iterations
        for _ in range(num_steps):
            node_id = mcts.select()
            value = mcts.simulate(node_id)
            mcts.backpropagate(node_id, value)

        # Get best path
        best_path = mcts.best_path()
        best_value = mcts.tot.tree[best_path[-1]].value if best_path else 0.0

        return jsonify({
            "iterations": num_steps,
            "best_path": best_path,
            "best_value": best_value,
            "status": "exploring"
        }), 200

    except Exception as e:
        print(f"Error in mcts_step: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/sovereign/axioms', methods=['GET'])
def api_sovereign_axioms():
    """
    List all axioms.

    Returns: {
        "axioms": [{axiom_id, category, statement, priority, enabled}]
    }
    """
    try:
        axiom_mgr = AxiomManager(axiom_dir="config/axioms")
        axioms = axiom_mgr.list_axioms()

        return jsonify({
            "axioms": axioms,
            "total": len(axioms)
        }), 200

    except Exception as e:
        print(f"Error in sovereign_axioms: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/sovereign/axioms/<axiom_id>/evaluate', methods=['POST'])
def api_sovereign_axiom_evaluate(axiom_id):
    """
    Evaluate a graph node or ToT node against specific axiom.

    Body: {
        "session_id": "uuid",
        "node_id": "xyz",  # ToT node
        "node_type": "tot" | "graph"
    }

    Returns: {
        "axiom_id": "opportunity_cost",
        "node_id": "xyz",
        "score": 0.75,
        "reasoning": "...",
        "verdict": "supports" | "neutral" | "contradicts"
    }
    """
    try:
        data = request.json
        session_id = data.get('session_id', '')
        node_id = data.get('node_id', '')
        node_type = data.get('node_type', 'tot')

        if not session_id or not node_id:
            return jsonify({"error": "session_id and node_id required"}), 400

        if session_id not in legacy_sovereign_sessions:
            return jsonify({"error": "Session not found"}), 404

        session = legacy_sovereign_sessions[session_id]
        axiom_mgr = session["axiom_mgr"]

        if node_type == "tot":
            tot = session["tot"]
            node = tot.tree.get(node_id)
            if not node:
                return jsonify({"error": "ToT node not found"}), 404

            # Evaluate ToT node
            result = axiom_mgr.evaluate_tot_node(node, axiom_id)

        elif node_type == "graph":
            graph = session["graph"]
            # Evaluate graph node
            result = axiom_mgr.evaluate_graph_node(graph, node_id, axiom_id)

        else:
            return jsonify({"error": f"Unknown node_type: {node_type}"}), 400

        return jsonify(result), 200

    except Exception as e:
        print(f"Error in axiom_evaluate: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ============================================================================
# API V2: UNIFIED RESEARCH ENDPOINTS (SessionManager-based)
# ============================================================================

@app.route('/api/v2/sessions', methods=['POST'])
def api_v2_create_session():
    """
    Create new unified research session.

    Body: {
        "mode": "thematic" | "tot" | "unified",
        "title": "My Research Title",
        "goal": "Research question/goal",
        "description": "Detailed description" (optional, for thematic),
        "axioms": ["axiom_id1", "axiom_id2"] (optional, for tot/unified),
        "research_type": "product|market|scientific" (optional, for thematic)
    }

    Returns: {
        "session_id": "uuid",
        "mode": "unified",
        "status": "wizard",
        "message": "Session created successfully"
    }
    """
    try:
        data = request.json
        mode = data.get('mode', 'unified')
        title = data.get('title', '')
        goal = data.get('goal', '')
        description = data.get('description', '')
        axioms = data.get('axioms', [])
        research_type = data.get('research_type', 'product')

        if not title or not goal:
            return jsonify({"error": "title and goal are required"}), 400

        # Create session via SessionManager
        session = session_manager.create_session(
            mode=mode,
            title=title,
            goal=goal,
            description=description,
            axioms=axioms,
            research_type=research_type
        )

        return jsonify({
            "session_id": session.metadata.session_id,
            "mode": session.metadata.mode,
            "status": session.metadata.status,
            "created_at": session.metadata.created_at,
            "message": "Session created successfully"
        }), 201

    except Exception as e:
        print(f"Error in v2_create_session: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/v2/sessions', methods=['GET'])
def api_v2_list_sessions():
    """
    List all sessions (optionally filtered by mode).

    Query params:
        ?mode=thematic|tot|unified  # Optional filter

    Returns: {
        "sessions": [
            {
                "session_id": "uuid",
                "title": "...",
                "mode": "unified",
                "status": "exploring",
                "created_at": "...",
                "responses_count": 5,
                "coverage_metrics": {...}
            }
        ],
        "total": 10
    }
    """
    try:
        mode = request.args.get('mode', None)
        sessions = session_manager.list_sessions(mode=mode)

        return jsonify({
            "sessions": sessions,
            "total": len(sessions)
        }), 200

    except Exception as e:
        print(f"Error in v2_list_sessions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/v2/sessions/<session_id>', methods=['GET'])
def api_v2_get_session(session_id):
    """
    Get full session details.

    Returns: {
        "session": {
            "metadata": {...},
            "context": {...},
            "thematic": {...},
            "tot": {...},
            "graph": {...},
            "state": {...},
            "responses": [...],
            "prompts": [...]
        }
    }
    """
    try:
        session = session_manager.get_session(session_id)

        if not session:
            return jsonify({"error": "Session not found"}), 404

        return jsonify({
            "session": session.to_dict()
        }), 200

    except Exception as e:
        print(f"Error in v2_get_session: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/v2/sessions/<session_id>', methods=['DELETE'])
def api_v2_delete_session(session_id):
    """Delete session from memory and disk."""
    try:
        success = session_manager.delete_session(session_id)

        if not success:
            return jsonify({"error": "Session not found"}), 404

        return jsonify({
            "message": f"Session {session_id} deleted successfully"
        }), 200

    except Exception as e:
        print(f"Error in v2_delete_session: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/v2/sessions/<session_id>/initialize', methods=['POST'])
def api_v2_initialize_session(session_id):
    """
    Initialize session components based on mode.
    Creates ToT Manager, Graph Manager, MCTS Engine, etc.

    Body: {
        "branching_factor": 3  (optional, for ToT)
        "max_depth": 3         (optional, for ToT)
    }

    Returns: {
        "session_id": "uuid",
        "components_initialized": ["graph", "tot", "axiom_mgr", "mcts"],
        "status": "exploring"
    }
    """
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        data = request.json or {}
        branching_factor = data.get('branching_factor', 3)
        max_depth = data.get('max_depth', 3)

        components = []

        # Initialize Graph Manager (all modes need this)
        graph = GraphManager()
        session_manager.attach_components(session_id, graph_manager=graph)
        components.append("graph")

        # Initialize mode-specific components
        if session.metadata.mode in ['tot', 'unified']:
            # Axiom Manager
            axiom_mgr = AxiomManager(axioms_dir="config/axioms")
            # Note: Axioms are already loaded based on enabled=true in config
            # session.context.axioms contains user selection for filtering

            # Model Orchestrator
            orchestrator = ModelOrchestrator(profile="standard")

            # ToT Manager
            tot = ToTManager(graph, axiom_mgr, orchestrator)
            root_node = tot.create_root(session.context.goal)

            # Update session ToT structure
            session.tot.root_node_id = root_node.node_id
            session.tot.branching_factor = branching_factor
            session.tot.max_depth = max_depth
            session.tot.total_nodes = 1

            # Coverage Analyzer (for Coverage-Guided MCTS)
            coverage = CoverageAnalyzer(graph, tot, axiom_mgr)

            # MCTS Engine with Coverage-Guided selection and Adaptive Weight
            mcts = MCTSEngine(
                tot,
                graph,
                orchestrator,
                coverage_analyzer=coverage,
                coverage_weight=0.5,
                adaptive_weight=True  # Gemini's recommendation: 0.7 → 0.5 → 0.3
            )

            # Attach components
            session_manager.attach_components(
                session_id,
                graph_manager=graph,
                tot_manager=tot,
                axiom_manager=axiom_mgr,
                mcts_engine=mcts,
                orchestrator=orchestrator,
                coverage_analyzer=coverage
            )

            components.extend(["tot", "axiom_mgr", "mcts", "orchestrator", "coverage"])

        # Update session status
        session.metadata.status = "exploring"
        session_manager.update_session(session)

        return jsonify({
            "session_id": session_id,
            "components_initialized": components,
            "status": session.metadata.status,
            "root_node_id": session.tot.root_node_id if session.tot else None
        }), 200

    except Exception as e:
        print(f"Error in v2_initialize_session: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/v2/sessions/<session_id>/graph/generate-seed', methods=['POST'])
def api_v2_generate_seed_graph(session_id):
    """
    Generate a seed graph from research description using LLM.

    Body: {
        "research_description": "Description text...",
        "research_goal": "Goal text...",
        "value_profile_id": "Sovereign_Mindset_v1" (optional),
        "generation_params": {
            "max_nodes": 8,
            "min_nodes": 3,
            "edge_density": "medium",
            "include_value_tensions": true
        }
    }

    Returns: {
        "session_id": "uuid",
        "seed_graph": {
            "metadata": {...},
            "nodes": [...],
            "edges": [...],
            "value_tensions": [...]
        }
    }
    """
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        data = request.json or {}
        description = data.get('research_description', session.context.description)
        goal = data.get('research_goal', session.context.goal)
        value_profile_id = data.get('value_profile_id')
        params = data.get('generation_params', {})

        if not description and not goal:
            return jsonify({"error": "Either research_description or research_goal is required"}), 400

        # Initialize LLM provider for graph generation
        # Use the orchestrator's default provider
        orchestrator = ModelOrchestrator(profile="standard")
        llm_provider = orchestrator.llm_manager.provider  # Get the active provider

        # Create graph generator
        graph_gen = GraphGenerator(llm_provider)

        # Generate seed graph
        print(f"Generating seed graph for session {session_id}...")
        graph_data = graph_gen.generate_from_description(
            description=description,
            goal=goal,
            value_profile_id=value_profile_id,
            params=params
        )

        # Convert to dataclass and store in session
        graph_structure = graph_gen.graph_to_dataclass(graph_data)
        session.graph = graph_structure

        # Update session
        session_manager.update_session(session)

        print(f"✓ Seed graph generated: {len(graph_structure.nodes)} nodes, {len(graph_structure.edges)} edges")

        return jsonify({
            "session_id": session_id,
            "seed_graph": graph_data  # Return dict for frontend, not dataclass
        }), 200

    except Exception as e:
        print(f"Error generating seed graph: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/v2/sessions/<session_id>/responses', methods=['POST'])
def api_v2_add_response(session_id):
    """
    Add an AI response to the session (unified format).

    Body: {
        "node_id": "xyz" (optional, for ToT/thematic node),
        "source": "claude-opus" | "gpt-4" | "gemini-pro" | "local-llm",
        "content": "Full response text...",
        "relevance_score": 0.85 (optional),
        "accuracy_score": 0.90 (optional),
        "confidence": 0.87 (optional)
    }

    Returns: {
        "response_id": "uuid",
        "entities_extracted": 12,
        "axiom_evaluation": {...},
        "axiom_compatible": true
    }
    """
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        data = request.json
        node_id = data.get('node_id', None)
        source = data.get('source', 'external')
        content = data.get('content', '')

        if not content:
            return jsonify({"error": "content is required"}), 400

        # Create unified response object
        import uuid as uuid_lib
        response_id = str(uuid_lib.uuid4())

        response = Response(
            response_id=response_id,
            node_id=node_id,
            source=source,
            content=content,
            timestamp=datetime.utcnow().isoformat(),
            relevance_score=data.get('relevance_score', 0.0),
            accuracy_score=data.get('accuracy_score', 0.0),
            confidence=data.get('confidence', 0.0)
        )

        # Process response based on mode
        if session.metadata.mode in ['tot', 'unified']:
            # Get ToT Manager
            tot = session_manager.get_component(session_id, 'tot_manager')

            if tot and node_id:
                # Add to ToT node (extracts entities, evaluates axioms)
                success = tot.add_external_response(node_id, content, source)

                if success:
                    node = tot.tree[node_id]
                    response.confidence = node.confidence
                    response.entities_extracted = node.graph_entities
                    response.graph_facts_added = node.graph_facts
                    response.axiom_evaluation = {
                        "scores": node.axiom_scores,
                        "compatible": node.axiom_compatible
                    }
                    response.axiom_compatible = node.axiom_compatible

        # Add response to session
        session.add_response(response)
        session_manager.update_session(session)

        return jsonify({
            "response_id": response_id,
            "entities_extracted": len(response.entities_extracted),
            "axiom_evaluation": response.axiom_evaluation,
            "axiom_compatible": response.axiom_compatible
        }), 201

    except Exception as e:
        print(f"Error in v2_add_response: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/v2/sessions/<session_id>/export', methods=['GET'])
def api_v2_export_session(session_id):
    """
    Export session as JSON file.

    Returns: JSON download
    """
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        # Export to file
        export_path = session_manager.export_session(session_id)

        # Return file content
        with open(export_path, 'r', encoding='utf-8') as f:
            content = f.read()

        from flask import Response as FlaskResponse
        return FlaskResponse(
            content,
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename=session_{session_id[:8]}.json'
            }
        )

    except Exception as e:
        print(f"Error in v2_export_session: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/v2/sessions/stats', methods=['GET'])
def api_v2_session_stats():
    """Get session statistics."""
    try:
        stats = session_manager.get_stats()
        return jsonify(stats), 200

    except Exception as e:
        print(f"Error in v2_session_stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Configuration loading endpoints for Dashboard & Docs
# ============================================================================
@app.route('/api/frameworks', methods=['GET'])
def api_frameworks():
    """List all available frameworks."""
    try:
        frameworks_dir = Path("config/frameworks")
        frameworks = []
        for file in frameworks_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    frameworks.append({
                        "framework_id": file.stem,
                        "name": data.get("name", file.stem),
                        "description": data.get("description", ""),
                        **data
                    })
            except Exception as e:
                print(f"Error loading framework {file}: {e}")
        return jsonify({"frameworks": frameworks})
    except Exception as e:
        return jsonify({"frameworks": []})


@app.route('/api/framework/<framework_id>', methods=['GET'])
def api_framework(framework_id):
    """Get a single framework by ID."""
    try:
        file_path = Path(f"config/frameworks/{framework_id}.json")
        if not file_path.exists():
            return jsonify({"error": "Framework not found"}), 404

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return jsonify({
                "framework_id": framework_id,
                "name": data.get("name", framework_id),
                **data
            })
    except Exception as e:
        print(f"Error loading framework {framework_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/workflows', methods=['GET'])
def api_workflows():
    """List all available workflows."""
    try:
        workflows = []
        for workflow_dir in Path("config/workflows").glob("*"):
            if workflow_dir.is_dir():
                for file in workflow_dir.glob("*.json"):
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            workflows.append({
                                "workflow_id": file.stem,
                                "name": data.get("name", file.stem),
                                "type": workflow_dir.name,
                                **data
                            })
                    except Exception as e:
                        print(f"Error loading workflow {file}: {e}")
        return jsonify({"workflows": workflows})
    except Exception as e:
        return jsonify({"workflows": []})


@app.route('/api/workflow/<workflow_id>', methods=['GET'])
def api_workflow(workflow_id):
    """Get a single workflow by ID."""
    try:
        # Search in all workflow subdirectories
        for workflow_dir in Path("config/workflows").glob("*"):
            if workflow_dir.is_dir():
                file_path = workflow_dir / f"{workflow_id}.json"
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return jsonify({
                            "workflow_id": workflow_id,
                            "name": data.get("name", workflow_id),
                            "type": workflow_dir.name,
                            **data
                        })
        return jsonify({"error": "Workflow not found"}), 404
    except Exception as e:
        print(f"Error loading workflow {workflow_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/techniques', methods=['GET'])
def api_techniques():
    """List all available techniques."""
    try:
        techniques_dir = Path("config/techniques")
        techniques = []
        for file in techniques_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    techniques.append({
                        "technique_id": file.stem,
                        "name": data.get("name", file.stem),
                        **data
                    })
            except Exception as e:
                print(f"Error loading technique {file}: {e}")
        return jsonify({"techniques": techniques})
    except Exception as e:
        return jsonify({"techniques": []})


@app.route('/api/technique/<technique_id>', methods=['GET'])
def api_technique(technique_id):
    """Get a single technique by ID."""
    try:
        file_path = Path(f"config/techniques/{technique_id}.json")
        if not file_path.exists():
            return jsonify({"error": "Technique not found"}), 404

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return jsonify({
                "technique_id": technique_id,
                "name": data.get("name", technique_id),
                **data
            })
    except Exception as e:
        print(f"Error loading technique {technique_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/phases', methods=['GET'])
def api_phases():
    """List all available phases."""
    try:
        phases_dir = Path("config/phases")
        phases = []
        if phases_dir.exists():
            for file in phases_dir.glob("*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        phases.append({
                            "phase_id": file.stem,
                            "name": data.get("name", file.stem),
                            **data
                        })
                except Exception as e:
                    print(f"Error loading phase {file}: {e}")
        return jsonify({"phases": phases})
    except Exception as e:
        return jsonify({"phases": []})


@app.route('/api/phase/<phase_id>', methods=['GET'])
def api_phase(phase_id):
    """Get a single phase by ID."""
    try:
        file_path = Path(f"config/phases/{phase_id}.json")
        if not file_path.exists():
            return jsonify({"error": "Phase not found"}), 404

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return jsonify({
                "phase_id": phase_id,
                "name": data.get("name", phase_id),
                **data
            })
    except Exception as e:
        print(f"Error loading phase {phase_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/docs', methods=['GET'])
def api_docs():
    """List all available documentation files categorized by type."""
    try:
        docs_dir = Path("docs")
        guides_dir = docs_dir / "guides"

        guides = []
        architecture = []
        frameworks = []

        # Scan guides subdirectory
        if guides_dir.exists():
            for file in guides_dir.glob("*.md"):
                guides.append({
                    "name": file.stem.replace("-", " ").replace("_", " ").title(),
                    "path": f"docs/guides/{file.name}"
                })

        # Scan main docs directory for architecture-related files
        if docs_dir.exists():
            architecture_keywords = ['architecture', 'concept', 'implementation', 'analysis', 'pipeline']
            for file in docs_dir.glob("*.md"):
                name_lower = file.stem.lower()
                if any(keyword in name_lower for keyword in architecture_keywords):
                    architecture.append({
                        "name": file.stem.replace("-", " ").replace("_", " ").title(),
                        "path": f"docs/{file.name}"
                    })

        return jsonify({
            "guides": guides,
            "architecture": architecture,
            "frameworks": frameworks  # Empty for now, could add framework docs later
        })
    except Exception as e:
        print(f"Error listing docs: {e}")
        return jsonify({"guides": [], "architecture": [], "frameworks": []})


@app.route('/api/docs/<path:filename>', methods=['GET'])
def api_docs_file(filename):
    """Return raw markdown content for a documentation file."""
    try:
        # Security: only allow .md files and prevent directory traversal
        if not filename.endswith('.md'):
            return "Only markdown files allowed", 400

        # Try to find the file in docs/ or project root
        file_path = Path(filename)

        # Check if it's in docs/ subdirectory
        if not file_path.exists():
            # Try project root
            file_path = Path(file_path.name)

        if not file_path.exists():
            return f"Documentation file not found: {filename}", 404

        # Read and return raw markdown content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    except Exception as e:
        print(f"Error loading doc file {filename}: {e}")
        import traceback
        traceback.print_exc()
        return f"Error loading file: {str(e)}", 500


@app.route('/api/orchestrator/reload', methods=['POST'])
def api_orchestrator_reload():
    """Stub for orchestrator reload (not used in Mock Mode)"""
    return jsonify({"status": "ok", "message": "Mock mode - no reload needed"})


# ============================================================================
# API V2: COVERAGE-GUIDED MCTS ENDPOINTS (Gemini's Ultimate Synergy!)
# ============================================================================

@app.route('/api/v2/sessions/<session_id>/coverage', methods=['GET'])
def api_v2_get_coverage(session_id):
    """Get overall coverage analysis for session."""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        coverage = getattr(session, '_coverage_analyzer', None)
        if not coverage:
            return jsonify({"error": "Coverage analysis not available"}), 400

        report = coverage.get_overall_research_coverage()
        return jsonify(report), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/v2/sessions/<session_id>/mcts/coverage-guided', methods=['POST'])
def api_v2_run_coverage_guided_mcts(session_id):
    """Run Coverage-Guided MCTS (THE ULTIMATE SYNERGY!)."""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        mcts = session_manager.get_component(session_id, 'mcts_engine')
        if not mcts:
            return jsonify({"error": "MCTS not initialized"}), 400

        data = request.json or {}
        num_iterations = data.get('num_iterations', 10)

        # Run Coverage-Guided MCTS
        mcts.iterate(num_iterations=num_iterations)

        # Get results
        best_path = mcts.best_path()
        stats = mcts.get_stats()
        suggestions = mcts.get_coverage_guided_suggestions(top_n=5)

        return jsonify({
            "iterations": num_iterations,
            "best_path": best_path,
            "stats": stats,
            "suggestions": suggestions,
            "message": "Coverage-guided MCTS completed! Prioritized low-coverage areas."
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Deep Research Orchestrator - API Server (Mock Mode)")
    print("=" * 60)
    print()
    print("📡 API Server:     http://localhost:5000")
    print("🎨 Vue Frontend:   http://localhost:5173")
    print()
    print("✓ Mock Mode: ACTIVE (no llama-server needed)")
    print("✓ CORS: Enabled for Vue frontend")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    app.run(host='0.0.0.0', port=5000, debug=True)
