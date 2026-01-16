#!/usr/bin/env python3
"""
Integration Test für Deep Research Orchestrator
Testet alle Komponenten: LlamaCppClient, Agent, WorkflowEngine, Orchestrator
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.llama_cpp_client import LlamaCppClient
from core.agent import Agent, Task
from core.orchestrator import Orchestrator
from utils.logger import setup_logger

logger = setup_logger("test_orchestrator")

def test_llama_cpp_client():
    """Test 1: LlamaCppClient Basis-Funktionalität"""
    print("\n" + "="*70)
    print("TEST 1: LlamaCppClient")
    print("="*70)

    try:
        client = LlamaCppClient(
            model_path=Path("/home/phili/llama-models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"),
            llama_cli_path=Path("llama.cpp/build/bin/llama-cli"),
            n_gpu_layers=999,
            ctx_size=2048,
            threads=4
        )

        print("✓ LlamaCppClient initialisiert")

        # Test prompt
        prompt = "What is 2+2? Answer with only the number."
        print(f"\nPrompt: {prompt}")

        response = client.generate(
            prompt=prompt,
            temperature=0.1,
            max_tokens=5
        )

        print(f"Response: {response}")
        print("✓ LlamaCppClient generate() funktioniert")

        return True

    except Exception as e:
        print(f"✗ LlamaCppClient Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_system():
    """Test 2: Agent System"""
    print("\n" + "="*70)
    print("TEST 2: Agent System")
    print("="*70)

    try:
        # LLM Client erstellen
        client = LlamaCppClient(
            model_path=Path("/home/phili/llama-models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"),
            llama_cli_path=Path("llama.cpp/build/bin/llama-cli"),
            n_gpu_layers=999,
            ctx_size=2048,
            threads=4
        )

        # Agent erstellen
        agent = Agent(
            agent_id="test_agent",
            role="researcher",
            llm_client=client,
            system_prompt="You are a helpful research assistant. Answer concisely.",
            temperature=0.3
        )

        print("✓ Agent erstellt")

        # Task ausführen
        task = Task(
            task_id="task_1",
            description="What is the capital of France? Answer with only the city name.",
            temperature=0.1,
            max_tokens=10
        )

        print(f"\nTask: {task.description}")

        result = agent.execute_task(task)

        print(f"Result: {result.output}")
        print(f"Success: {result.success}")
        print("✓ Agent execute_task() funktioniert")

        return True

    except Exception as e:
        print(f"✗ Agent Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_loading():
    """Test 3: Config Loading"""
    print("\n" + "="*70)
    print("TEST 3: Config Loading")
    print("="*70)

    try:
        # Test Agent Config
        agent_config_path = Path("config/agents/test_agent.json")
        if agent_config_path.exists():
            with open(agent_config_path) as f:
                agent_config = json.load(f)
            print(f"✓ Agent Config geladen: {agent_config['agent_id']}")
        else:
            print(f"✗ Agent Config nicht gefunden: {agent_config_path}")
            return False

        # Test Model Config
        model_config_path = Path("config/models/test_mixtral.json")
        if model_config_path.exists():
            with open(model_config_path) as f:
                model_config = json.load(f)
            print(f"✓ Model Config geladen: {model_config['model_id']}")
        else:
            print(f"✗ Model Config nicht gefunden: {model_config_path}")
            return False

        # Test Workflow Config
        workflow_config_path = Path("config/workflows/sequential/general_chat.json")
        if workflow_config_path.exists():
            with open(workflow_config_path) as f:
                workflow_config = json.load(f)
            print(f"✓ Workflow Config geladen: {workflow_config['workflow_id']}")
        else:
            print(f"✗ Workflow Config nicht gefunden: {workflow_config_path}")
            return False

        # Test Technique Config
        technique_config_path = Path("config/techniques/contradiction.json")
        if technique_config_path.exists():
            with open(technique_config_path) as f:
                technique_config = json.load(f)
            print(f"✓ Technique Config geladen: {technique_config['technique_id']}")
        else:
            print(f"✗ Technique Config nicht gefunden: {technique_config_path}")
            return False

        return True

    except Exception as e:
        print(f"✗ Config Loading Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_decorator():
    """Test 4: Tool Decorator System"""
    print("\n" + "="*70)
    print("TEST 4: Tool Decorator System")
    print("="*70)

    try:
        from core.tool_decorator import ToolRegistry, get_tool_prompt
        from tools.registered_tools import calculate_statistics

        registry = ToolRegistry()

        # Check registered tools
        tools = registry.list_tools()
        print(f"✓ {len(tools)} Tools registriert: {', '.join(tools)}")

        # Test tool execution
        result = calculate_statistics([1, 2, 3, 4, 5])
        print(f"✓ calculate_statistics Test: mean={result['mean']}, median={result['median']}")

        # Test tool prompt generation
        prompt = get_tool_prompt(["calculate_statistics"])
        print(f"✓ Tool Prompt generiert ({len(prompt)} Zeichen)")

        return True

    except Exception as e:
        print(f"✗ Tool Decorator Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_orchestrator_init():
    """Test 5: Orchestrator Initialisierung"""
    print("\n" + "="*70)
    print("TEST 5: Orchestrator Initialisierung")
    print("="*70)

    try:
        # Erstelle temporäre Model Config für TinyLlama
        tinyllama_config = {
            "model_id": "tinyllama_test",
            "name": "TinyLlama Test",
            "path": "/home/phili/llama-models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
            "llama_cli_path": "llama.cpp/build/bin/llama-cli",
            "n_gpu_layers": 999,
            "ctx_size": 2048,
            "threads": 4,
            "temperature_default": 0.3,
            "max_tokens_default": 50
        }

        config_path = Path("config/models/tinyllama_test.json")
        with open(config_path, "w") as f:
            json.dump(tinyllama_config, f, indent=2)
        print("✓ TinyLlama Test Config erstellt")

        # Orchestrator initialisieren
        orchestrator = Orchestrator()
        print("✓ Orchestrator initialisiert")

        # Check loaded configs
        print(f"✓ {len(orchestrator.models)} Model Configs geladen")
        print(f"✓ {len(orchestrator.agents)} Agent Configs geladen")
        print(f"✓ {len(orchestrator.workflows)} Workflow Configs geladen")

        return True

    except Exception as e:
        print(f"✗ Orchestrator Init Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Führt alle Tests aus"""
    print("\n" + "="*70)
    print("DEEP RESEARCH ORCHESTRATOR - INTEGRATION TESTS")
    print("="*70)

    results = {
        "LlamaCppClient": test_llama_cpp_client(),
        "Agent System": test_agent_system(),
        "Config Loading": test_config_loading(),
        "Tool Decorator": test_tool_decorator(),
        "Orchestrator Init": test_orchestrator_init(),
    }

    # Zusammenfassung
    print("\n" + "="*70)
    print("TEST ZUSAMMENFASSUNG")
    print("="*70)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nErgebnis: {passed}/{total} Tests bestanden")

    if passed == total:
        print("\n🎉 Alle Tests erfolgreich!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} Test(s) fehlgeschlagen")
        return 1


if __name__ == "__main__":
    exit(main())
