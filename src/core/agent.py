"""
Agent system for deep research orchestrator.

Inspired by CrewAI but custom implementation without external dependencies.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
import json


@dataclass
class AgentOutput:
    """Output from an agent task execution."""

    agent_id: str
    task_id: str
    output: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None


@dataclass
class Task:
    """Task to be executed by an agent."""

    task_id: str
    description: str
    technique: Optional[str] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    expected_output: Optional[Dict[str, Any]] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    requires_tools: bool = False


class Agent:
    """
    Autonomous agent with specific role and capabilities.

    Inspired by CrewAI's agent pattern but custom implementation.
    """

    def __init__(
        self,
        agent_id: str,
        role: str,
        llm_client,  # LlamaCppClient instance
        tools: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Initialize agent.

        Args:
            agent_id: Unique agent identifier
            role: Agent role (e.g., "researcher", "validator")
            llm_client: LlamaCppClient instance
            tools: List of available tool names
            system_prompt: System prompt for this agent
            temperature: Default temperature for generation
        """
        self.agent_id = agent_id
        self.role = role
        self.llm_client = llm_client
        self.tools = tools or []
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.temperature = temperature

    def execute_task(self, task: Task) -> AgentOutput:
        """
        Execute a task using available tools.

        Args:
            task: Task to execute

        Returns:
            AgentOutput with results
        """
        try:
            # Build prompt from task
            prompt = self._build_prompt(task)

            # Generate response using LLM
            response = self.llm_client.generate(
                prompt=prompt,
                temperature=task.temperature or self.temperature,
                max_tokens=task.max_tokens,
                system_prompt=self.system_prompt
            )

            # TODO: Apply tools if task.requires_tools
            # For now, return raw response

            return AgentOutput(
                agent_id=self.agent_id,
                task_id=task.task_id,
                output=response,
                metadata={
                    "role": self.role,
                    "tools_used": []  # Placeholder
                },
                success=True
            )

        except Exception as e:
            return AgentOutput(
                agent_id=self.agent_id,
                task_id=task.task_id,
                output="",
                metadata={"role": self.role},
                success=False,
                error=str(e)
            )

    def _build_prompt(self, task: Task) -> str:
        """Build prompt from task description and inputs."""
        prompt_parts = [task.description]

        # Add input context if provided
        if task.inputs:
            prompt_parts.append("\n\nContext:")
            for key, value in task.inputs.items():
                prompt_parts.append(f"\n{key}: {value}")

        # Add expected output format if specified
        if task.expected_output:
            prompt_parts.append("\n\nExpected output format:")
            prompt_parts.append(json.dumps(task.expected_output, indent=2))

        return "\n".join(prompt_parts)

    def _default_system_prompt(self) -> str:
        """Default system prompt based on role."""
        prompts = {
            "researcher": (
                "You are a research analyst system. "
                "Provide factual, data-driven analysis. "
                "Use impersonal language. "
                "Cite sources when possible. "
                "Output structured data (JSON or tables preferred)."
            ),
            "validator": (
                "You are a validation system. "
                "Critically analyze information for contradictions and gaps. "
                "Be thorough and objective. "
                "Output findings in structured format."
            ),
            "synthesizer": (
                "You are a synthesis system. "
                "Combine multiple sources into coherent analysis. "
                "Highlight agreements and disagreements. "
                "Maintain objectivity."
            )
        }

        return prompts.get(self.role, "You are an analytical system. Provide objective, structured analysis.")

    @classmethod
    def from_json(cls, config_path: Path, llm_client):
        """
        Load agent from JSON configuration.

        Args:
            config_path: Path to agent JSON config
            llm_client: LlamaCppClient instance

        Returns:
            Agent instance
        """
        with open(config_path) as f:
            config = json.load(f)

        return cls(
            agent_id=config["agent_id"],
            role=config["role"],
            llm_client=llm_client,
            tools=config.get("tools", []),
            system_prompt=config.get("system_prompt"),
            temperature=config.get("temperature", 0.7)
        )
