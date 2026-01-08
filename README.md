# OVOS Skill MCP

A [FastMCP](https://github.com/jlowin/fastmcp) server that exposes [OpenVoiceOS](https://openvoiceos.org/) (OVOS) skills and functionality via HTTP streaming using the Model Context Protocol (MCP).

This package allows LLMs and other MCP clients to interact with your OVOS voice assistant programmatically, enabling capabilities like:
- Making OVOS speak text
- Controlling media playback
- Managing volume
- Interacting with skills
- Controlling the GUI

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Client (LLM)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Streaming (Streamable HTTP)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              ovos-skill-mcp (FastMCP Server)                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Tools: speak, listen, play_media, set_volume, ...   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ WebSocket (ws://localhost:8181/core)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    OVOS Message Bus                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │ ovos-audio  │ │ ovos-core   │ │ ovos-dinkum-listener│   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
pip install ovos-skill-mcp
```

Or install from source:

```bash
git clone https://github.com/OpenVoiceOS/ovos-skill-mcp.git
cd ovos-skill-mcp
pip install -e .
```

## Quick Start

### Running the Server

```bash
# Start with default settings (HTTP on port 8000, OVOS bus on localhost:8181)
ovos-mcp-server

# Or with custom settings
ovos-mcp-server --host 0.0.0.0 --port 8000 --bus-host 192.168.1.100 --bus-port 8181
```

### Using with Python

```python
from ovos_skill_mcp import mcp, run_server

# Run the server
run_server(host="0.0.0.0", port=8000)
```

### Environment Variables

You can configure the OVOS bus connection using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OVOS_BUS_HOST` | `localhost` | OVOS message bus host |
| `OVOS_BUS_PORT` | `8181` | OVOS message bus port |
| `OVOS_BUS_ROUTE` | `/core` | WebSocket route |
| `OVOS_BUS_SSL` | `false` | Use SSL for connection |

## Available Tools

### Speech Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `speak` | Make OVOS speak text aloud | `text` (str), `lang` (str, default: "en-us"), `expect_response` (bool) |
| `listen` | Activate microphone for voice input | - |
| `stop_speaking` | Stop ongoing speech synthesis | - |
| `send_utterance` | Send text command as if spoken | `utterance` (str), `lang` (str) |
| `mute_microphone` | Mute the microphone | - |
| `unmute_microphone` | Unmute the microphone | - |
| `get_microphone_status` | Get microphone mute status | - |

### Audio Service Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `play_audio` | Play audio tracks | `tracks` (list[str]), `repeat` (bool) |
| `queue_audio` | Queue tracks for playback | `tracks` (list[str]) |
| `pause_audio` | Pause current playback | - |
| `resume_audio` | Resume paused playback | - |
| `stop_audio` | Stop playback | - |
| `next_track` | Skip to next track | - |
| `previous_track` | Go to previous track | - |
| `seek_audio` | Seek to position | `position_ms` (int) |
| `seek_forward` | Seek forward | `seconds` (int, default: 30) |
| `seek_backward` | Seek backward | `seconds` (int, default: 30) |
| `get_track_info` | Get current track info | - |
| `get_track_position` | Get playback position | - |
| `get_track_length` | Get track duration | - |
| `play_sound` | Play notification sound | `uri` (str) |

### Volume Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `set_volume` | Set volume level | `percent` (float, 0.0-1.0) |
| `get_volume` | Get current volume | - |
| `increase_volume` | Increase volume | `amount` (float, default: 0.1) |
| `decrease_volume` | Decrease volume | `amount` (float, default: 0.1) |
| `mute_volume` | Mute system volume | - |
| `unmute_volume` | Unmute system volume | - |
| `duck_volume` | Temporarily lower volume | - |
| `unduck_volume` | Restore volume after ducking | - |

### OCP (OVOS Common Play) Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `ocp_search` | Search for media | `query` (str), `media_type` (str, optional) |
| `ocp_play` | Start playback | - |
| `ocp_pause` | Pause playback | - |
| `ocp_resume` | Resume playback | - |
| `ocp_stop` | Stop playback | - |
| `ocp_next` | Next track | - |
| `ocp_previous` | Previous track | - |
| `ocp_seek` | Seek to position | `seconds` (int) |
| `ocp_shuffle` | Toggle shuffle | `enable` (bool) |
| `ocp_repeat` | Set repeat mode | `mode` (str: "none", "track", "playlist") |
| `ocp_get_player_state` | Get player state | - |
| `ocp_get_track` | Get current track info | - |
| `ocp_get_playlist` | Get playlist | - |
| `ocp_clear_playlist` | Clear playlist | - |
| `ocp_get_media_skills` | List media skills | - |
| `ocp_play_featured` | Play featured tracks | `skill_id` (str) |
| `ocp_like_track` | Like current track | - |
| `ocp_dislike_track` | Dislike current track | - |

### Skill Management Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_skills` | List all loaded skills | - |
| `activate_skill` | Activate/load a skill | `skill_id` (str) |
| `deactivate_skill` | Deactivate/unload a skill | `skill_id` (str) |
| `get_active_skills` | Get active conversation skills | - |
| `deactivate_active_skill` | Remove skill from active stack | `skill_id` (str) |
| `install_skill` | Install skill from GitHub | `url` (str) |
| `uninstall_skill` | Uninstall a skill | `skill_id` (str) |
| `get_skill_settings` | Get skill settings/API | `skill_id` (str) |

### System Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `stop_all` | Global stop command | - |
| `check_system_ready` | Check if OVOS is ready | - |
| `get_listener_state` | Get voice listener state | - |
| `set_listener_state` | Set listener state/mode | `state` (str), `mode` (str, optional) |
| `sleep_listener` | Put listener to sleep | - |
| `wake_listener` | Wake up listener | - |
| `get_stt_languages` | Get supported STT languages | - |
| `get_tts_languages` | Get supported TTS languages | - |
| `get_gui_status` | Check GUI connection | - |
| `show_gui_page` | Display a GUI page | `page` (str), `namespace` (str), `data` (dict, optional) |
| `clear_gui_namespace` | Clear GUI pages | `namespace` (str) |
| `set_gui_value` | Set GUI data value | `namespace` (str), `key` (str), `value` (any) |
| `show_homescreen` | Show active homescreen | - |
| `list_homescreens` | List available homescreens | - |
| `set_active_homescreen` | Set active homescreen | `homescreen_id` (str) |

## Usage Examples

### With FastMCP Client

```python
import asyncio
from fastmcp import Client

async def main():
    client = Client("http://localhost:8000/mcp")
    
    async with client:
        # Make OVOS speak
        result = await client.call_tool("speak", {"text": "Hello, world!"})
        print(result)
        
        # Set volume to 50%
        result = await client.call_tool("set_volume", {"percent": 0.5})
        print(result)
        
        # Search and play music
        result = await client.call_tool("ocp_search", {"query": "jazz music"})
        print(result)

asyncio.run(main())
```

### With LangChain

```python
from langchain_mcp import MCPToolkit

# Create toolkit from MCP server
toolkit = MCPToolkit(server_url="http://localhost:8000/mcp")
tools = toolkit.get_tools()

# Use tools with your LLM agent
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/OpenVoiceOS/ovos-skill-mcp.git
cd ovos-skill-mcp
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Linting
ruff check .

# Type checking
mypy ovos_skill_mcp
```

## Requirements

- Python 3.10+
- Running OVOS instance with message bus accessible
- FastMCP 2.0+
- ovos-bus-client 0.1+

## License

Apache License 2.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Related Projects

- [OpenVoiceOS](https://github.com/OpenVoiceOS) - The open voice operating system
- [FastMCP](https://github.com/jlowin/fastmcp) - Fast Model Context Protocol framework
- [ovos-bus-client](https://github.com/OpenVoiceOS/ovos-bus-client) - OVOS message bus client
