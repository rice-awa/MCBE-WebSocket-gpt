from dataclasses import dataclass, field
from typing import Dict, Any
from collections import defaultdict
import websockets
from .game_info import GameInformation

@dataclass
class ServerState:
    """服务器状态数据类"""
    connections: Dict[str, websockets.WebSocketServerProtocol] = field(default_factory=dict)
    information: Dict[str, GameInformation] = field(default_factory=dict)
    received_parts: Dict[str, Dict[str, Dict[int, str]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(dict))
    )
    complete_data: str = ''
    pending_commands: Dict[str, str] = field(default_factory=dict) 