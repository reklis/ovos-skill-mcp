"""Skill management tools for OVOS MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ovos_bus_client import Message

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from ovos_skill_mcp.bus import OVOSBusClient


def register_skills_tools(mcp: FastMCP, bus: OVOSBusClient) -> None:
    """Register skill management tools with the MCP server.

    Args:
        mcp: The FastMCP server instance.
        bus: The OVOS bus client instance.
    """

    @mcp.tool()
    async def list_skills() -> dict:
        """Get a list of all loaded skills in OVOS.

        Returns:
            Dictionary containing a list of skills with their IDs and status.
        """
        response = await bus.wait_for_response_async(
            Message("skillmanager.list"),
            reply_type="mycroft.skills.list",
            timeout=10.0,
        )
        if response:
            return {"skills": response.data}
        return {"skills": [], "error": "No response from skill manager"}

    @mcp.tool()
    async def activate_skill(skill_id: str) -> str:
        """Activate (load) a skill by its ID.

        Args:
            skill_id: The unique identifier of the skill to activate.

        Returns:
            Confirmation that the skill activation was requested.
        """
        response = await bus.wait_for_response_async(
            Message("skillmanager.activate", {"skill_id": skill_id}),
            reply_type="skillmanager.activate.response",
            timeout=10.0,
        )
        if response:
            if response.data.get("success", False):
                return f"Skill '{skill_id}' activated successfully"
            return f"Failed to activate skill '{skill_id}': {response.data.get('error', 'Unknown error')}"
        return f"No response when activating skill '{skill_id}'"

    @mcp.tool()
    async def deactivate_skill(skill_id: str) -> str:
        """Deactivate (unload) a skill by its ID.

        Args:
            skill_id: The unique identifier of the skill to deactivate.

        Returns:
            Confirmation that the skill deactivation was requested.
        """
        response = await bus.wait_for_response_async(
            Message("skillmanager.deactivate", {"skill_id": skill_id}),
            reply_type="skillmanager.deactivate.response",
            timeout=10.0,
        )
        if response:
            if response.data.get("success", False):
                return f"Skill '{skill_id}' deactivated successfully"
            return f"Failed to deactivate skill '{skill_id}': {response.data.get('error', 'Unknown error')}"
        return f"No response when deactivating skill '{skill_id}'"

    @mcp.tool()
    async def get_active_skills() -> dict:
        """Get a list of currently active (conversing) skills.

        These are skills that are in the active conversation stack.

        Returns:
            Dictionary containing a list of active skill IDs.
        """
        response = await bus.wait_for_response_async(
            Message("intent.service.active_skills.get"),
            reply_type="intent.service.active_skills.reply",
            timeout=5.0,
        )
        if response:
            return {"active_skills": response.data.get("skills", [])}
        return {"active_skills": [], "error": "No response from intent service"}

    @mcp.tool()
    async def deactivate_active_skill(skill_id: str) -> str:
        """Remove a skill from the active conversation stack.

        This prevents the skill from receiving follow-up conversation messages.

        Args:
            skill_id: The unique identifier of the skill to deactivate from conversation.

        Returns:
            Confirmation that the skill was removed from active stack.
        """
        await bus.emit_async(
            Message(
                "intent.service.skills.deactivate",
                {"skill_id": skill_id},
            )
        )
        return f"Skill '{skill_id}' removed from active conversation stack"

    @mcp.tool()
    async def install_skill(url: str) -> str:
        """Install a skill from a GitHub URL.

        Args:
            url: The GitHub URL of the skill repository to install.

        Returns:
            Confirmation that the skill installation was initiated.
        """
        response = await bus.wait_for_response_async(
            Message("ovos.skills.install", {"url": url}),
            reply_type="ovos.skills.install.complete",
            timeout=120.0,  # Installation can take a while
        )
        if response:
            return f"Skill installed successfully from {url}"
        return f"Skill installation initiated for {url} (may still be in progress)"

    @mcp.tool()
    async def uninstall_skill(skill_id: str) -> str:
        """Uninstall a skill by its ID.

        Args:
            skill_id: The unique identifier of the skill to uninstall.

        Returns:
            Confirmation of the uninstallation.
        """
        response = await bus.wait_for_response_async(
            Message("ovos.skills.uninstall", {"skill_id": skill_id}),
            reply_type="ovos.skills.uninstall.complete",
            timeout=60.0,
        )
        if response:
            return f"Skill '{skill_id}' uninstalled successfully"
        return f"Skill uninstallation initiated for '{skill_id}'"

    @mcp.tool()
    async def get_skill_settings(skill_id: str) -> dict:
        """Get the settings for a specific skill.

        Args:
            skill_id: The unique identifier of the skill.

        Returns:
            Dictionary containing the skill's settings.
        """
        response = await bus.wait_for_response_async(
            Message(f"{skill_id}.public_api"),
            reply_type=f"{skill_id}.public_api.response",
            timeout=5.0,
        )
        if response:
            return {"skill_id": skill_id, "api": response.data}
        return {"skill_id": skill_id, "error": "No response from skill"}
