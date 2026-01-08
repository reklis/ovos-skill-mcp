"""Speech-related tools for OVOS MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ovos_bus_client import Message

if TYPE_CHECKING:
    from fastmcp import FastMCP
    from ovos_skill_mcp.bus import OVOSBusClient


def register_speech_tools(mcp: FastMCP, bus: OVOSBusClient) -> None:
    """Register speech-related tools with the MCP server.

    Args:
        mcp: The FastMCP server instance.
        bus: The OVOS bus client instance.
    """

    @mcp.tool()
    async def speak(
        text: str,
        lang: str = "en-us",
        expect_response: bool = False,
    ) -> str:
        """Make OVOS speak the given text aloud.

        Args:
            text: The text to speak.
            lang: The language code for speech synthesis (e.g., 'en-us', 'es-es').
            expect_response: Whether to activate the microphone after speaking.

        Returns:
            Confirmation message indicating what will be spoken.
        """
        await bus.emit_async(
            Message(
                "speak",
                {
                    "utterance": text,
                    "lang": lang,
                    "expect_response": expect_response,
                },
            )
        )
        return f"Speaking: {text}"

    @mcp.tool()
    async def listen() -> str:
        """Activate the microphone and start listening for voice input.

        This triggers OVOS to wake up and listen for a voice command,
        similar to saying the wake word.

        Returns:
            Confirmation that listening has been activated.
        """
        await bus.emit_async(Message("mycroft.mic.listen"))
        return "Listening activated - microphone is now active"

    @mcp.tool()
    async def stop_speaking() -> str:
        """Stop any ongoing speech synthesis.

        This immediately halts any text-to-speech output that OVOS
        is currently producing.

        Returns:
            Confirmation that speech has been stopped.
        """
        await bus.emit_async(Message("mycroft.audio.speech.stop"))
        return "Speech stopped"

    @mcp.tool()
    async def send_utterance(
        utterance: str,
        lang: str = "en-us",
    ) -> str:
        """Send a text utterance to OVOS as if it were spoken by the user.

        This injects a command into OVOS's intent processing system,
        allowing you to trigger skills and actions programmatically.

        Args:
            utterance: The text command to process (e.g., "what time is it").
            lang: The language code for intent processing.

        Returns:
            Confirmation that the utterance was sent.
        """
        await bus.emit_async(
            Message(
                "recognizer_loop:utterance",
                {
                    "utterances": [utterance],
                    "lang": lang,
                },
            )
        )
        return f"Utterance sent: {utterance}"

    @mcp.tool()
    async def mute_microphone() -> str:
        """Mute the microphone to prevent wake word detection.

        When muted, OVOS will not respond to wake words or voice commands
        until unmuted.

        Returns:
            Confirmation that the microphone is muted.
        """
        await bus.emit_async(Message("mycroft.mic.mute"))
        return "Microphone muted"

    @mcp.tool()
    async def unmute_microphone() -> str:
        """Unmute the microphone to enable wake word detection.

        Re-enables voice command listening after being muted.

        Returns:
            Confirmation that the microphone is unmuted.
        """
        await bus.emit_async(Message("mycroft.mic.unmute"))
        return "Microphone unmuted"

    @mcp.tool()
    async def get_microphone_status() -> dict:
        """Get the current microphone mute status.

        Returns:
            Dictionary containing the mute status of the microphone.
        """
        response = await bus.wait_for_response_async(
            Message("mycroft.mic.get_status"),
            reply_type="mycroft.mic.get_status.response",
            timeout=5.0,
        )
        if response:
            return {"muted": response.data.get("muted", False)}
        return {"muted": False, "error": "No response from OVOS"}
