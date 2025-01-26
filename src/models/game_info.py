from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class PlayerTransformInfo:
    name: str
    id: str
    color: str
    type: str
    variant: str
    yRot: float
    dimension: str
    position: Dict[str, float]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerTransformInfo':
        return cls(
            name=data.get('name', 'Unknown'),
            id=data.get('id', 'Unknown'),
            color=data.get('color', 'Unknown'),
            type=data.get('type', 'Unknown'),
            variant=data.get('variant', 'Unknown'),
            yRot=data.get('yRot', 0.0),
            dimension=data.get('dimension', 'Unknown'),
            position=data.get('position', {})
        )

@dataclass
class GameInformation:
    game_weather: str = ''
    game_time: str = ''
    game_day: str = ''
    players: str = ''
    player_inventory: Dict[str, Any] = field(default_factory=dict)
    need_entityid: str = ''
    entity_info: str = ''
    player_self_info: Dict[str, Any] = field(default_factory=dict)
    player_transform_messages: Dict[str, PlayerTransformInfo] = field(default_factory=dict)
    commandResponse_log: Dict[str, str] = field(default_factory=dict)
    op_list: List[str] = field(default_factory=list)
    
    def clear_temporary_data(self):
        """清理临时数据"""
        self.game_weather = ''
        self.game_time = ''
        self.game_day = ''
        self.players = '' 