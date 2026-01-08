"""Volume control tools for OVOS MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ovos_bus_client import Message

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from ovos_skill_mcp.bus import OVOSBusClient


def register_volume_tools(mcp: FastMCP, bus: OVOSBusClient) -> None:
    """Register volume control tools with the MCP server.

    Args:
        mcp: The FastMCP server instance.
        bus: The OVOS bus client instance.
    """

    @mcp.tool()
    async def set_volume(percent: float) -> str:
        """Set the system volume level.

        Args:
            percent: Volume level from 0.0 (mute) to 1.0 (maximum).

        Returns:
            Confirmation of the new volume level.
        """
        # Clamp value between 0 and 1
        percent = max(0.0, min(1.0, percent))
        await bus.emit_async(
            Message(
                "mycroft.volume.set",
                {"percent": percent},
            )
        )
        return f"Volume set to {int(percent * 100)}%"

    @mcp.tool()
    async def get_volume() -> dict:
        """Get the current system volume level.

        Returns:
            Dictionary containing the current volume as a percentage (0.0-1.0).
        """
        response = await bus.wait_for_response_async(
            Message("mycroft.volume.get"),
            reply_type="mycroft.volume.get.response",
            timeout=5.0,
        )
        if response:
            percent = response.data.get("percent", 0.5)
            return {
                "percent": percent,
                "percent_display": f"{int(percent * 100)}%",
            }
        return {"percent": 0.5, "error": "No response from volume service"}

    @mcp.tool()
    async def increase_volume(amount: float = 0.1) -> str:
        """Increase the system volume.

        Args:
            amount: Amount to increase (0.0-1.0). Default is 0.1 (10%).

        Returns:
            Confirmation of the volume increase.
        """
        await bus.emit_async(
            Message(
                "mycroft.volume.increase",
                {"amount": amount},
            )
        )
        return f"Volume increased by {int(amount * 100)}%"

    @mcp.tool()
    async def decrease_volume(amount: float = 0.1) -> str:
        """Decrease the system volume.

        Args:
            amount: Amount to decrease (0.0-1.0). Default is 0.1 (10%).

        Returns:
            Confirmation of the volume decrease.
        """
        await bus.emit_async(
            Message(
                "mycroft.volume.decrease",
                {"amount": amount},
            )
        )
        return f"Volume decreased by {int(amount * 100)}%"

    @mcp.tool()
    async def mute_volume() -> str:
        """Mute the system volume.

        Returns:
            Confirmation that volume is muted.
        """
        await bus.emit_async(Message("mycroft.volume.mute"))
        return "Volume muted"

    @mcp.tool()
    async def unmute_volume() -> str:
        """Unmute the system volume.

        Returns:
            Confirmation that volume is unmuted.
        """
        await bus.emit_async(Message("mycroft.volume.unmute"))
        return "Volume unmuted"

    @mcp.tool()
    async def duck_volume() -> str:
        """Duck (temporarily lower) the volume for announcements.

        This is typically used when TTS or notifications need to play
        over background audio.

        Returns:
            Confirmation that volume ducking is active.
        """
        await bus.emit_async(Message("recognizer_loop:audio_output_start"))
        return "Volume ducked"

    @mcp.tool()
    async def unduck_volume() -> str:
        """Restore volume after ducking.

        Returns:
            Confirmation that volume has been restored.
        """
        await bus.emit_async(Message("recognizer_loop:audio_output_end"))
        return "Volume restored from ducking"
