#!/usr/bin/env python3
"""Sequential Thinking tools, registered on the main llama-tools FastMCP server."""

import textwrap

from fastmcp import FastMCP

sequential_mcp = FastMCP("Sequential Thinking")

thought_history: list[dict] = []
thought_branches: dict[str, list[dict]] = {}


def _find_index(thoughts: list[dict], thought_number: int) -> int | None:
    return next(
        (i for i, t in enumerate(thoughts) if t["thoughtNumber"] == thought_number),
        None,
    )


def _record(
    thoughts: list[dict],
    thought_data: dict,
    is_revision: bool | None,
    revises: int | None,
) -> None:
    if is_revision and revises:
        idx = _find_index(thoughts, revises)
        if idx is not None:
            thoughts[idx] = thought_data
    else:
        thoughts.append(thought_data)


def _format_thought(t: dict) -> str:
    return f"## Thought {t['thoughtNumber']}/{t['totalThoughts']}\n\n{t['thought']}\n\n"


@sequential_mcp.tool()
def sequential_thinking(
    thought: str,
    thoughtNumber: int,
    totalThoughts: int,
    nextThoughtNeeded: bool,
    isRevision: bool | None = None,
    revisesThought: int | None = None,
    branchFromThought: int | None = None,
    branchId: str | None = None,
    needsMoreThoughts: bool | None = None,
) -> str:
    """
    Facilitates a detailed, step-by-step thinking process for problem-solving and analysis.

    Args:
        thought: The current thinking step
        thoughtNumber: Current thought number
        totalThoughts: Estimated total thoughts needed
        nextThoughtNeeded: Whether another thought step is needed
        isRevision: Whether this revises previous thinking
        revisesThought: Which thought is being reconsidered
        branchFromThought: Branching point thought number
        branchId: Branch identifier
        needsMoreThoughts: If more thoughts are needed

    Returns:
        Response message about the recorded thought
    """
    thought_data = {
        "thought": thought,
        "thoughtNumber": thoughtNumber,
        "totalThoughts": totalThoughts,
        "nextThoughtNeeded": nextThoughtNeeded,
        "isRevision": isRevision,
        "revisesThought": revisesThought,
        "branchFromThought": branchFromThought,
        "branchId": branchId,
        "needsMoreThoughts": needsMoreThoughts,
    }

    if branchId:
        if branchId not in thought_branches and branchFromThought:
            idx = _find_index(thought_history, branchFromThought)
            thought_branches[branchId] = (
                thought_history[: idx + 1].copy() if idx is not None else []
            )
        if branchId in thought_branches:
            _record(
                thought_branches[branchId], thought_data, isRevision, revisesThought
            )
    else:
        _record(thought_history, thought_data, isRevision, revisesThought)

    if isRevision:
        return f"Revised thought {revisesThought}."

    branch_text = f" (Branch: {branchId})" if branchId else ""

    if not nextThoughtNeeded:
        return (
            f"Recorded final thought {thoughtNumber}/{totalThoughts}{branch_text}. "
            "The thinking process is complete."
        )

    suffix = (
        "More thoughts will be needed."
        if needsMoreThoughts
        else "Continue with the next thought."
    )
    return f"Recorded thought {thoughtNumber}/{totalThoughts}{branch_text}. {suffix}"


@sequential_mcp.resource("thoughts://history")
def get_thought_history() -> str:
    """Get the complete thought history as a formatted string."""
    if not thought_history:
        return "No thoughts recorded yet."
    return "# Thought History\n\n" + "".join(
        _format_thought(t) for t in thought_history
    )


@sequential_mcp.resource("thoughts://branches/{branch_id}")
def get_branch_thoughts(branch_id: str) -> str:
    """Get the thoughts for a specific branch."""
    if branch_id not in thought_branches:
        return f"Branch '{branch_id}' not found."
    branch = thought_branches[branch_id]
    if not branch:
        return f"No thoughts recorded for branch '{branch_id}'."
    return f"# Branch: {branch_id}\n\n" + "".join(_format_thought(t) for t in branch)


@sequential_mcp.resource("thoughts://summary")
def get_thought_summary() -> str:
    """Get a summary of all thoughts and branches."""
    result = "# Sequential Thinking Summary\n\n## Main Thought Line\n\n"
    result += f"- Total thoughts: {len(thought_history)}\n"
    if thought_history:
        last = thought_history[-1]
        result += f"- Current progress: Thought {last['thoughtNumber']}/{last['totalThoughts']}\n"

    if thought_branches:
        result += "\n## Branches\n\n"
        for branch_id, branch in thought_branches.items():
            result += f"- Branch '{branch_id}': {len(branch)} thoughts\n"

    return result


@sequential_mcp.prompt()
def thinking_process_guide() -> str:
    """Guide for using the sequential thinking process."""
    return textwrap.dedent("""
        # Sequential Thinking Process Guide

        This tool helps break down complex problems into manageable steps through a structured thinking process.

        ## How to Use

        1. Start with an initial thought (thoughtNumber = 1)
        2. Continue adding thoughts sequentially
        3. You can revise previous thoughts if needed
        4. You can create branches to explore alternative paths

        ## Example

        ```python
        # First thought
        sequential_thinking(
            thought="First, we need to understand the problem requirements.",
            thoughtNumber=1,
            totalThoughts=5,
            nextThoughtNeeded=True
        )

        # Revise a thought
        sequential_thinking(
            thought="Actually, we need to clarify the problem requirements first.",
            thoughtNumber=1,
            totalThoughts=5,
            nextThoughtNeeded=True,
            isRevision=True,
            revisesThought=1
        )

        # Branch from thought 2
        sequential_thinking(
            thought="Let's explore an alternative approach.",
            thoughtNumber=3,
            totalThoughts=5,
            nextThoughtNeeded=True,
            branchFromThought=2,
            branchId="alternative-approach"
        )
        ```
    """).strip()
