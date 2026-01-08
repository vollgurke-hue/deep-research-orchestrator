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
        self.techniques: Dict[str, Dict] = {}

        # Initialize engines
        self.workflow_engine = WorkflowEngine(self)
        self.state_manager = StateManager()

        # Load configs
        self._load_model_configs()
        self._load_agent_configs()
        self._load_workflow_configs()
        self._load_technique_configs()

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

    def _load_technique_configs(self):
        """Load technique configurations."""
        techniques_dir = self.config_dir / "techniques"
        if not techniques_dir.exists():
            self.logger.warning(f"Techniques config dir not found: {techniques_dir}")
            return

        for config_file in techniques_dir.glob("*.json"):
            config = JSONLoader.load(config_file)
            self.techniques[config["technique_id"]] = config
            self.logger.debug(f"Loaded technique: {config['technique_id']}")

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

        Calculates confidence based on multiple factors:
        - Task success rate
        - Output quality (length, structure)
        - Consistency across outputs
        - Gap severity
        - LLM-based confidence assessment
        """
        if not outputs:
            return 0.0

        confidence_factors = []

        # Factor 1: Success Rate (0.0-1.0)
        success_rate = sum(1 for o in outputs if o.success) / len(outputs)
        confidence_factors.append(("success_rate", success_rate, 0.3))  # 30% weight

        # Factor 2: Output Quality (0.0-1.0)
        quality_scores = []
        for output in outputs:
            if output.success:
                # Heuristics for quality
                length_score = min(len(output.output) / 500, 1.0)  # Longer = better (up to 500 chars)

                # Check for structured output (bullets, numbers, sections)
                has_structure = any(marker in output.output for marker in ['-', '1.', '2.', '##', '*'])
                structure_score = 1.0 if has_structure else 0.5

                quality_scores.append((length_score + structure_score) / 2)
            else:
                quality_scores.append(0.0)

        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        confidence_factors.append(("output_quality", avg_quality, 0.2))  # 20% weight

        # Factor 3: Consistency Check (0.0-1.0)
        # If multiple outputs, check if they're consistent in length/quality
        if len(outputs) > 1:
            lengths = [len(o.output) for o in outputs if o.success]
            if lengths:
                avg_len = sum(lengths) / len(lengths)
                variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
                # Low variance = high consistency
                consistency_score = max(0.0, 1.0 - (variance / (avg_len ** 2)))
            else:
                consistency_score = 0.0
        else:
            consistency_score = 1.0  # Single output, no consistency check needed

        confidence_factors.append(("consistency", consistency_score, 0.1))  # 10% weight

        # Factor 4: Gap Severity (0.0-1.0)
        # Fewer gaps = higher confidence
        try:
            gaps = self._identify_gaps(outputs, inputs)
            gap_penalty = min(len(gaps) * 0.1, 0.4)  # Each gap reduces confidence, max 40% penalty
            gap_score = max(0.0, 1.0 - gap_penalty)
        except Exception:
            gap_score = 0.7  # Moderate score if gap detection fails

        confidence_factors.append(("gap_score", gap_score, 0.2))  # 20% weight

        # Factor 5: LLM-based Confidence (0.0-1.0) - Optional, expensive
        llm_confidence = None
        if inputs.get("use_llm_confidence", False):
            try:
                llm_confidence = self._llm_based_confidence(outputs, inputs)
            except Exception as e:
                self.logger.warning(f"LLM confidence assessment failed: {e}")

        if llm_confidence is not None:
            confidence_factors.append(("llm_assessment", llm_confidence, 0.2))  # 20% weight
            # Rebalance other weights
            total_weight_without_llm = sum(w for _, _, w in confidence_factors[:-1])
            confidence_factors = [
                (name, score, weight * 0.8 / total_weight_without_llm)
                for name, score, weight in confidence_factors[:-1]
            ] + [("llm_assessment", llm_confidence, 0.2)]

        # Calculate weighted average
        total_confidence = sum(score * weight for _, score, weight in confidence_factors)

        self.logger.debug(f"Confidence factors: {confidence_factors}")
        self.logger.info(f"Total confidence: {total_confidence:.2f}")

        return round(total_confidence, 2)

    def _llm_based_confidence(
        self,
        outputs: List[AgentOutput],
        inputs: Dict[str, Any]
    ) -> float:
        """
        Use LLM to assess confidence in research outputs.

        Optional, expensive method for high-stakes research.
        """
        quality_agent = None
        for agent in self.agents.values():
            if agent.role == "validator":
                quality_agent = agent
                break

        if not quality_agent:
            return 0.7  # Default moderate confidence

        # Build confidence assessment task
        outputs_summary = "\n\n".join([
            f"Task: {o.task_id}\nOutput: {o.output[:300]}..."
            for o in outputs if o.success
        ])

        task = Task(
            task_id="confidence_assessment",
            description=f"""# Confidence Assessment

