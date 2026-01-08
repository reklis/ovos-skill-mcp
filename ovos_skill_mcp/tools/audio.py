"""Audio service tools for OVOS MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ovos_bus_client import Message

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from ovos_skill_mcp.bus import OVOSBusClient


def register_audio_tools(mcp: FastMCP, bus: OVOSBusClient) -> None:
    """Register audio service tools with the MCP server.

    Args:
        mcp: The FastMCP server instance.
        bus: The OVOS bus client instance.
    """

    @mcp.tool()
    async def play_audio(
        tracks: list[str],
        repeat: bool = False,
    ) -> str:
        """Play audio tracks through the OVOS audio service.

        Args:
            tracks: List of audio URIs or file paths to play.
            repeat: Whether to repeat the playlist when finished.

        Returns:
            Confirmation that playback has started.
        """
        await bus.emit_async(
            Message(
                "mycroft.audio.service.play",
                {
                    "tracks": tracks,
                    "repeat": repeat,
                },
            )
        )
        return f"Playing {len(tracks)} track(s)"

    @mcp.tool()
    async def queue_audio(tracks: list[str]) -> str:
        """Queue audio tracks for playback after current track finishes.

        Args:
            tracks: List of audio URIs or file paths to queue.

        Returns:
            Confirmation that tracks were queued.
        """
        await bus.emit_async(
            Message(
                "mycroft.audio.service.queue",
                {"tracks": tracks},
            )
        )
        return f"Queued {len(tracks)} track(s)"

    @mcp.tool()
    async def pause_audio() -> str:
        """Pause the currently playing audio.

        Returns:
            Confirmation that audio has been paused.
        """
        await bus.emit_async(Message("mycroft.audio.service.pause"))
        return "Audio paused"

    @mcp.tool()
    async def resume_audio() -> str:
        """Resume paused audio playback.

        Returns:
            Confirmation that audio playback has resumed.
        """
        await bus.emit_async(Message("mycroft.audio.service.resume"))
        return "Audio resumed"

    @mcp.tool()
    async def stop_audio() -> str:
        """Stop audio playback completely.

        Returns:
            Confirmation that audio has been stopped.
        """
        await bus.emit_async(Message("mycroft.audio.service.stop"))
        return "Audio stopped"

    @mcp.tool()
    async def next_track() -> str:
        """Skip to the next track in the playlist.

        Returns:
            Confirmation that skipped to next track.
        """
        await bus.emit_async(Message("mycroft.audio.service.next"))
        return "Skipped to next track"

    @mcp.tool()
    async def previous_track() -> str:
        """Go back to the previous track in the playlist.

        Returns:
            Confirmation that went back to previous track.
        """
        await bus.emit_async(Message("mycroft.audio.service.prev"))
        return "Went back to previous track"

    @mcp.tool()
    async def seek_audio(position_ms: int) -> str:
        """Seek to a specific position in the current track.

        Args:
            position_ms: Position in milliseconds to seek to.

        Returns:
            Confirmation of the seek operation.
        """
        await bus.emit_async(
            Message(
                "mycroft.audio.service.set_track_position",
                {"position": position_ms},
            )
        )
        return f"Seeked to position {position_ms}ms"

    @mcp.tool()
    async def seek_forward(seconds: int = 30) -> str:
        """Seek forward in the current track.

        Args:
            seconds: Number of seconds to seek forward.

        Returns:
            Confirmation of the seek operation.
        """
        await bus.emit_async(
            Message(
                "mycroft.audio.service.seek_forward",
                {"seconds": seconds},
            )
        )
        return f"Seeked forward {seconds} seconds"

    @mcp.tool()
    async def seek_backward(seconds: int = 30) -> str:
        """Seek backward in the current track.

        Args:
            seconds: Number of seconds to seek backward.

        Returns:
            Confirmation of the seek operation.
        """
        await bus.emit_async(
            Message(
                "mycroft.audio.service.seek_backward",
                {"seconds": seconds},
            )
        )
        return f"Seeked backward {seconds} seconds"

    @mcp.tool()
    async def get_track_info() -> dict:
        """Get information about the currently playing track.

        Returns:
            Dictionary containing track information (title, artist, etc.).
        """
        response = await bus.wait_for_response_async(
            Message("mycroft.audio.service.track_info"),
            reply_type="mycroft.audio.service.track_info_reply",
            timeout=5.0,
        )
        if response:
            return response.data
        return {"error": "No track info available"}

    @mcp.tool()
    async def get_track_position() -> dict:
        """Get the current playback position of the audio.

        Returns:
            Dictionary containing the current position in milliseconds.
        """
        response = await bus.wait_for_response_async(
            Message("mycroft.audio.service.get_track_position"),
            reply_type="mycroft.audio.service.get_track_position.response",
            timeout=5.0,
        )
        if response:
            return {"position_ms": response.data.get("position", 0)}
        return {"position_ms": 0, "error": "No response from audio service"}

    @mcp.tool()
    async def get_track_length() -> dict:
        """Get the total length of the current track.

        Returns:
            Dictionary containing the track length in milliseconds.
        """
        response = await bus.wait_for_response_async(
            Message("mycroft.audio.service.get_track_length"),
            reply_type="mycroft.audio.service.get_track_length.response",
            timeout=5.0,
        )
        if response:
            return {"length_ms": response.data.get("length", 0)}
        return {"length_ms": 0, "error": "No response from audio service"}

    @mcp.tool()
    async def play_sound(uri: str) -> str:
        """Play a sound file immediately (may play over TTS).

        This is useful for notification sounds, alerts, etc.

        Args:
            uri: The URI or path to the sound file.

        Returns:
            Confirmation that the sound is playing.
        """
        await bus.emit_async(
            Message(
                "mycroft.audio.play_sound",
                {"uri": uri},
            )
        )
        return f"Playing sound: {uri}"
