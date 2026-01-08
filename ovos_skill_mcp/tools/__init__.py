"""OVOS MCP Tools - Tool handlers for OVOS message bus interactions."""

from ovos_skill_mcp.tools.speech import register_speech_tools
from ovos_skill_mcp.tools.audio import register_audio_tools
from ovos_skill_mcp.tools.volume import register_volume_tools
from ovos_skill_mcp.tools.skills import register_skills_tools
from ovos_skill_mcp.tools.system import register_system_tools
from ovos_skill_mcp.tools.ocp import register_ocp_tools

__all__ = [
    "register_speech_tools",
    "register_audio_tools",
    "register_volume_tools",
    "register_skills_tools",
    "register_system_tools",
    "register_ocp_tools",
]


def register_all_tools(mcp, bus):
    """Register all OVOS tools with the MCP server."""
    register_speech_tools(mcp, bus)
    register_audio_tools(mcp, bus)
    register_volume_tools(mcp, bus)
    register_skills_tools(mcp, bus)
    register_system_tools(mcp, bus)
    register_ocp_tools(mcp, bus)
