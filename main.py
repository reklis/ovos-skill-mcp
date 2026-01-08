#!/usr/bin/env python3
"""Main entry point for OVOS MCP Server."""

from ovos_skill_mcp.server import mcp, run_server

if __name__ == "__main__":
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
        import logging

        logging.basicConfig(level=logging.DEBUG)

    run_server(
        host=args.host,
        port=args.port,
        transport=args.transport,
        bus_host=args.bus_host,
        bus_port=args.bus_port,
    )
