from typing import Dict, Any
import uuid
import websockets
import asyncio
import json
import yaml
import os
from src.models.server_state import ServerState
from src.gpt.conversation import GPTAPIConversation
from src.utils.message_utils import send_game_message, send_data
from src.models.game_info import GameInformation
from src.utils.logger import Logger
from src.server.game_functions import GameFunctions
from src.server.event_handler import EventHandler
from src.services.game_info_service import GameInfoService

class MinecraftGPTServer:
    def __init__(self, host: str, port: int, config: Dict[str, Any]):
        self.host = host
        self.port = port
        self.config = config
        self.server_state = ServerState()
        self.game_functions = GameFunctions()
        self.event_handler = EventHandler(self.server_state, self.config)
        self.game_info_service = GameInfoService()
        
        # 添加函数映射到配置中
        self.config['functions_map'].update({
            'gpt_game_weather': self.game_functions.gpt_game_weather,
            'gpt_game_players': self.game_functions.gpt_game_players,
            'gpt_get_time': self.game_functions.gpt_get_time,
            'gpt_run_command': self.game_functions.gpt_run_command,
            'gpt_world_entity': self.game_functions.gpt_world_entity,
            'gpt_player_inventory': self.game_functions.gpt_player_inventory,
            'gpt_get_commandlog': self.game_functions.gpt_get_commandlog
        })
        
    async def start(self):
        """启动WebSocket服务器"""
        try:
            # 初始化 periodic_task 为 None
            periodic_task = None

            update_info = self.config['server']['update_info']
            # 创建定期更新任务
            if update_info:
                periodic_task = asyncio.create_task(self.periodic_update())
            
            server = await websockets.serve(
                self.handle_connection,
                self.host,
                self.port,
                ping_interval=20,
                ping_timeout=20,
                close_timeout=10
            )
            Logger.info(f"WebSocket服务器已启动，正在监听 {self.host}:{self.port}")
            Logger.info(f"信息定期更新状态:{update_info}")
            
            # 根据 periodic_task 是否存在来决定要等待的任务
            if periodic_task:
                await asyncio.gather(
                    server.wait_closed(),
                    periodic_task
                )
            else:
                await server.wait_closed()

        except Exception as e:
            Logger.error(f"启动服务器时发生错误: {str(e)}")
            raise

            
    async def handle_connection(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """处理新的WebSocket连接"""
        connection_uuid = str(uuid.uuid4())
        websocket.uuid = connection_uuid
        websocket.server_state = self.server_state
        Logger.info(f"客户端 {connection_uuid} 已连接")
        
        try:
            # 确保GPT配置存在
            gpt_config = self.config.get('gpt', {})
            missing_keys = [key for key in ['api_url', 'model', 'system_prompt'] if key not in gpt_config]
            
            if missing_keys:
                raise ValueError(f"GPT配置缺少以下键: {', '.join(missing_keys)}")
            
            Logger.debug(f"GPT配置: {gpt_config}")
            
            async with GPTAPIConversation(
                api_key=os.getenv("API_KEY"),
                api_url=gpt_config['api_url'],
                model=gpt_config['model'],
                functions=self.config.get('functions', []),
                functions_map=self.config.get('functions_map', {}),
                websocket=websocket,
                system_prompt=gpt_config['system_prompt']
            ) as conversation:
                await self.initialize_connection(websocket, connection_uuid)
                await self.message_loop(websocket, conversation)
                
        except websockets.exceptions.ConnectionClosed as e:
            Logger.info(f"客户端 {connection_uuid} 连接已断开: {e.reason}")
        except Exception as e:
            Logger.error(f"处理连接时发生错误: {str(e)}")
            import traceback
            Logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        finally:
            await self.cleanup_connection(connection_uuid)
            Logger.info(f"客户端 {connection_uuid} 资源清理完成")
                
    async def initialize_connection(self, websocket: websockets.WebSocketServerProtocol, connection_uuid: str):
        """初始化新的连接"""
        self.server_state.information[connection_uuid] = GameInformation()
        self.server_state.connections[connection_uuid] = websocket
        
        await self.subscribe_events(websocket)
        await send_data(websocket, {"Result": "true"})
        
        welcome_message = self.config['welcome_message_template'].format(
            ip=self.host,
            port=self.port,
            model=self.config['gpt']['model'],
            uuid=connection_uuid
        )
        await send_game_message(websocket, welcome_message)
        
    async def subscribe_events(self, websocket):
        """订阅事件"""
        for event_name in self.config['event_lists']:
            message = {
                "body": {"eventName": event_name},
                "header": {
                    "requestId": str(uuid.uuid4()),
                    "messagePurpose": "subscribe",
                    "version": 1,
                    "messageType": "commandRequest"
                }
            }
            await send_data(websocket, message)
            
    async def cleanup_connection(self, connection_uuid: str):
        """清理断开的连接"""
        try:
            websocket = self.server_state.connections.pop(connection_uuid, None)
            if websocket:
                await websocket.close()
                
            self.server_state.information.pop(connection_uuid, None)
            self.server_state.received_parts.pop(connection_uuid, None)
                
        except Exception as e:
            Logger.error(f"清理连接 {connection_uuid} 时发生错误: {str(e)}")
            
    async def periodic_update(self):
        """定期更新游戏信息"""
        while True:
            for connection_uuid, websocket in list(self.server_state.connections.items()):
                await self.game_info_service.update_game_info(websocket, connection_uuid)
            await asyncio.sleep(10)

    async def message_loop(self, websocket, conversation):
        """处理消息循环"""
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data.get('header', {}).get('eventName') != 'PlayerTransform':
                        Logger.debug(f"收到消息: {data}")
                    await self.handle_event(websocket, data, conversation)
                except json.JSONDecodeError as e:
                    Logger.error(f"JSON解析错误: {str(e)}")
                except Exception as e:
                    Logger.error(f"处理消息时出错: {str(e)}")
                
        except websockets.exceptions.ConnectionClosedOK:
            Logger.info(f"客户端 {websocket.uuid} 正常断开连接")
        except websockets.exceptions.ConnectionClosedError as e:
            Logger.warning(f"客户端 {websocket.uuid} 连接异常断开: {str(e)}")
        except websockets.exceptions.WebSocketException as e:
            Logger.error(f"WebSocket错误: {str(e)}")
        except Exception as e:
            Logger.error(f"消息循环中发生错误: {str(e)}")
            import traceback
            Logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")

    async def handle_event(self, websocket, data: Dict[str, Any], conversation):
        """处理事件"""
        header = data.get('header', {})
        message_purpose = header.get('messagePurpose')
        
        if message_purpose == "commandResponse":
            await self.event_handler.handle_command_response(websocket, data)
        elif message_purpose == "event":
            await self.event_handler.handle_event_message(websocket, data, conversation)

    async def handle_event_message(self, websocket, data):
        body = data.get('body', {})
        header = data.get('header', {})
        event_name = header.get('eventName', '')

        if event_name == "PlayerTransform":
            await self.game_info_service.update_player_transform(
                websocket.uuid,
                body.get('player', {})
            )
        elif event_name == "PlayerMessage":
            await self.handle_player_message(websocket, data)