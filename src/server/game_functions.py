from typing import Dict, Any, List
import json
import asyncio
from src.utils.logger import Logger
from src.utils.message_utils import send_data, send_script_data, run_command
import uuid

class GameFunctions:
    @staticmethod
    async def gpt_game_weather(websocket, dimension: str) -> str:
        """获取指定维度的天气信息"""
        Logger.debug(f"查询天气信息: {dimension}")
        
        # 生成一个唯一的请求ID
        request_id = str(uuid.uuid4())
        # 记录这个命令到pending_commands
        websocket.server_state.pending_commands[request_id] = "weather query"
        
        await run_command(websocket, "weather query", request_id)
        # 等待命令响应更新天气信息
        await asyncio.sleep(1)
        
        weather = websocket.server_state.information[websocket.uuid].game_weather
        if not weather:
            weather = "未知"
            
        return json.dumps({
            "dimension": dimension,
            "weather": weather
        })

    @staticmethod
    async def gpt_game_players(websocket) -> str:
        """获取所有玩家信息"""
        Logger.debug("查询玩家信息")
        connection_uuid = websocket.uuid
        state = websocket.server_state.information[connection_uuid]
        
        players = state.players
        player_self_info = state.player_self_info
        player_transform_messages = state.player_transform_messages
        
        all_players_info = [{"all_players": players}]
        
        for player_name, player_info in player_transform_messages.items():
            player_data = {
                "player_name": player_info.name,
                "player_health": player_self_info.get(player_name, {}).get("health", ""),
                "player_tags": player_self_info.get(player_name, {}).get("tags", []),
                "player_yRot": player_info.yRot,
                "player_dimension": player_info.dimension,
                "position": player_info.position
            }
            all_players_info.append(player_data)
            
        return json.dumps(all_players_info)

    @staticmethod
    async def gpt_get_time(websocket, dimension: str) -> str:
        """获取游戏时间信息"""
        Logger.debug(f"查询时间信息: {dimension}")
        connection_uuid = websocket.uuid
        state = websocket.server_state.information[connection_uuid]
        
        await run_command(websocket, "time query day")
        await run_command(websocket, "time query gametime")
        await asyncio.sleep(1)
        
        return json.dumps({
            "dimension": dimension,
            "time": state.game_time,
            "day": state.game_day
        })

    @staticmethod
    async def gpt_run_command(websocket, commands: List[str]) -> str:
        """执行游戏命令"""
        Logger.debug(f"执行命令: {commands}")
        if not commands:
            return "至少需要一个命令"
            
        for command in commands:
            await run_command(websocket, command)
            
        return f"已发送 {len(commands)} 个命令，命令稍后执行"

    @staticmethod
    async def gpt_world_entity(websocket, entityid: str) -> str:
        """获取实体信息"""
        Logger.debug(f"查询实体信息: {entityid}")
        connection_uuid = websocket.uuid
        state = websocket.server_state.information[connection_uuid]
        
        state.need_entityid = entityid
        await send_script_data(websocket, f"check_entity {entityid}", "server:script")
        await asyncio.sleep(1)
        
        entity_info = state.entity_info
        if not entity_info:
            return json.dumps({"status": "正在查询实体信息，再次询问可获取"})
        return json.dumps(entity_info)

    @staticmethod
    async def gpt_player_inventory(websocket, player_name: str = None) -> str:
        """获取玩家背包信息"""
        Logger.debug(f"查询玩家背包: {player_name if player_name else '所有玩家'}")
        connection_uuid = websocket.uuid
        state = websocket.server_state.information[connection_uuid]
        
        try:
            if not player_name:
                inventory = state.player_inventory
            else:
                inventory = state.player_inventory.get(player_name, {})
            return json.dumps(inventory)
        except Exception as e:
            Logger.error(f"获取玩家背包时出错: {e}")
            return json.dumps({"error": "无法获取背包信息"})

    @staticmethod
    async def gpt_get_commandlog(websocket) -> str:
        """获取命令执行日志"""
        Logger.debug("获取命令日志")
        connection_uuid = websocket.uuid
        commandResponse_log = websocket.server_state.information[connection_uuid].commandResponse_log
        return json.dumps(commandResponse_log) 