"""System control tools for OVOS MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ovos_bus_client import Message

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from ovos_skill_mcp.bus import OVOSBusClient


def register_system_tools(mcp: FastMCP, bus: OVOSBusClient) -> None:
    """Register system control tools with the MCP server.

    Args:
        mcp: The FastMCP server instance.
        bus: The OVOS bus client instance.
    """

    @mcp.tool()
    async def stop_all() -> str:
        """Send a global stop command to all skills and services.

        This stops any ongoing speech, media playback, and skill activities.

        Returns:
            Confirmation that the stop command was sent.
        """
        await bus.emit_async(Message("mycroft.stop"))
        return "Global stop command sent - all activities halted"

    @mcp.tool()
    async def check_system_ready() -> dict:
        """Check if the OVOS system is fully ready and operational.

        Returns:
            Dictionary indicating the system ready status.
        """
        response = await bus.wait_for_response_async(
            Message("mycroft.skills.is_ready"),
            reply_type="mycroft.skills.is_ready.response",
            timeout=5.0,
        )
        if response:
            return {
                "ready": response.data.get("status", False),
                "message": "System is ready"
                if response.data.get("status")
                else "System is not ready",
            }
        return {"ready": False, "message": "No response from system"}

    @mcp.tool()
    async def get_listener_state() -> dict:
        """Get the current state of the voice listener.

        Returns:
            Dictionary containing the listener state and mode.
        """
        response = await bus.wait_for_response_async(
            Message("recognizer_loop:state.get"),
            reply_type="recognizer_loop:state",
            timeout=5.0,
        )
        if response:
            return {
                "state": response.data.get("state", "unknown"),
                "mode": response.data.get("mode", "unknown"),
            }
        return {"state": "unknown", "mode": "unknown", "error": "No response"}

    @mcp.tool()
    async def set_listener_state(state: str, mode: str | None = None) -> str:
        """Set the voice listener state and mode.

        Args:
            state: The listener state (e.g., 'sleeping', 'awake').
            mode: The listening mode (e.g., 'wakeword', 'continuous').

        Returns:
            Confirmation of the state change.
        """
        data = {"state": state}
        if mode:
            data["mode"] = mode
        await bus.emit_async(Message("recognizer_loop:state.set", data))
        return f"Listener state set to: {state}" + (f" (mode: {mode})" if mode else "")

    @mcp.tool()
    async def sleep_listener() -> str:
        """Put the voice listener to sleep (disable wake word detection).

        Returns:
            Confirmation that the listener is sleeping.
        """
        await bus.emit_async(Message("recognizer_loop:sleep"))
        return "Voice listener is now sleeping"

    @mcp.tool()
    async def wake_listener() -> str:
        """Wake up the voice listener (enable wake word detection).

        Returns:
            Confirmation that the listener is awake.
        """
        await bus.emit_async(Message("recognizer_loop:wake_up"))
        return "Voice listener is now awake"

    @mcp.tool()
    async def get_stt_languages() -> dict:
        """Get the list of supported speech-to-text languages.

        Returns:
            Dictionary containing the supported STT languages.
        """
        response = await bus.wait_for_response_async(
            Message("ovos.languages.stt"),
            reply_type="ovos.languages.stt.response",
            timeout=5.0,
        )
        if response:
            return {"languages": response.data.get("langs", [])}
        return {"languages": [], "error": "No response from STT service"}

    @mcp.tool()
    async def get_tts_languages() -> dict:
        """Get the list of supported text-to-speech languages.

        Returns:
            Dictionary containing the supported TTS languages.
        """
        response = await bus.wait_for_response_async(
            Message("ovos.languages.tts"),
            reply_type="ovos.languages.tts.response",
            timeout=5.0,
        )
        if response:
            return {"languages": response.data.get("langs", [])}
        return {"languages": [], "error": "No response from TTS service"}

    @mcp.tool()
    async def get_gui_status() -> dict:
        """Check if a GUI client is connected.

        Returns:
            Dictionary indicating GUI connection status.
        """
        response = await bus.wait_for_response_async(
            Message("gui.status.request"),
            reply_type="gui.status.request.response",
            timeout=5.0,
        )
        if response:
            return {"connected": response.data.get("connected", False)}
        return {"connected": False, "error": "No response from GUI service"}

    @mcp.tool()
    async def show_gui_page(
        page: str,
        namespace: str,
        data: dict | None = None,
    ) -> str:
        """Show a specific GUI page on connected displays.

        Args:
            page: The QML page file to display.
            namespace: The skill namespace for the page.
            data: Optional data to pass to the page.

        Returns:
            Confirmation that the page show request was sent.
        """
        message_data = {
            "page": page,
            "__from": namespace,
        }
        if data:
            message_data["data"] = data

        await bus.emit_async(Message("gui.page.show", message_data))
        return f"GUI page '{page}' display requested"

    @mcp.tool()
    async def clear_gui_namespace(namespace: str) -> str:
        """Clear all GUI pages for a namespace.

        Args:
            namespace: The skill namespace to clear.

        Returns:
            Confirmation that the namespace was cleared.
        """
        await bus.emit_async(Message("gui.clear.namespace", {"__from": namespace}))
        return f"GUI namespace '{namespace}' cleared"

    @mcp.tool()
    async def set_gui_value(
        namespace: str, key: str, value: str | int | float | bool | dict | list
    ) -> str:
        """Set a value in the GUI namespace for data binding.

        Args:
            namespace: The skill namespace.
            key: The variable name to set.
            value: The value to set.

        Returns:
            Confirmation that the value was set.
        """
        await bus.emit_async(
            Message(
                "gui.value.set",
                {
                    "__from": namespace,
                    key: value,
                },
            )
        )
        return f"GUI value '{key}' set in namespace '{namespace}'"

    @mcp.tool()
    async def show_homescreen() -> str:
        """Show the active homescreen on the GUI.

        Returns:
            Confirmation that the homescreen display was requested.
        """
        await bus.emit_async(Message("homescreen.manager.show_active"))
        return "Homescreen display requested"

    @mcp.tool()
    async def list_homescreens() -> dict:
        """Get a list of available homescreens.

        Returns:
            Dictionary containing the list of available homescreens.
        """
        response = await bus.wait_for_response_async(
            Message("homescreen.manager.list"),
            reply_type="homescreen.manager.list.response",
            timeout=5.0,
        )
        if response:
            return {"homescreens": response.data.get("homescreens", [])}
        return {"homescreens": [], "error": "No response from homescreen manager"}

    @mcp.tool()
    async def set_active_homescreen(homescreen_id: str) -> str:
        """Set the active homescreen by ID.

        Args:
            homescreen_id: The ID of the homescreen to activate.

        Returns:
            Confirmation that the homescreen was set.
        """
        await bus.emit_async(
            Message("homescreen.manager.set_active", {"id": homescreen_id})
        )
        return f"Active homescreen set to '{homescreen_id}'"
