import asyncio
import json
import uuid
from typing import Dict
from ..utils.logger import Logger
from ..models.game_info import GameInformation, PlayerTransformInfo
from ..utils.message_utils import run_command, send_script_data

class GameInfoService:
    def __init__(self):
        self.game_info: Dict[str, GameInformation] = {}
        
    async def update_game_info(self, websocket, connection_uuid):
        """定期更新游戏信息"""
        try:
            info = websocket.server_state.information[connection_uuid]
            
            # 清理旧数据
            self._clear_temporary_info(info)
            
            # 运行基础信息命令
            await self._run_info_commands(websocket)
            
            # 查询实体信息
            if info.need_entityid:
                await send_script_data(
                    websocket,
                    f"check_entity {info.need_entityid}",
                    "server:script"
                )
                await asyncio.sleep(0.2)
            
            # 查询玩家信息
            await send_script_data(websocket, "player_info", "server:script")
            
            Logger.log_game_info(f"已更新游戏信息到 {connection_uuid}")
            
        except Exception as e:
            Logger.log_game_info(f"更新游戏信息时发生错误: {str(e)}")

    def _clear_temporary_info(self, info):
        """清理临时信息"""
        info.game_weather = ''
        info.game_time = ''
        info.game_day = ''
        info.players = ''
        # 保留玩家位置和背包等持久性数据

    async def _run_info_commands(self, websocket):
        """运行信息查询命令"""
        commands = [
            "weather query",
            "list",
            "time query day",
            "time query gametime"
        ]
        for cmd in commands:
            await run_command(websocket, cmd)
            await asyncio.sleep(0.5)  # 使用更短的延迟

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