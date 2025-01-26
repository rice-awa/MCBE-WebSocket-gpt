import asyncio
import json
import uuid
from typing import Dict
from ..utils.logger import Logger
from ..models.game_info import GameInformation, PlayerTransformInfo

class GameInfoService:
    def __init__(self):
        self.game_info: Dict[str, GameInformation] = {}
        
    async def update_game_info(self, websocket, connection_uuid):
        """定期更新游戏信息"""
        try:
            await self._run_info_commands(websocket)
            Logger.log_game_info(f"已更新游戏信息到 {connection_uuid}")
        except Exception as e:
            Logger.log_game_info(f"更新游戏信息时发生错误: {str(e)}")

    async def _run_info_commands(self, websocket):
        """运行信息查询命令"""
        commands = [
            "weather query",
            "list",
            "time query day",
            "time query gametime"
        ]
        for cmd in commands:
            await self._run_command(websocket, cmd)
            await asyncio.sleep(0.5)

    async def _run_command(self, websocket, command: str):
        """执行命令并记录"""
        message = {
            "body": {
                "origin": {"type": "player"},
                "commandLine": command,
                "version": 1
            },
            "header": {
                "requestId": str(uuid.uuid4()),
                "messagePurpose": "commandRequest",
                "version": 1,
                "EventName": "commandRequest"
            }
        }
        await websocket.send(json.dumps(message))
        Logger.log_game_info(f"发送命令: {command}")

    def update_player_transform(self, connection_uuid: str, player_info: dict):
        """更新玩家位置信息"""
        if player_info.get('name') != "工具人":  # 忽略工具人
            transform_info = PlayerTransformInfo(
                name=player_info.get('name'),
                id=player_info.get('id'),
                color=player_info.get('color'),
                type=player_info.get('type'),
                variant=player_info.get('variant'),
                yRot=player_info.get('yRot'),
                dimension=player_info.get('dimension'),
                position=player_info.get('position', {})
            )
            
            self.game_info[connection_uuid].player_transform_messages[
                player_info['name']
            ] = transform_info
            
            Logger.log_player_move(
                f"Player {player_info['name']} moved to "
                f"x:{transform_info.position.get('x')} "
                f"y:{transform_info.position.get('y')} "
                f"z:{transform_info.position.get('z')}"
            ) 