from typing import Dict, Any, Optional
import json
import re
from dataclasses import dataclass
from collections import defaultdict
from src.utils.logger import Logger
from src.utils.message_utils import send_game_message, send_script_data, run_command
from src.utils.auth import get_stored_token, verify_token, save_token, generate_token, is_token_valid, verify_password
from src.models.game_info import PlayerTransformInfo, GameInformation
from src.gpt.conversation import GPTAPIConversation
import asyncio

class EventHandler:
    def __init__(self, server_state, config: Dict[str, Any]):
        self.server_state = server_state
        self.config = config
        
        # 验证命令配置
        if 'commands' not in config:
            raise ValueError("配置缺少 'commands' 部分")
        if 'available_commands' not in config:
            raise ValueError("配置缺少 'available_commands' 部分")
        
        # 验证所有命令都在可用命令列表中
        for cmd_value in config['commands'].values():
            if cmd_value not in config['available_commands']:
                raise ValueError(f"命令 '{cmd_value}' 不在可用命令列表中")
        
        self.dimension_map = self.config.get('dimension_map', {
            0: 'overworld',
            1: 'nether',
            2: 'the_end'
        })
        
        # 初始化命令处理器映射
        self.command_handlers = {
            self.config['commands']['login']: self.handle_login,
            self.config['commands']['gpt_chat']: self.handle_gpt_chat,
            self.config['commands']['gpt_script']: self.handle_gpt_script,
            self.config['commands']['gpt_save']: self.handle_gpt_save,
            self.config['commands']['run_command']: self.handle_run_command,
            self.config['commands']['script_command']: self.handle_script_run_command,
            self.config['commands']['command_log']: self.handle_display_command_log,
            self.config['commands']['op_manage']: self.handle_op
        }

    async def handle_command_response(self, websocket, data: Dict[str, Any]):
        """处理命令响应"""
        body = data.get('body', {})
        header = data.get('header', {})
        requestid = header.get('requestId', '')
        
        if 'statusMessage' in body:
            message = body['statusMessage']
            Logger.debug(f"命令响应: {message}")
            
            connection_uuid = websocket.uuid
            message_part = message.split('：', 1)
            message_part_space = message.split(' ', 1)

            if message_part[0] == '天气状态是':
                weather = message_part[1].strip()
                self.server_state.information[connection_uuid].game_weather = weather
                Logger.debug(f"当前天气: {weather}")
            elif message_part[0][9:13] == '玩家在线':
                players = message_part[1].strip()
                self.server_state.information[connection_uuid].players = players
            elif message_part_space[0] == '游戏时间为':
                gametime = message_part_space[1].strip()
                self.server_state.information[connection_uuid].game_time = gametime
            elif message_part_space[0] == '日期为':
                gameday = message_part_space[1].strip()
                self.server_state.information[connection_uuid].game_day = gameday
            elif message_part_space[0] == 'Script':
                pass
            else:
                # 记录其他类型的命令
                if requestid in self.server_state.pending_commands:
                    command = self.server_state.pending_commands.pop(requestid)
                    self.server_state.information[connection_uuid].commandResponse_log[command] = message
                    Logger.debug(f"命令 '{command}' 的响应已记录")

    async def handle_event_message(self, websocket, data: Dict[str, Any], conversation):
        """处理事件消息"""
        body = data.get('body', {})
        header = data.get('header', {})
        event_name = header.get('eventName', '')

        if event_name == "PlayerMessage":
            await self.handle_player_message(websocket, data, conversation)
        elif event_name == "PlayerTransform":
            await self.handle_player_transform(websocket, data)

    async def handle_player_transform(self, websocket, data: Dict[str, Any]):
        """处理玩家位置更新事件"""
        body = data.get('body', {})
        player = body.get('player', {})
        
        player_info = PlayerTransformInfo(
            name=player.get('name', 'Unknown'),
            id=player.get('id', 'Unknown'),
            color=player.get('color', 'Unknown'),
            type=player.get('type', 'Unknown'),
            variant=player.get('variant', 'Unknown'),
            yRot=player.get('yRot', 'Unknown'),
            dimension=self.dimension_map.get(player.get('dimension', 'Unknown'), 'Unknown'),
            position={
                "x": player.get('position', {}).get('x', 'Unknown'),
                "y": player.get('position', {}).get('y', 'Unknown'),
                "z": player.get('position', {}).get('z', 'Unknown')
            }
        )

        connection_uuid = websocket.uuid
        if connection_uuid not in self.server_state.information:
            self.server_state.information[connection_uuid] = GameInformation()
        
        if player_info.name != "工具人":
            self.server_state.information[connection_uuid].player_transform_messages[player_info.name] = player_info

    async def handle_player_message(self, websocket, data: Dict[str, Any], conversation):
        """处理玩家消息"""
        body = data.get('body', {})
        sender = body.get('sender', '')
        message = body.get('message', '')
        connection_uuid = websocket.uuid

        if not sender or not message:
            return

        Logger.debug(f"玩家 {sender} 说: {message}")

        # 检查是否是工具人或脚本引擎的消息
        if sender == self.config['special_players']['tool']:
            await self.handle_tool_message(websocket, message, connection_uuid)
            return
        elif sender == self.config['special_players']['script_engine']:
            await self.handle_script_message(websocket, message)
            return

        # 解析命令和内容
        command, content = self.parse_message(message)
        if not command:  # 如果不是命令，直接返回
            return

        # 处理登录命令
        if command == self.config['commands']['login']:
            await self.handle_login(websocket, content, connection_uuid, sender)
            return

        # 验证权限
        stored_token = get_stored_token(connection_uuid)
        op_list = self.server_state.information[connection_uuid].op_list

        if stored_token and verify_token(stored_token) and sender in op_list:
            handler = self.command_handlers.get(command)
            if handler:
                await handler(websocket, content, conversation)
        elif command and not verify_token(stored_token):
            await send_game_message(websocket, self.config['messages']['login_required'])

    def parse_message(self, message: str) -> tuple[str, str]:
        """解析消息"""
        # 先检查完整的命令匹配
        for cmd_value in self.config['commands'].values():
            if message.startswith(cmd_value):
                content = message[len(cmd_value):].strip()
                return cmd_value, content
                
        # 如果没有匹配到命令，返回空
        return "", message

    async def handle_tool_message(self, websocket, message: str, connection_uuid: str):
        """处理工具人消息"""
        for data_type in self.config['data_types']:
            if message.startswith(f"{data_type}part"):
                await self.handle_data_part(message, connection_uuid, data_type)
                break

    async def handle_script_message(self, websocket, message: str):
        """处理脚本引擎消息"""
        script_prefix = self.config['messages']['script_prefix']
        if message.startswith(script_prefix):
            content = message[len(script_prefix):].strip()
            Logger.debug(f"脚本引擎说: {content}")

    async def handle_login(self, websocket, content: str, connection_uuid: str, sender: str):
        """处理登录命令"""
        if verify_password(content):
            if is_token_valid(connection_uuid):
                await send_game_message(websocket, self.config['messages']['already_logged_in'])
                Logger.debug(self.config['log_messages']['token_exists'])
            else:
                token = generate_token()
                save_token(connection_uuid, token)
                await send_game_message(websocket, self.config['messages']['login_success'])
                Logger.debug(self.config['log_messages']['token_generated'].format(token=token))

            # 存储OP列表
            op_list = self.server_state.information[connection_uuid].op_list
            if sender not in op_list:
                op_list.append(sender)
        else:
            await send_game_message(websocket, self.config['messages']['login_failed'])
            Logger.debug(self.config['log_messages']['invalid_key'])

    async def handle_data_part(self, message: str, connection_uuid: str, data_type: str):
        """处理数据片段"""
        Logger.debug(f"工具人说: {message}")
        match = re.match(rf'^{data_type}part(\d+)-(\d+):(.*)', message)

        if match:
            part_index = int(match.group(1))
            total_parts = int(match.group(2))
            data_chunk = match.group(3)

            if connection_uuid not in self.server_state.received_parts:
                self.server_state.received_parts[connection_uuid] = defaultdict(dict)

            self.server_state.received_parts[connection_uuid][data_type][part_index] = data_chunk
            Logger.debug(f"接收到的片段 {part_index}/{total_parts}: {data_chunk}")

            if len(self.server_state.received_parts[connection_uuid][data_type]) == total_parts:
                await self.process_complete_data(connection_uuid, data_type, total_parts)

    async def process_complete_data(self, connection_uuid: str, data_type: str, total_parts: int):
        """处理完整的数据"""
        complete_data = ''.join(
            self.server_state.received_parts[connection_uuid][data_type][i] 
            for i in range(1, total_parts + 1)
        )

        try:
            data_dict = json.loads(complete_data)
            Logger.debug(f"完整的{data_type}数据：{data_dict}")
            
            info = self.server_state.information[connection_uuid]
            if data_type == 'inventory':
                info.player_inventory = data_dict
            elif data_type == 'playerinfo':
                info.player_self_info = data_dict
            elif data_type == 'entity_position':
                info.entity_info = data_dict
                
        except json.JSONDecodeError as error:
            Logger.error(f"解析数据时出错：{error}")

        # 清空数据以便下次使用
        self.server_state.received_parts[connection_uuid][data_type].clear()

    async def handle_gpt_chat(self, websocket, content: str, conversation):
        """处理GPT聊天命令"""
        Logger.debug(f"GPT聊天: {content}")
        try:
            gpt_message = await conversation.call_gpt(content)
            sentences = re.split(r'(?<=[。])', gpt_message)
            
            for sentence in sentences:
                if sentence.strip():
                    await send_game_message(websocket, sentence)
                    await send_script_data(websocket, sentence, "server:script")
        except Exception as e:
            Logger.error(f"GPT聊天处理出错: {str(e)}")
            await send_game_message(websocket, self.config['messages']['gpt_error'])

    async def handle_gpt_script(self, websocket, content: str, conversation):
        """处理GPT脚本命令"""
        Logger.debug(f"GPT脚本: {content}")
        try:
            gpt_message = await conversation.call_gpt(content)
            await send_script_data(websocket, gpt_message, "server:script")
            await asyncio.sleep(0.1)
        except Exception as e:
            Logger.error(f"GPT脚本处理出错: {str(e)}")
            await send_game_message(websocket, self.config['messages']['gpt_error'])

    async def handle_gpt_save(self, websocket, content: str, conversation):
        """处理GPT保存命令"""
        Logger.debug("保存GPT对话")
        if not conversation:
            await send_game_message(websocket, self.config['messages']['no_conversation'])
            return
        
        try:
            conversation.save_conversation()
            await conversation.restart()
            await send_game_message(websocket, self.config['messages']['save_success'])
        except Exception as e:
            Logger.error(f"保存对话出错: {str(e)}")
            await send_game_message(websocket, self.config['messages']['save_error'])

    async def handle_run_command(self, websocket, content: str, conversation=None):
        """处理运行命令"""
        Logger.debug(f"执行命令: {content}")
        try:
            await run_command(websocket, content)
        except Exception as e:
            Logger.error(f"执行命令出错: {str(e)}")
            await send_game_message(websocket, self.config['messages']['command_error'])

    async def handle_script_run_command(self, websocket, content: str, conversation=None):
        """处理脚本命令"""
        Logger.debug(f"执行脚本命令: {content}")
        try:
            await send_script_data(websocket, content, "server:run_command")
        except Exception as e:
            Logger.error(f"执行脚本命令出错: {str(e)}")
            await send_game_message(websocket, self.config['messages']['script_error'])

    async def handle_display_command_log(self, websocket, content: str, conversation=None):
        """显示命令日志"""
        Logger.debug("显示命令日志")
        connection_uuid = websocket.uuid
        log_content = self.server_state.information[connection_uuid].commandResponse_log
        
        if not log_content:
            await send_game_message(websocket, self.config['messages']['no_command_log'])
        else:
            await send_game_message(websocket, str(log_content))

    async def handle_op(self, websocket, content: str, conversation=None):
        """处理权限管理命令"""
        Logger.debug(f"处理权限管理: {content}")
        connection_uuid = websocket.uuid
        op_list = self.server_state.information[connection_uuid].op_list
        
        parts = content.split(maxsplit=1)
        if len(parts) < 1:
            await send_game_message(websocket, self.config['messages']['op_usage'])
            return

        action = parts[0]
        
        if action == "查看":
            op_list_str = ", ".join(op_list) if op_list else "空"
            await send_game_message(websocket, f"当前wsOP列表: {op_list_str}")
        elif action == "添加" and len(parts) == 2:
            player_name = parts[1].strip()
            if player_name not in op_list:
                op_list.append(player_name)
                await send_game_message(websocket, self.config['messages']['op_add_success'].format(player=player_name))
            else:
                await send_game_message(websocket, self.config['messages']['op_already_exists'].format(player=player_name))
        elif action == "删除" and len(parts) == 2:
            player_name = parts[1].strip()
            if player_name in op_list:
                op_list.remove(player_name)
                await send_game_message(websocket, self.config['messages']['op_remove_success'].format(player=player_name))
            else:
                await send_game_message(websocket, self.config['messages']['op_not_exists'].format(player=player_name))
        else:
            await send_game_message(websocket, self.config['messages']['op_usage']) 