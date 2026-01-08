"""FastMCP server for OVOS skills."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastmcp import FastMCP

from ovos_skill_mcp.bus import OVOSBusClient, connect_bus
from ovos_skill_mcp.tools import register_all_tools

logger = logging.getLogger(__name__)

# Global bus client
_bus: OVOSBusClient | None = None


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[None]:
    """Manage the OVOS bus connection lifecycle.

    Args:
        server: The FastMCP server instance.

    Yields:
        None during the server lifecycle.
    """
    global _bus

    # Get connection settings from environment
    host = os.environ.get("OVOS_BUS_HOST", "localhost")
    port = int(os.environ.get("OVOS_BUS_PORT", "8181"))
    route = os.environ.get("OVOS_BUS_ROUTE", "/core")
    ssl = os.environ.get("OVOS_BUS_SSL", "false").lower() == "true"

    logger.info(f"Connecting to OVOS bus at {host}:{port}{route}")
    _bus = connect_bus(host=host, port=port, route=route, ssl=ssl)

    try:
        yield
    finally:
        if _bus:
            _bus.disconnect()
            logger.info("Disconnected from OVOS bus")


def create_server(
    name: str = "OVOS MCP Server",
    host: str | None = None,
    port: int | None = None,
) -> FastMCP:
    """Create and configure the FastMCP server.

    Args:
        name: The server name.
        host: Optional OVOS bus host override.
        port: Optional OVOS bus port override.

    Returns:
        Configured FastMCP server instance.
    """
    global _bus

    # Override environment if provided
    if host:
        os.environ["OVOS_BUS_HOST"] = host
    if port:
        os.environ["OVOS_BUS_PORT"] = str(port)

    server = FastMCP(
        name=name,
        lifespan=lifespan,
    )

    return server


def _ensure_bus() -> OVOSBusClient:
    """Ensure the bus client is available.

    Returns:
        The OVOS bus client.

    Raises:
        RuntimeError: If the bus is not connected.
    """
    if _bus is None:
        raise RuntimeError("OVOS bus not connected. Server not started properly.")
    return _bus


# Create default server instance
mcp = FastMCP(
    name="OVOS MCP Server",
    instructions="""
    OVOS MCP Server provides tools to interact with an OpenVoiceOS voice assistant.
    
    Available tool categories:
    - Speech: Make OVOS speak, listen for voice commands, control microphone
    - Audio: Control audio playback (play, pause, stop, seek, track info)
    - Volume: Control system volume levels
    - OCP: OVOS Common Play media framework for music, podcasts, videos
    - Skills: List, activate, deactivate, install, and uninstall skills
    - System: Control listener state, GUI, homescreens, and system status
    
    The server connects to the OVOS message bus to send commands and receive responses.
    Most operations are asynchronous and return confirmation messages.
    """,
)


def _register_tools_lazy() -> None:
    """Register all tools with the MCP server lazily."""
    # This is called during server startup to register tools
    # We need to ensure bus is connected first
    pass


# Eagerly register tools using a factory pattern
# Tools will use _ensure_bus() internally to get the bus client
def _create_tool_registrar():
    """Create a tool registrar that registers all tools on first access."""
    registered = False

    def ensure_registered():
        nonlocal registered
        if not registered and _bus is not None:
            register_all_tools(mcp, _bus)
            registered = True

    return ensure_registered


_ensure_tools_registered = _create_tool_registrar()


# Override the lifespan to also register tools
@asynccontextmanager
async def _full_lifespan(server: FastMCP) -> AsyncIterator[None]:
    """Full lifespan including tool registration."""
    global _bus

    host = os.environ.get("OVOS_BUS_HOST", "localhost")
    port = int(os.environ.get("OVOS_BUS_PORT", "8181"))
    route = os.environ.get("OVOS_BUS_ROUTE", "/core")
    ssl = os.environ.get("OVOS_BUS_SSL", "false").lower() == "true"

    logger.info(f"Connecting to OVOS bus at {host}:{port}{route}")
    _bus = connect_bus(host=host, port=port, route=route, ssl=ssl)

    # Register all tools now that bus is connected
    register_all_tools(mcp, _bus)
    logger.info("Registered all OVOS MCP tools")

    try:
        yield
    finally:
        if _bus:
            _bus.disconnect()
            logger.info("Disconnected from OVOS bus")


# Update server lifespan
mcp._lifespan = _full_lifespan


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    transport: str = "http",
    bus_host: str = "localhost",
    bus_port: int = 8181,
) -> None:
    """Run the OVOS MCP server.

    Args:
        host: HTTP server host address.
        port: HTTP server port.
        transport: Transport type ('http', 'sse', or 'stdio').
        bus_host: OVOS message bus host.
        bus_port: OVOS message bus port.
    """
    os.environ["OVOS_BUS_HOST"] = bus_host
    os.environ["OVOS_BUS_PORT"] = str(bus_port)

    mcp.run(transport=transport, host=host, port=port)


def main() -> None:
    """CLI entry point for ovos-mcp-server."""
    import argparse

    parser = argparse.ArgumentParser(
        description="OVOS MCP Server - Expose OpenVoiceOS skills via HTTP streaming"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="HTTP server host address (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP server port (default: 8000)",
    )
    parser.add_argument(
        "--transport",
        default="http",
        choices=["http", "sse", "stdio"],
        help="Transport type (default: http)",
    )
    parser.add_argument(
        "--bus-host",
        default="localhost",
        help="OVOS message bus host (default: localhost)",
    )
    parser.add_argument(
        "--bus-port",
        type=int,
        default=8181,
        help="OVOS message bus port (default: 8181)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    run_server(
        host=args.host,
        port=args.port,
        transport=args.transport,
        bus_host=args.bus_host,
        bus_port=args.bus_port,
    )


if __name__ == "__main__":
    main()
