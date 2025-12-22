"""
Master Orchestrator for deep research workflows.

Inspired by GPT-Researcher's Master-Worker pattern.
Coordinates multiple agents and manages workflow execution.
"""
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
from dataclasses import dataclass

from src.models.llama_cpp_client import LlamaCppClient
from src.core.agent import Agent, Task, AgentOutput
from src.core.workflow_engine import WorkflowEngine
from src.core.state_manager import StateManager
from src.utils.json_loader import JSONLoader
from src.utils.logger import setup_logger


@dataclass
class OrchestrationResult:
    """Result from workflow orchestration."""

    workflow_id: str
    status: str  # "completed", "failed", "partial"
    iterations: int
    confidence: float
    outputs: List[AgentOutput]
    final_report: Optional[str] = None
    metadata: Dict[str, Any] = None


class Orchestrator:
    """
    Master orchestrator for research workflows.

    Coordinates agents, manages workflows, tracks state.
    """

    def __init__(
        self,
        config_dir: Path = Path("config"),
        models_dir: Path = Path("models"),
        llama_cli_path: Path = Path("llama.cpp/build/bin/llama-cli")
    ):
        """
        Initialize orchestrator.

        Args:
            config_dir: Path to config directory
            models_dir: Path to models directory
            llama_cli_path: Path to llama-cli binary
        """
        self.config_dir = config_dir
        self.models_dir = models_dir
        self.llama_cli_path = llama_cli_path

        self.logger = setup_logger("orchestrator")

        # Load configurations
        self.agents: Dict[str, Agent] = {}
        self.workflows: Dict[str, Dict] = {}
        self.models: Dict[str, Dict] = {}

        # Initialize engines
        self.workflow_engine = WorkflowEngine(self)
        self.state_manager = StateManager()

        # Load configs
        self._load_model_configs()
        self._load_agent_configs()
        self._load_workflow_configs()

        self.logger.info("Orchestrator initialized")

    def _load_model_configs(self):
        """Load model configurations."""
        models_dir = self.config_dir / "models"
        if not models_dir.exists():
            self.logger.warning(f"Models config dir not found: {models_dir}")
            return

        for config_file in models_dir.glob("*.json"):
            config = JSONLoader.load(config_file)
            self.models[config["model_id"]] = config
            self.logger.debug(f"Loaded model config: {config['model_id']}")

    def _load_agent_configs(self):
        """Load agent configurations."""
        agents_dir = self.config_dir / "agents"
        if not agents_dir.exists():
            self.logger.warning(f"Agents config dir not found: {agents_dir}")
            return

        for config_file in agents_dir.glob("*.json"):
            config = JSONLoader.load(config_file)

            # Create LLM client for agent's model
            model_tier = config.get("model_tier", "tier1_fast")
            llm_client = self._create_llm_client(model_tier)

            # Create agent
            agent = Agent(
                agent_id=config["agent_id"],
                role=config["role"],
                llm_client=llm_client,
                tools=config.get("tools", []),
                system_prompt=config.get("system_prompt"),
                temperature=config.get("temperature", 0.7)
            )

            self.agents[config["agent_id"]] = agent
            self.logger.debug(f"Loaded agent: {config['agent_id']}")

    def _load_workflow_configs(self):
        """Load workflow configurations."""
        workflows_dir = self.config_dir / "workflows"

        # Load sequential workflows
        sequential_dir = workflows_dir / "sequential"
        if sequential_dir.exists():
            for config_file in sequential_dir.glob("*.json"):
                config = JSONLoader.load(config_file)
                self.workflows[config["workflow_id"]] = config
                self.logger.debug(f"Loaded workflow: {config['workflow_id']}")

        # Load iterative workflows
        iterative_dir = workflows_dir / "iterative"
        if iterative_dir.exists():
            for config_file in iterative_dir.glob("*.json"):
                config = JSONLoader.load(config_file)
                self.workflows[config["workflow_id"]] = config
                self.logger.debug(f"Loaded workflow: {config['workflow_id']}")

    def _create_llm_client(self, model_tier: str) -> LlamaCppClient:
        """
        Create LLM client for given model tier.

        Args:
            model_tier: Model tier ID (e.g., "tier1_fast")

        Returns:
            LlamaCppClient instance
        """
        if model_tier not in self.models:
            self.logger.warning(f"Model tier not found: {model_tier}, using tier1_fast")
            model_tier = "tier1_fast"

        model_config = self.models[model_tier]
        model_path = self.models_dir / model_config["path"]

        return LlamaCppClient(
            model_path=model_path,
            llama_cli_path=self.llama_cli_path,
            n_gpu_layers=model_config.get("n_gpu_layers", 999),
            ctx_size=model_config.get("ctx_size", 4096),
            threads=model_config.get("threads", 4)
        )

    def execute_workflow(
        self,
        workflow_id: str,
        inputs: Dict[str, Any],
        max_iterations: Optional[int] = None
    ) -> OrchestrationResult:
        """
        Execute a workflow with given inputs.

        Args:
            workflow_id: Workflow ID to execute
            inputs: Input data for workflow
            max_iterations: Override max iterations (for iterative workflows)

        Returns:
            OrchestrationResult with outputs
        """
        self.logger.info(f"Executing workflow: {workflow_id}")

        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow = self.workflows[workflow_id]

        # Determine workflow mode
        mode = workflow.get("mode", "sequential")

        if mode == "iterative":
            return self._execute_iterative_workflow(workflow, inputs, max_iterations)
        else:
            return self._execute_sequential_workflow(workflow, inputs)

    def _execute_sequential_workflow(
        self,
        workflow: Dict,
        inputs: Dict[str, Any]
    ) -> OrchestrationResult:
        """Execute sequential workflow."""
        self.logger.info(f"Executing sequential workflow: {workflow['workflow_id']}")

        outputs = []
        context = {}

        for step in workflow["steps"]:
            technique_id = step["technique"]

            # Load technique
            technique_path = self.config_dir / "techniques" / f"{technique_id}.json"
            technique = JSONLoader.load(technique_path)

            # Determine which agent to use
            agent = self._select_agent_for_technique(technique)

            # Build task
            task_inputs = {**inputs}

            # Add context from previous steps if specified
            if step.get("context_from_previous", False):
                task_inputs["previous_context"] = context

            task = Task(
                task_id=f"{workflow['workflow_id']}_{technique_id}",
                description=technique["prompt"].format(**task_inputs),
                technique=technique_id,
                inputs=task_inputs,
                temperature=technique.get("temperature", 0.7),
                max_tokens=technique.get("max_tokens", 2048)
            )

            # Execute
            output = agent.execute_task(task)
            outputs.append(output)

            # Update context
            context[technique_id] = output.output

            # Handle failures
            if not output.success and step.get("on_fail") == "stop":
                self.logger.error(f"Task failed, stopping workflow: {output.error}")
                return OrchestrationResult(
                    workflow_id=workflow["workflow_id"],
                    status="failed",
                    iterations=1,
                    confidence=0.0,
                    outputs=outputs,
                    metadata={"error": output.error}
                )

        # Generate final report (if needed)
        final_report = self._generate_final_report(outputs)

        return OrchestrationResult(
            workflow_id=workflow["workflow_id"],
            status="completed",
            iterations=1,
            confidence=1.0,  # TODO: Calculate confidence
            outputs=outputs,
            final_report=final_report
        )

    def _execute_iterative_workflow(
        self,
        workflow: Dict,
        inputs: Dict[str, Any],
        max_iterations: Optional[int] = None
    ) -> OrchestrationResult:
        """Execute iterative workflow with refinement loops."""
        self.logger.info(f"Executing iterative workflow: {workflow['workflow_id']}")

        max_iter = max_iterations or workflow.get("max_iterations", 5)
        exit_threshold = workflow.get("exit_criteria", {}).get("threshold", 0.8)

        iteration = 0
        confidence = 0.0
        all_outputs = []
        current_inputs = inputs.copy()

        while iteration < max_iter:
            self.logger.info(f"Iteration {iteration + 1}/{max_iter}")

            # Execute workflow steps
            iteration_outputs = []

            for step in workflow["steps"]:
                # Skip conditional steps if condition not met
                if "condition" in step:
                    if not self._evaluate_condition(step["condition"], current_inputs):
                        continue

                # Execute step
                output = self._execute_workflow_step(step, current_inputs, workflow)
                iteration_outputs.append(output)

                # Update inputs for next step
                if "output_key" in step:
                    current_inputs[step["output_key"]] = output.output

            all_outputs.extend(iteration_outputs)

            # Evaluate confidence
            confidence = self._evaluate_confidence(iteration_outputs, current_inputs)
            self.logger.info(f"Iteration {iteration + 1} confidence: {confidence:.2f}")

            # Check exit criteria
            if confidence >= exit_threshold:
                self.logger.info(f"Exit threshold reached: {confidence:.2f} >= {exit_threshold}")
                break

            # Identify gaps for next iteration
            if iteration < max_iter - 1:
                gaps = self._identify_gaps(iteration_outputs, current_inputs)
                current_inputs = self._refine_inputs(current_inputs, gaps)

            iteration += 1

        # Generate final report
        final_report = self._generate_final_report(all_outputs)

        return OrchestrationResult(
            workflow_id=workflow["workflow_id"],
            status="completed" if confidence >= exit_threshold else "partial",
            iterations=iteration,
            confidence=confidence,
            outputs=all_outputs,
            final_report=final_report,
            metadata={
                "exit_threshold": exit_threshold,
                "final_confidence": confidence
            }
        )

    def _execute_workflow_step(
        self,
        step: Dict,
        inputs: Dict[str, Any],
        workflow: Dict
    ) -> AgentOutput:
        """Execute a single workflow step."""
        # Get agent
        agent_id = step.get("agent", "fast_researcher")
        agent = self.agents.get(agent_id)

        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")

        # Build task
        task = Task(
            task_id=f"{workflow['workflow_id']}_step_{step['step']}",
            description=step.get("task", "Execute workflow step"),
            inputs=inputs,
            temperature=step.get("temperature", 0.7)
        )

        # Execute
        return agent.execute_task(task)

    def _evaluate_condition(self, condition: str, inputs: Dict) -> bool:
        """
        Evaluate a conditional expression.

        Simple implementation - can be extended for complex logic.
        """
        # Example: "evaluation.confidence < 0.8"
        try:
            # Simple eval - UNSAFE in production, use proper parser
            return eval(condition, {"__builtins__": {}}, inputs)
        except Exception as e:
            self.logger.warning(f"Condition evaluation failed: {e}")
            return False

    def _evaluate_confidence(
        self,
        outputs: List[AgentOutput],
        inputs: Dict[str, Any]
    ) -> float:
        """
        Evaluate confidence score for workflow outputs.

        TODO: Implement proper confidence calculation
        """
        # Simple heuristic: all tasks succeeded
        success_rate = sum(1 for o in outputs if o.success) / len(outputs) if outputs else 0
        return success_rate

    def _identify_gaps(
        self,
        outputs: List[AgentOutput],
        inputs: Dict[str, Any]
    ) -> List[str]:
        """
        Identify gaps in research for next iteration.

        TODO: Implement gap detection logic
        """
        gaps = []

        # Simple heuristic: failed tasks are gaps
        for output in outputs:
            if not output.success:
                gaps.append(f"Failed task: {output.task_id}")

        return gaps

    def _refine_inputs(
        self,
        inputs: Dict[str, Any],
        gaps: List[str]
    ) -> Dict[str, Any]:
        """
        Refine inputs based on identified gaps.

        TODO: Implement input refinement logic
        """
        refined = inputs.copy()
        refined["gaps"] = gaps
        refined["refinement_needed"] = True

        return refined

    def _generate_final_report(self, outputs: List[AgentOutput]) -> str:
        """
        Generate final report from outputs.

        TODO: Implement proper report generation
        """
        report_parts = []

        for output in outputs:
            report_parts.append(f"## {output.task_id}\n")
            report_parts.append(output.output)
            report_parts.append("\n\n")

        return "\n".join(report_parts)

    def _select_agent_for_technique(self, technique: Dict) -> Agent:
        """
        Select appropriate agent for a technique.

        Uses agent_role field from technique config.
        """
        agent_role = technique.get("agent_role", "analyst")

        # Find agent with matching role
        for agent in self.agents.values():
            if agent.role == agent_role:
                return agent

        # Fallback to first agent
        if self.agents:
            return list(self.agents.values())[0]

        raise RuntimeError("No agents available")

    # Public utility methods

    def list_workflows(self) -> List[Dict]:
        """List all available workflows."""
        return [
            {
                "workflow_id": wf["workflow_id"],
                "name": wf.get("name", wf["workflow_id"]),
                "mode": wf.get("mode", "sequential"),
                "description": wf.get("description", "")
            }
            for wf in self.workflows.values()
        ]

    def list_agents(self) -> List[Dict]:
        """List all available agents."""
        return [
            {
                "agent_id": agent.agent_id,
                "role": agent.role,
                "tools": agent.tools
            }
            for agent in self.agents.values()
        ]

    def list_techniques(self) -> List[Dict]:
        """List all available techniques."""
        techniques_dir = self.config_dir / "techniques"
        if not techniques_dir.exists():
            return []

        techniques = []
        for config_file in techniques_dir.glob("*.json"):
            config = JSONLoader.load(config_file)
            techniques.append({
                "technique_id": config["technique_id"],
                "name": config.get("name", config["technique_id"]),
                "description": config.get("description", "")
            })

        return techniques

    def list_models(self) -> List[Dict]:
        """List all available models."""
        return [
            {
                "model_id": model["model_id"],
                "name": model.get("name", model["model_id"]),
                "agent_role": model.get("agent_role", "")
            }
            for model in self.models.values()
        ]

    def health_check(self) -> Dict[str, Any]:
        """
        Check orchestrator health.

        Returns:
            Health status dict
        """
        status = {
            "orchestrator": "ready",
            "agents_loaded": len(self.agents),
            "workflows_loaded": len(self.workflows),
            "models_loaded": len(self.models),
            "llama_cli_exists": self.llama_cli_path.exists()
        }

        # Test first agent's LLM client
        if self.agents:
            first_agent = list(self.agents.values())[0]
            try:
                llm_status = first_agent.llm_client.health_check()
                status["llm_backend"] = llm_status
            except Exception as e:
                status["llm_backend_error"] = str(e)

        return status