Original Query: {inputs.get('topic', inputs.get('query', 'N/A'))}

## Research Outputs:
{outputs_summary}

## Task
Rate your confidence in these research outputs on a scale of 0.0 to 1.0.

Consider:
- Completeness of information
- Quality of sources/reasoning
- Consistency across outputs
- Remaining uncertainties

Output ONLY a single number between 0.0 and 1.0, e.g.: 0.85
""",
            temperature=0.3,
            max_tokens=50
        )

        result = quality_agent.execute_task(task)

        if result.success:
            # Parse confidence score
            try:
                # Extract first number between 0 and 1
                import re
                match = re.search(r'0?\.\d+|1\.0|0|1', result.output)
                if match:
                    score = float(match.group())
                    return min(1.0, max(0.0, score))
            except Exception:
                pass

        return 0.7  # Fallback

    def _identify_gaps(
        self,
        outputs: List[AgentOutput],
        inputs: Dict[str, Any]
    ) -> List[str]:
        """
        Identify gaps in research for next iteration.

        Uses quality validator agent to analyze outputs and find:
        - Missing information
        - Unanswered questions
        - Blind spots
        - Areas needing deeper investigation
        """
        gaps = []

        # 1. Failed tasks are automatic gaps
        for output in outputs:
            if not output.success:
                gaps.append(f"Failed task: {output.task_id} - {output.error}")

        # 2. Use quality agent for LLM-based gap detection
        try:
            # Get quality validator agent
            quality_agent = None
            for agent in self.agents.values():
                if agent.role == "validator":
                    quality_agent = agent
                    break

            if quality_agent:
                # Build comprehensive context from all outputs
                context = {
                    "original_query": inputs.get("topic", inputs.get("query", "Unknown")),
                    "outputs": [
                        {
                            "task_id": o.task_id,
                            "output": o.output[:500],  # Limit for context
                            "success": o.success
                        }
                        for o in outputs
                    ]
                }

                # Create gap detection task
                gap_task = Task(
                    task_id="gap_detection",
                    description=self._build_gap_detection_prompt(context),
                    technique="blind_spots",
                    inputs=context,
                    temperature=0.8,  # Higher for creative gap finding
                    max_tokens=1024
                )

                # Execute
                gap_output = quality_agent.execute_task(gap_task)

                if gap_output.success:
                    # Parse output for gaps (simple parsing - can be improved)
                    gap_text = gap_output.output

                    # Extract gaps from structured output
                    # Expected format: "- Gap: [description]" or "Gap: [description]"
                    for line in gap_text.split('\n'):
                        line = line.strip()
                        if line.startswith('- Gap:') or line.startswith('Gap:'):
                            gap = line.replace('- Gap:', '').replace('Gap:', '').strip()
                            if gap and gap not in gaps:
                                gaps.append(gap)
                        elif line.startswith('-') and len(line) > 10:
                            # Generic bullet point that might be a gap
                            gap = line.lstrip('- ').strip()
                            if gap and not any(skip in gap.lower() for skip in ['none', 'no gaps']):
                                gaps.append(gap)

        except Exception as e:
            self.logger.error(f"Error in LLM-based gap detection: {e}")
            gaps.append(f"Error detecting gaps: {str(e)}")

        # 3. Heuristic: Check for low-confidence outputs
        for output in outputs:
            if output.success and len(output.output) < 100:
                gaps.append(f"Insufficient detail in {output.task_id}")

        return gaps

    def _build_gap_detection_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for LLM-based gap detection."""
        outputs_summary = "\n".join([
            f"- Task: {o['task_id']}\n  Output: {o['output'][:200]}..."
            for o in context.get("outputs", [])
        ])

        return f"""# Gap Detection Analysis

Original Query: {context.get('original_query', 'N/A')}

## Current Research Outputs:

{outputs_summary}

## Task

Analyze these research outputs and identify GAPS - what's missing or needs deeper investigation?

Consider:
1. **Missing Information**: What key facts or data are absent?
2. **Unanswered Questions**: What important questions remain?
3. **Insufficient Depth**: What topics need more detailed analysis?
4. **Blind Spots**: What perspectives or angles were overlooked?
5. **Contradictions**: Any unresolved conflicting information?

For each gap, provide:
- Gap: [Clear description]
- Why it matters: [Brief explanation]
- Priority: high/medium/low

Output format:
```
Gap: [Description of what's missing]
Why it matters: [Impact]
Priority: [high/medium/low]

Gap: [Next gap]
...
```

If no significant gaps, respond: "No major gaps identified."
"""

    def _refine_inputs(
        self,
        inputs: Dict[str, Any],
        gaps: List[str]
    ) -> Dict[str, Any]:
        """
        Refine inputs based on identified gaps.

        Generates focused sub-queries and context refinements to address
        each identified gap in the next iteration.
        """
        refined = inputs.copy()

        if not gaps:
            # No gaps, return original inputs
            return refined

        # Add gaps to context
        refined["identified_gaps"] = gaps
        refined["iteration_focus"] = "gap_filling"

        # Use quality agent to generate refined queries
        try:
            quality_agent = None
            for agent in self.agents.values():
                if agent.role == "validator":
                    quality_agent = agent
                    break

            if quality_agent:
                # Build refinement task
                refinement_task = Task(
                    task_id="input_refinement",
                    description=self._build_refinement_prompt(inputs, gaps),
                    inputs={"original_inputs": inputs, "gaps": gaps},
                    temperature=0.7,
                    max_tokens=1024
                )

                refinement_output = quality_agent.execute_task(refinement_task)

                if refinement_output.success:
                    # Parse refined queries
                    refined_text = refinement_output.output

                    # Extract refined queries
                    refined_queries = []
                    for line in refined_text.split('\n'):
                        line = line.strip()
                        if line.startswith('Query:') or line.startswith('- Query:'):
                            query = line.replace('- Query:', '').replace('Query:', '').strip()
                            if query:
                                refined_queries.append(query)

                    if refined_queries:
                        refined["refined_queries"] = refined_queries
                        refined["focus_areas"] = refined_queries[:3]  # Top 3 priorities

        except Exception as e:
            self.logger.error(f"Error in input refinement: {e}")

        # Heuristic refinements based on gap patterns
        high_priority_gaps = [g for g in gaps if 'high' in g.lower() or 'critical' in g.lower()]
        if high_priority_gaps:
            refined["priority_gaps"] = high_priority_gaps

        # Increase detail level for next iteration
        if "detail_level" in inputs:
            refined["detail_level"] = inputs["detail_level"] + 1
        else:
            refined["detail_level"] = 2

        return refined

    def _build_refinement_prompt(self, inputs: Dict[str, Any], gaps: List[str]) -> str:
        """Build prompt for input refinement."""
        gaps_list = "\n".join([f"- {gap}" for gap in gaps])

        return f"""# Input Refinement for Next Iteration

## Original Query/Topic
{inputs.get('topic', inputs.get('query', 'N/A'))}

## Identified Gaps
{gaps_list}

## Task

Based on these gaps, generate focused research queries for the next iteration.

For each gap, create:
1. A specific, actionable query
2. Suggested research direction
3. Priority level

Output format:
```
Query: [Specific question to address Gap 1]
Direction: [How to research this]
Priority: high/medium/low

Query: [Next query for Gap 2]
...
```

Generate 3-5 refined queries that will effectively fill the identified gaps.
Prioritize the most critical gaps first.
"""

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

    def get_agent(self, agent_id: str) -> Agent:
        """
        Get agent by ID.

        Args:
            agent_id: Agent ID to retrieve

        Returns:
            Agent instance

        Raises:
            ValueError: If agent not found
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent not found: {agent_id}. Available: {list(self.agents.keys())}")
        return self.agents[agent_id]

    def get_workflow(self, workflow_id: str) -> Dict:
        """
        Get workflow config by ID.

        Args:
            workflow_id: Workflow ID to retrieve

        Returns:
            Workflow config dict

        Raises:
            ValueError: If workflow not found
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}. Available: {list(self.workflows.keys())}")
        return self.workflows[workflow_id]

    def get_model(self, model_id: str) -> Dict:
        """
        Get model config by ID.

        Args:
            model_id: Model ID to retrieve

        Returns:
            Model config dict

        Raises:
            ValueError: If model not found
        """
        if model_id not in self.models:
            raise ValueError(f"Model not found: {model_id}. Available: {list(self.models.keys())}")
        return self.models[model_id]

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
