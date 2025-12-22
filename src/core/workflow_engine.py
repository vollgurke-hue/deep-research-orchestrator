"""
Workflow Engine for executing research workflows.

Supports sequential and iterative execution modes.
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass

from src.utils.logger import setup_logger


@dataclass
class WorkflowStep:
    """Single step in a workflow."""

    step: int
    technique: Optional[str] = None
    agent: Optional[str] = None
    task: Optional[str] = None
    condition: Optional[str] = None
    input_from: Optional[str] = None
    output_key: Optional[str] = None
    on_fail: str = "continue"
    context_from_previous: bool = False


class WorkflowEngine:
    """
    Engine for executing workflows.

    Handles both sequential and iterative modes.
    """

    def __init__(self, orchestrator):
        """
        Initialize workflow engine.

        Args:
            orchestrator: Reference to parent Orchestrator
        """
        self.orchestrator = orchestrator
        self.logger = setup_logger("workflow_engine")

    def execute(
        self,
        workflow: Dict[str, Any],
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a workflow.

        Args:
            workflow: Workflow configuration
            inputs: Input data

        Returns:
            Execution results
        """
        mode = workflow.get("mode", "sequential")

        if mode == "iterative":
            return self._execute_iterative(workflow, inputs)
        elif mode == "sequential":
            return self._execute_sequential(workflow, inputs)
        else:
            raise ValueError(f"Unknown workflow mode: {mode}")

    def _execute_sequential(
        self,
        workflow: Dict[str, Any],
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute workflow in sequential mode.

        All steps run once in order.
        """
        self.logger.info(f"Executing sequential workflow: {workflow['workflow_id']}")

        results = {
            "workflow_id": workflow["workflow_id"],
            "mode": "sequential",
            "steps_executed": [],
            "context": {}
        }

        for step_data in workflow["steps"]:
            step = self._parse_step(step_data)

            self.logger.debug(f"Executing step {step.step}: {step.technique or step.task}")

            # Execute step
            step_result = self._execute_step(step, inputs, results["context"])

            results["steps_executed"].append({
                "step": step.step,
                "technique": step.technique,
                "success": step_result.get("success", True),
                "output": step_result.get("output")
            })

            # Update context
            if step.output_key:
                results["context"][step.output_key] = step_result.get("output")

            # Handle failure
            if not step_result.get("success", True) and step.on_fail == "stop":
                self.logger.error(f"Step {step.step} failed, stopping workflow")
                results["status"] = "failed"
                results["error"] = step_result.get("error")
                return results

        results["status"] = "completed"
        return results

    def _execute_iterative(
        self,
        workflow: Dict[str, Any],
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute workflow in iterative mode.

        Steps can loop based on conditions until exit criteria met.
        """
        self.logger.info(f"Executing iterative workflow: {workflow['workflow_id']}")

        max_iterations = workflow.get("max_iterations", 5)
        exit_criteria = workflow.get("exit_criteria", {})

        results = {
            "workflow_id": workflow["workflow_id"],
            "mode": "iterative",
            "iterations": [],
            "context": {},
            "current_inputs": inputs.copy()
        }

        for iteration in range(max_iterations):
            self.logger.info(f"Iteration {iteration + 1}/{max_iterations}")

            iteration_result = {
                "iteration": iteration + 1,
                "steps_executed": [],
                "context": {}
            }

            # Execute all steps for this iteration
            for step_data in workflow["steps"]:
                step = self._parse_step(step_data)

                # Check condition if present
                if step.condition and not self._evaluate_condition(
                    step.condition,
                    results["context"]
                ):
                    self.logger.debug(f"Step {step.step} condition not met, skipping")
                    continue

                # Execute step
                step_result = self._execute_step(
                    step,
                    results["current_inputs"],
                    results["context"]
                )

                iteration_result["steps_executed"].append({
                    "step": step.step,
                    "technique": step.technique,
                    "success": step_result.get("success", True)
                })

                # Update context
                if step.output_key:
                    results["context"][step.output_key] = step_result.get("output")
                    iteration_result["context"][step.output_key] = step_result.get("output")

                # Handle loop_to (return to earlier step)
                if "loop_to" in step_data and step_result.get("should_loop", False):
                    self.logger.info(f"Looping back to step {step_data['loop_to']}")
                    # This would require more complex flow control
                    # For now, continue to next iteration
                    break

            results["iterations"].append(iteration_result)

            # Check exit criteria
            if self._check_exit_criteria(exit_criteria, results["context"]):
                self.logger.info(f"Exit criteria met at iteration {iteration + 1}")
                results["status"] = "completed"
                results["exit_reason"] = "criteria_met"
                return results

        results["status"] = "completed"
        results["exit_reason"] = "max_iterations"
        return results

    def _execute_step(
        self,
        step: WorkflowStep,
        inputs: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single workflow step.

        Args:
            step: Step to execute
            inputs: Input data
            context: Current workflow context

        Returns:
            Step execution result
        """
        # Build step inputs
        step_inputs = inputs.copy()

        # Add context if needed
        if step.context_from_previous:
            step_inputs["context"] = context

        # Add specific input if specified
        if step.input_from and step.input_from in context:
            step_inputs["input"] = context[step.input_from]

        # Delegate to orchestrator for actual execution
        # (This is a placeholder - actual implementation would call agents)

        result = {
            "success": True,
            "output": f"Executed {step.technique or step.task}",
            "metadata": {
                "step": step.step,
                "technique": step.technique
            }
        }

        return result

    def _parse_step(self, step_data: Dict) -> WorkflowStep:
        """Parse step data into WorkflowStep object."""
        return WorkflowStep(
            step=step_data["step"],
            technique=step_data.get("technique"),
            agent=step_data.get("agent"),
            task=step_data.get("task"),
            condition=step_data.get("condition"),
            input_from=step_data.get("input_from"),
            output_key=step_data.get("output_key"),
            on_fail=step_data.get("on_fail", "continue"),
            context_from_previous=step_data.get("context_from_previous", False)
        )

    def _evaluate_condition(
        self,
        condition: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Evaluate a condition string.

        Simple implementation using eval (UNSAFE - replace with proper parser).
        """
        try:
            # Create safe namespace
            namespace = {
                "__builtins__": {},
                **context
            }
            return bool(eval(condition, namespace))
        except Exception as e:
            self.logger.warning(f"Condition evaluation failed: {e}")
            return False

    def _check_exit_criteria(
        self,
        criteria: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """
        Check if exit criteria are met.

        Args:
            criteria: Exit criteria configuration
            context: Current workflow context

        Returns:
            True if criteria met, False otherwise
        """
        if not criteria:
            return False

        criteria_type = criteria.get("type")

        if criteria_type == "confidence_threshold":
            threshold = criteria.get("threshold", 0.8)
            confidence = context.get("confidence", 0.0)
            return confidence >= threshold

        elif criteria_type == "all_complete":
            # Check if all required outputs are present
            required = criteria.get("required_outputs", [])
            return all(key in context for key in required)

        elif criteria_type == "custom":
            # Evaluate custom condition
            condition = criteria.get("condition")
            if condition:
                return self._evaluate_condition(condition, context)

        return False

    def validate_workflow(self, workflow: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate workflow configuration.

        Args:
            workflow: Workflow to validate

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        # Check required fields
        if "workflow_id" not in workflow:
            errors.append("Missing workflow_id")

        if "steps" not in workflow or not workflow["steps"]:
            errors.append("Missing or empty steps")

        # Check mode-specific requirements
        mode = workflow.get("mode", "sequential")

        if mode == "iterative":
            if "max_iterations" not in workflow:
                errors.append("Iterative workflow missing max_iterations")

            if "exit_criteria" not in workflow:
                errors.append("Iterative workflow missing exit_criteria")

        # Validate steps
        for i, step in enumerate(workflow.get("steps", [])):
            if "step" not in step:
                errors.append(f"Step {i} missing step number")

            if "technique" not in step and "task" not in step:
                errors.append(f"Step {i} missing technique or task")

        return (len(errors) == 0, errors)
