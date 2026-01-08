"""OCP (OVOS Common Play) media tools for OVOS MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ovos_bus_client import Message

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from ovos_skill_mcp.bus import OVOSBusClient


def register_ocp_tools(mcp: FastMCP, bus: OVOSBusClient) -> None:
    """Register OCP media playback tools with the MCP server.

    OCP (OVOS Common Play) is the unified media playback framework
    for OVOS that handles audio and video from various sources.

    Args:
        mcp: The FastMCP server instance.
        bus: The OVOS bus client instance.
    """

    @mcp.tool()
    async def ocp_search(query: str, media_type: str | None = None) -> str:
        """Search for media using OVOS Common Play.

        This triggers a search across all registered OCP media skills.

        Args:
            query: The search query (e.g., "play beethoven", "jazz music").
            media_type: Optional media type filter (e.g., "music", "video", "podcast").

        Returns:
            Confirmation that the search was initiated.
        """
        data = {"phrase": query}
        if media_type:
            data["question_type"] = media_type
        await bus.emit_async(Message("ovos.common_play.query", data))
        return f"OCP search initiated for: {query}"

    @mcp.tool()
    async def ocp_play() -> str:
        """Start or resume OCP media playback.

        Returns:
            Confirmation that play command was sent.
        """
        await bus.emit_async(Message("ovos.common_play.play"))
        return "OCP playback started"

    @mcp.tool()
    async def ocp_pause() -> str:
        """Pause OCP media playback.

        Returns:
            Confirmation that pause command was sent.
        """
        await bus.emit_async(Message("ovos.common_play.pause"))
        return "OCP playback paused"

    @mcp.tool()
    async def ocp_resume() -> str:
        """Resume paused OCP media playback.

        Returns:
            Confirmation that resume command was sent.
        """
        await bus.emit_async(Message("ovos.common_play.resume"))
        return "OCP playback resumed"

    @mcp.tool()
    async def ocp_stop() -> str:
        """Stop OCP media playback.

        Returns:
            Confirmation that stop command was sent.
        """
        await bus.emit_async(Message("ovos.common_play.stop"))
        return "OCP playback stopped"

    @mcp.tool()
    async def ocp_next() -> str:
        """Skip to the next track in OCP playlist.

        Returns:
            Confirmation that next command was sent.
        """
        await bus.emit_async(Message("ovos.common_play.next"))
        return "Skipped to next track"

    @mcp.tool()
    async def ocp_previous() -> str:
        """Go back to the previous track in OCP playlist.

        Returns:
            Confirmation that previous command was sent.
        """
        await bus.emit_async(Message("ovos.common_play.previous"))
        return "Went back to previous track"

    @mcp.tool()
    async def ocp_seek(seconds: int) -> str:
        """Seek to a position in the current OCP media.

        Args:
            seconds: Position in seconds to seek to.

        Returns:
            Confirmation of the seek operation.
        """
        await bus.emit_async(Message("ovos.common_play.seek", {"seconds": seconds}))
        return f"Seeked to {seconds} seconds"

    @mcp.tool()
    async def ocp_shuffle(enable: bool = True) -> str:
        """Enable or disable shuffle mode in OCP.

        Args:
            enable: Whether to enable (True) or disable (False) shuffle.

        Returns:
            Confirmation of the shuffle setting.
        """
        await bus.emit_async(Message("ovos.common_play.shuffle", {"shuffle": enable}))
        return f"Shuffle {'enabled' if enable else 'disabled'}"

    @mcp.tool()
    async def ocp_repeat(mode: str = "none") -> str:
        """Set the repeat mode in OCP.

        Args:
            mode: Repeat mode - 'none', 'track', or 'playlist'.

        Returns:
            Confirmation of the repeat setting.
        """
        await bus.emit_async(Message("ovos.common_play.repeat", {"repeat": mode}))
        return f"Repeat mode set to '{mode}'"

    @mcp.tool()
    async def ocp_get_player_state() -> dict:
        """Get the current OCP player state.

        Returns:
            Dictionary containing player state information.
        """
        response = await bus.wait_for_response_async(
            Message("ovos.common_play.player.state.get"),
            reply_type="ovos.common_play.player.state",
            timeout=5.0,
        )
        if response:
            return {
                "state": response.data.get("state", "unknown"),
            }
        return {"state": "unknown", "error": "No response from OCP"}

    @mcp.tool()
    async def ocp_get_track() -> dict:
        """Get information about the currently playing track in OCP.

        Returns:
            Dictionary containing track information.
        """
        response = await bus.wait_for_response_async(
            Message("ovos.common_play.track.info.get"),
            reply_type="ovos.common_play.track.info",
            timeout=5.0,
        )
        if response:
            return response.data
        return {"error": "No track information available"}

    @mcp.tool()
    async def ocp_get_playlist() -> dict:
        """Get the current OCP playlist.

        Returns:
            Dictionary containing the playlist information.
        """
        response = await bus.wait_for_response_async(
            Message("ovos.common_play.playlist.get"),
            reply_type="ovos.common_play.playlist",
            timeout=5.0,
        )
        if response:
            return {
                "playlist": response.data.get("playlist", []),
                "current_index": response.data.get("index", 0),
            }
        return {"playlist": [], "error": "No playlist available"}

    @mcp.tool()
    async def ocp_clear_playlist() -> str:
        """Clear the current OCP playlist.

        Returns:
            Confirmation that the playlist was cleared.
        """
        await bus.emit_async(Message("ovos.common_play.playlist.clear"))
        return "OCP playlist cleared"

    @mcp.tool()
    async def ocp_get_media_skills() -> dict:
        """Get a list of registered OCP media skills.

        Returns:
            Dictionary containing the list of media skills.
        """
        response = await bus.wait_for_response_async(
            Message("ovos.common_play.skills.get"),
            reply_type="ovos.common_play.announce",
            timeout=10.0,
        )
        if response:
            return {
                "skill_id": response.data.get("skill_id"),
                "skill_name": response.data.get("skill_name"),
                "media_types": response.data.get("media_types", []),
            }
        return {"error": "No response from OCP skills"}

    @mcp.tool()
    async def ocp_play_featured(skill_id: str) -> str:
        """Play featured tracks from a specific OCP skill.

        Args:
            skill_id: The ID of the OCP skill to play featured tracks from.

        Returns:
            Confirmation that featured playback was requested.
        """
        await bus.emit_async(
            Message(
                "ovos.common_play.featured_tracks.play",
                {"skill_id": skill_id},
            )
        )
        return f"Playing featured tracks from skill '{skill_id}'"

    @mcp.tool()
    async def ocp_like_track() -> str:
        """Like/favorite the currently playing track.

        Returns:
            Confirmation that the track was liked.
        """
        await bus.emit_async(Message("ovos.common_play.like"))
        return "Current track liked"

    @mcp.tool()
    async def ocp_dislike_track() -> str:
        """Dislike the currently playing track.

        Returns:
            Confirmation that the track was disliked.
        """
        await bus.emit_async(Message("ovos.common_play.dislike"))
        return "Current track disliked"
