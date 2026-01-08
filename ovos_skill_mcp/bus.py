"""OVOS Message Bus client wrapper for async operations."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from ovos_bus_client import MessageBusClient, Message

logger = logging.getLogger(__name__)


class OVOSBusClient:
    """Async wrapper around the OVOS MessageBusClient."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8181,
        route: str = "/core",
        ssl: bool = False,
    ):
        """Initialize the OVOS bus client.

        Args:
            host: The message bus host address.
            port: The message bus port.
            route: The WebSocket route.
            ssl: Whether to use SSL for the connection.
        """
        self.host = host
        self.port = port
        self.route = route
        self.ssl = ssl
        self._client: MessageBusClient | None = None
        self._connected = False

    def connect(self) -> None:
        """Connect to the OVOS message bus."""
        if self._client is not None:
            return

        self._client = MessageBusClient(
            host=self.host,
            port=self.port,
            route=self.route,
            ssl=self.ssl,
        )
        self._client.run_in_thread()
        self._client.connected_event.wait(timeout=10)
        self._connected = True
        logger.info(f"Connected to OVOS bus at {self.host}:{self.port}")

    def disconnect(self) -> None:
        """Disconnect from the OVOS message bus."""
        if self._client is not None:
            self._client.close()
            self._client = None
            self._connected = False
            logger.info("Disconnected from OVOS bus")

    @property
    def connected(self) -> bool:
        """Check if the client is connected."""
        return self._connected and self._client is not None

    def emit(self, message: Message) -> None:
        """Emit a message to the bus (fire and forget).

        Args:
            message: The message to emit.
        """
        if not self._client:
            raise RuntimeError("Not connected to OVOS bus")
        self._client.emit(message)

    async def emit_async(self, message: Message) -> None:
        """Emit a message asynchronously.

        Args:
            message: The message to emit.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.emit, message)

    def wait_for_response(
        self,
        message: Message,
        reply_type: str | None = None,
        timeout: float = 10.0,
    ) -> Message | None:
        """Wait for a response to a message.

        Args:
            message: The message to send.
            reply_type: The expected response message type.
            timeout: Timeout in seconds.

        Returns:
            The response message, or None if timed out.
        """
        if not self._client:
            raise RuntimeError("Not connected to OVOS bus")
        return self._client.wait_for_response(
            message, reply_type=reply_type, timeout=timeout
        )

    async def wait_for_response_async(
        self,
        message: Message,
        reply_type: str | None = None,
        timeout: float = 10.0,
    ) -> Message | None:
        """Wait for a response asynchronously.

        Args:
            message: The message to send.
            reply_type: The expected response message type.
            timeout: Timeout in seconds.

        Returns:
            The response message, or None if timed out.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.wait_for_response(message, reply_type, timeout),
        )

    def on(self, event_type: str, handler: Any) -> None:
        """Register a handler for a message type.

        Args:
            event_type: The message type to listen for.
            handler: The handler function.
        """
        if not self._client:
            raise RuntimeError("Not connected to OVOS bus")
        self._client.on(event_type, handler)

    def remove(self, event_type: str, handler: Any) -> None:
        """Remove a handler for a message type.

        Args:
            event_type: The message type.
            handler: The handler function to remove.
        """
        if not self._client:
            raise RuntimeError("Not connected to OVOS bus")
        self._client.remove(event_type, handler)


# Global bus instance
_bus: OVOSBusClient | None = None


def get_bus() -> OVOSBusClient:
    """Get the global bus client instance.

    Returns:
        The global OVOSBusClient instance.
    """
    global _bus
    if _bus is None:
        _bus = OVOSBusClient()
    return _bus


def connect_bus(
    host: str = "localhost",
    port: int = 8181,
    route: str = "/core",
    ssl: bool = False,
) -> OVOSBusClient:
    """Connect to the OVOS bus and return the client.

    Args:
        host: The message bus host address.
        port: The message bus port.
        route: The WebSocket route.
        ssl: Whether to use SSL.

    Returns:
        The connected OVOSBusClient instance.
    """
    global _bus
    _bus = OVOSBusClient(host=host, port=port, route=route, ssl=ssl)
    _bus.connect()
    return _bus
