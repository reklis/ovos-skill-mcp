"""OVOS Skill MCP - FastMCP server exposing OVOS skills via HTTP streaming."""

from ovos_skill_mcp.server import mcp, create_server

__version__ = "0.1.0"
__all__ = ["mcp", "create_server", "__version__"]
