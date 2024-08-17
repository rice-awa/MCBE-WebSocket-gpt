import asyncio
import json
import os
import re
import auth
import uuid
import websockets
from dataclasses import dataclass, field
from typing import Dict, Any
from collections import defaultdict
from gptapi import GPTAPIConversation
from functions import functions

@dataclass
class PlayertransformInfo:
    name: str
    id: str
    color: str
    type: str
    variant: str
    yRot: float
    dimension: str
    position: Dict[str, float]

@dataclass
class GameInformation:
    game_weather: str = ''
    game_time: str = ''
    game_day: str = ''
    players: str = ''
    player_inventory: Dict[str, Any] = field(default_factory=dict) # 玩家背包信息
    need_entityid: str = ''
    entity_info: str = ''
    player_self_info: Dict[str, Any] = field(default_factory=dict) # 玩家自身信息
    player_transform_messages: Dict[str, PlayertransformInfo] = field(default_factory=dict)
    commandResponse_log: Dict[str, str] = field(default_factory=dict)

@dataclass
class ServerState:
    connections: Dict[str, websockets.WebSocketServerProtocol] = field(default_factory=dict)
    information: Dict[str, GameInformation] = field(default_factory=dict)
    received_parts: Dict[str, Dict[str, Dict[int, str]]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(dict)))
    complete_data: str = ''
    pending_commands: Dict[str, str] = field(default_factory=dict)  # 新增字段，用于存储待响应的命令

server_state = ServerState()

api_url = os.getenv("API_URL")
api_key = os.getenv("API_KEY")

if not api_url:
    raise ValueError("API_URL 环境变量未设置")
if not api_key:
    raise ValueError("API_KEY 环境变量未设置")

model = "gpt-4o"
system_prompt = "你是一个MCBE的AI助手，根据游戏内玩家的要求和游戏知识回答，你需要遵守以下几点：#1.交流中称玩家为“冒险家”#2.任何回答时都必须把玩家“工具人”忽略（除非特殊需要）#3.当玩家的问题可能需要执行命令获取时，直接调用函数获取而不是叫玩家执行。#4.请始终保持积极和专业的态度。#5.回答尽量保持一段话不要太长。"

ip = "0.0.0.0"
port = "8080"

welcome_message_template = """-----------
成功连接WebSocket服务器
服务器ip:{ip}
端口:{port}
GPT上下文:function-call不支持关闭上下文，请使用GPT保存
GPT模型:{model}
连接UUID:{uuid}
-----------
"""

COMMANDS = ["#登录", "GPT 聊天", "GPT 保存", "运行命令", "GPT 脚本", "测试天气", "脚本命令", "命令日志"]
EVENT_LISTS = ["PlayerMessage", "PlayerTransform"]

async def get_game_information(websocket, connection_uuid):
    await run_command(websocket, "weather query")
    await run_command(websocket, "list")
    await asyncio.sleep(0.5)
    await run_command(websocket, "time query day")
    await run_command(websocket, "time query gametime")
    await asyncio.sleep(0.5)
    entityid = server_state.information[connection_uuid].need_entityid
    await send_script_data(websocket, f"check_entity {entityid}", "server:script")
    await asyncio.sleep(0.5)
    await send_script_data(websocket, f"player_info", "server:script")
    print(f"已发送信息查询命令给 {connection_uuid}")

async def clear_old_data(websocket, connection_uuid):
    """定期清理 GameInformation 对象中的临时数据"""
    if connection_uuid in server_state.information:
        info = server_state.information[connection_uuid]
        # info.commandResponse_log.clear()
        # 清理天气、时间等临时信息
        info.game_weather = ''
        info.game_time = ''
        info.game_day = ''
        info.players = ''

async def periodic_update():
    while True:
        for connection_uuid, websocket in server_state.connections.items():
            await clear_old_data(websocket, connection_uuid)
            await get_game_information(websocket, connection_uuid)
        await asyncio.sleep(10)
        
async def gpt_get_commandlog(websocket):
    connection_uuid = websocket.uuid
    commandResponse_log = server_state.information[connection_uuid].commandResponse_log
    return json.dumps(commandResponse_log)

async def gpt_player_inventory(websocket, player_name=None):
    connection_uuid = websocket.uuid
    try:
        if not player_name:
            inventory = server_state.information[connection_uuid].player_inventory
        else:
            inventory = server_state.information[connection_uuid].player_inventory.get(player_name, {})
        print(f"收到玩家背包信息: {inventory}")
        return json.dumps(inventory)
    except Exception as e:
        print(f"获取玩家背包时出错: {e}")
        return json.dumps({"error": "无法获取背包信息"})

async def gpt_world_entity(websocket, entityid):
    connection_uuid = websocket.uuid
    entity_info = server_state.information[connection_uuid].entity_info
    server_state.information[connection_uuid].need_entityid = entityid
    if entity_info == '':
        entity_info = {"status": "正在查询实体信息，再次询问可获取"}
    return json.dumps(entity_info)

async def gpt_run_command(websocket, commands):
    if not commands:
        print("没有命令可执行")
        return "至少需要一个命令"
    
    for command in commands:
        print(f"已发送命令: {command}")
        await run_command(websocket, command)
    
    return f"已发送 {len(commands)} 个命令，命令稍后执行"

async def gpt_get_time(websocket, dimension):
    connection_uuid = websocket.uuid
    gametime = server_state.information[connection_uuid].game_time
    gameday = server_state.information[connection_uuid].game_day

    json_data = {
        "dimension": dimension,
        "time": gametime,
        "day": gameday,
    }
    return json.dumps(json_data)

async def gpt_game_weather(websocket, dimension):
    connection_uuid = websocket.uuid
    weather = server_state.information[connection_uuid].game_weather
    print(f"收到天气信息: {weather}")
    
    json_data = {
        "dimension": dimension,
        "weather": weather,
    }
    return json.dumps(json_data)

async def gpt_game_players(websocket):
    connection_uuid = websocket.uuid
    players = server_state.information[connection_uuid].players
    player_self_info = server_state.information[connection_uuid].player_self_info
    player_transform_messages = server_state.information[connection_uuid].player_transform_messages
    all_players_info = [{"all_players": players}]

    if not player_transform_messages:
        return json.dumps({"error": "No player transform messages found."})
    
    for player_name, player_info in player_transform_messages.items():
        if player_info:
            json_data = {
                "player_name": player_info.name,
                "player_health" : player_self_info[player_name]["health"],
                "player_tag": player_self_info[player_name]["tags"],
                "player_yRot": player_info.yRot,
                "player_dimension": player_info.dimension,
                "position": player_info.position,
            }
            all_players_info.append(json_data)
    
    return json.dumps(all_players_info)

# 函数映射
functions_map = {
    "gpt_game_weather": gpt_game_weather,
    "gpt_game_players": gpt_game_players,
    "gpt_get_time": gpt_get_time,
    "gpt_run_command": gpt_run_command,
    "gpt_world_entity": gpt_world_entity,
    "gpt_player_inventory": gpt_player_inventory,
    "gpt_get_commandlog": gpt_get_commandlog
}

async def gpt_main(conversation, player_prompt):
    gpt_message = await conversation.call_gpt(player_prompt)

    if gpt_message is None:
        gpt_message = '错误: GPT回复为None，模型可能不支持function-call'

    print(f"gpt消息: {gpt_message}")

    return gpt_message

async def send_data(websocket, message):
    await websocket.send(json.dumps(message))

async def subscribe_events(websocket):
    for event_name in EVENT_LISTS:
        message = {
            "body": {
                "eventName": event_name
            },
            "header": {
                "requestId": str(uuid.uuid4()),
                "messagePurpose": "subscribe",
                "version": 1,
                "EventName": "commandRequest"
            }
        }
        await send_data(websocket, message)

async def send_game_message(websocket, message):
    say_message = message.replace('"', '\\"').replace(':', '：').replace('%', '\\%') # .replace('[', '\\[').replace(']', '\\]').replace('{', '\\{').replace('}', '\\}')
    say_message = "§a" + say_message
    complete_message = json.dumps(say_message, ensure_ascii=False)
    print(complete_message)
    game_message = {
        "body": {
            "origin": {
                "type": "say"
            },
            "commandLine": f'tellraw @a {{"rawtext":[{{"text":{complete_message}}}]}}',
            "version": 1
        },
        "header": {
            "requestId": str(uuid.uuid4()),
            "messagePurpose": "commandRequest",
            "version": 1,
            "EventName": "commandRequest"
        }
    }
    await send_data(websocket, game_message)

async def run_command(websocket, command):
    print(f"命令{command}开始发送")
    requestid = str(uuid.uuid4())
    message = {
        "body": {
            "origin": {
                "type": "player"
            },
            "commandLine": command,
            "version": 17039360
        },
        "header": {
            "requestId": requestid,
            "messagePurpose": "commandRequest",
            "version": 1,
            "EventName": "commandRequest"
        }
    }
    await send_data(websocket, message)
    
    # 记录待响应的命令
    connection_uuid = websocket.uuid
    server_state.pending_commands[requestid] = command
    
    return requestid

async def send_script_data(websocket, content, messageid="server:data"):
    message = {
        "body": {
            "origin": {
                "type": "player"
            },
            "commandLine": f"scriptevent {messageid} {content}",
            "version": 17039360
        },
        "header": {
            "requestId": str(uuid.uuid4()),
            "messagePurpose": "commandRequest",
            "version": 1,
            "EventName": "commandRequest"
        }
    }
    await send_data(websocket, message)

async def handle_event_message(websocket, data):
    body = data.get('body', {})
    header = data.get('header', {})
    event_name = header.get('eventName', '')

    if event_name == "PlayerTransform":
        player = body.get('player', {})
        player_name = player.get('name', 'Unknown')
        player_pos = player.get('position', {})
        dimension_id = player.get('dimension', 'Unknown')
        player_id = player.get('id', 'Unknown')
        player_color = player.get('color', 'Unknown')
        player_type = player.get('type', 'Unknown')
        player_variant = player.get('variant', 'Unknown')
        player_yRot = player.get('yRot', 'Unknown')

        dimension_map = {
            0: 'overworld',
            1: 'nether',
            2: 'the_end'
        }
        dimension = dimension_map.get(dimension_id, 'Unknown')

        x = player_pos.get('x', 'Unknown')
        y = player_pos.get('y', 'Unknown')
        z = player_pos.get('z', 'Unknown')

        player_info = PlayertransformInfo(
            name=player_name,
            id=player_id,
            color=player_color,
            type=player_type,
            variant=player_variant,
            yRot=player_yRot,
            dimension=dimension,
            position={"x": x, "y": y, "z": z}
        )

        connection_uuid = websocket.uuid
        if connection_uuid not in server_state.information:
            server_state.information[connection_uuid] = GameInformation()
        
        if player_name != "工具人":
            server_state.information[connection_uuid].player_transform_messages[player_name] = player_info

        #print(f"存储在字典的信息： {server_state.information[connection_uuid]}")

async def handle_command_response(websocket, data):
    """处理命令响应"""
    body = data.get('body', {})
    header = data.get('header', {})
    requestid = header.get('requestId', '')
    
    if 'statusMessage' in body:
        message = body['statusMessage']
        print(f"命令响应: {message}")
        
        connection_uuid = websocket.uuid
        
        
        
        message_part = message.split('：', 1)
        message_part_space = message.split(' ', 1)

        if message_part[0] == '天气状态是':
            weather = message_part[1].strip()
            server_state.information[connection_uuid].game_weather = weather
            print(f"当前天气: {weather}")
        elif message_part[0][9:13] == '玩家在线':
            players = message_part[1].strip()
            server_state.information[connection_uuid].players = players
        elif message_part_space[0] == '游戏时间为':
            gametime = message_part_space[1].strip()
            server_state.information[connection_uuid].game_time = gametime
        elif message_part_space[0] == '日期为':
            gameday = message_part_space[1].strip()
            server_state.information[connection_uuid].game_day = gameday
        elif message_part_space[0] == 'Script':
            pass
        else:
            # 记录其他类型的命令
            if requestid in server_state.pending_commands:
                command = server_state.pending_commands.pop(requestid)
                server_state.information[connection_uuid].commandResponse_log[command] = message
                print(f"命令 '{command}' 的响应已记录")

async def handle_player_message(websocket, data, conversation):
    sender = data['body']['sender']
    message = data['body']['message']

    if sender and message:
        print(f"玩家 {sender} 说: {message}")

        command, content = parse_message(message)

        connection_uuid = websocket.uuid
        if command == "#登录":
            if auth.verify_password(content):
                if auth.is_token_valid(connection_uuid):
                    await send_game_message(websocket, "你已经登录过啦！")
                    print("已有有效的令牌，拒绝重新生成")
                else:
                    token = auth.generate_token()
                    auth.save_token(connection_uuid, token)
                    await send_game_message(websocket, "登录成功！")
                    print("密钥验证成功，生成令牌")
                    print(f"令牌: {token}")
            else:
                await send_game_message(websocket, "登录失败，密钥无效!")
                print("密钥无效")
            return

        stored_token = auth.get_stored_token(connection_uuid)
        if stored_token and auth.verify_token(stored_token):
            if command == "GPT 聊天":
                await handle_gpt_chat(websocket, content, conversation)
            elif command == "GPT 脚本":
                await handle_gpt_script(websocket, content, conversation)
            elif command == "GPT 保存":
                await handle_gpt_save(websocket, conversation)
            elif command == "运行命令":
                await handle_run_command(websocket, content)
            elif command == "测试天气":
                await send_game_message(websocket, f"测试结果: {server_state.information[connection_uuid].game_weather}")
            elif command == "脚本命令":
                await handle_script_run_command(websocket, content)
            elif command == "命令日志":
                await handle_display_command_log(websocket)

        if command and not auth.verify_token(stored_token):
            await send_game_message(websocket, "请先登录")

        if sender == "工具人":
            if message.startswith("entity_position:"):
                content = message.split(":", 1)[1].strip()
                server_state.information[connection_uuid].entity_info = content
            elif message.startswith("inventorypart"):
                await handle_data_part(message, connection_uuid, 'inventory')
            elif message.startswith("playerinfopart"):
                await handle_data_part(message, connection_uuid, 'playerinfo')
            
        if sender == "脚本引擎":
            if message.startswith("[脚本引擎]"):
                content = message.split(" ", 1)[1].strip()
            print(f"脚本引擎说: {content}")

def parse_message(message):
    for cmd in COMMANDS:
        if message.startswith(cmd):
            return cmd, message[len(cmd):].strip()
    return "", message

async def handle_display_command_log(websocket):
    """显示命令日志"""
    connection_uuid = websocket.uuid
    log_content = server_state.information[connection_uuid].commandResponse_log
    if not log_content:
        await send_game_message(websocket, "暂无命令日志")
    await send_game_message(websocket, f"{log_content}")

async def handle_data_part(message, connection_uuid, data_type, other_message=None):
    print(f"工具人说: {message}")
    match = re.match(rf'^{data_type}part(\d+)-(\d+):(.*)', message)

    if match:
        part_index = int(match.group(1))
        total_parts = int(match.group(2))
        data_chunk = match.group(3)

        if connection_uuid not in server_state.received_parts:
            server_state.received_parts[connection_uuid] = defaultdict(dict)

        server_state.received_parts[connection_uuid][data_type][part_index] = data_chunk
        print(f"接收到的片段 {part_index}/{total_parts}: {data_chunk}")

        # 检查是否所有部分都已接收
        all_parts_received = len(server_state.received_parts[connection_uuid][data_type]) == total_parts

        if all_parts_received:
            # 组合所有部分
            complete_data = ''.join(server_state.received_parts[connection_uuid][data_type][i] for i in range(1, total_parts + 1))

            try:
                data_dict = json.loads(complete_data)
                print(f"完整的{data_type}数据：", data_dict)
                if data_type == 'inventory':
                    server_state.information[connection_uuid].player_inventory = data_dict
                elif data_type == 'playerinfo':
                    server_state.information[connection_uuid].player_self_info = data_dict
                # 处理其他类型的数据
            except json.JSONDecodeError as error:
                print("解析数据时出错：", error)

            # 清空数据以便下次使用
            server_state.received_parts[connection_uuid][data_type].clear()

async def handle_gpt_chat(websocket, content, conversation):
    prompt = content
    gpt_message = await gpt_main(conversation, prompt)
    
    sentences = re.split(r'(?<=[。])', gpt_message)
    
    for sentence in sentences:
        if sentence.strip():
            await send_game_message(websocket, sentence)
            await send_script_data(websocket, sentence)

async def handle_gpt_script(websocket, content, conversation):
    prompt = content
    gpt_message = await gpt_main(conversation, prompt)
    
    await send_script_data(websocket, gpt_message)
    await asyncio.sleep(0.1)

async def handle_gpt_save(websocket, conversation):
    if not conversation:
        await send_game_message(websocket, "没有对话实例，无法保存！")
        return 
    else:
        conversation.save_conversation()
    await conversation.restart()
    await send_game_message(websocket, "对话重启，数据已保存！")

async def handle_run_command(websocket, content):
    command = content
    await run_command(websocket, command)

async def handle_script_run_command(websocket, content):
    command = content
    await send_script_data(websocket, command, "server:run_command")

async def handle_event(websocket, data, conversation):
    header = data.get('header', {})
    event_name = header.get('eventName')
    message_purpose = header.get('messagePurpose')

    if event_name == "PlayerMessage":
        await handle_player_message(websocket, data, conversation)
    if message_purpose == "commandResponse":
        await handle_command_response(websocket, data)
    if message_purpose == "event":
        await handle_event_message(websocket, data)

async def handle_connection(websocket, path):
    connection_uuid = str(uuid.uuid4())
    websocket.uuid = connection_uuid
    print(f"客户端: {connection_uuid} 已连接")

    conversation = GPTAPIConversation(api_key, api_url, model, functions, functions_map, websocket, system_prompt=system_prompt, enable_logging=True)

    welcome_message = welcome_message_template.format(
        ip=ip, 
        port=port, 
        model=model, 
        uuid=connection_uuid
    )
    await send_game_message(websocket, welcome_message)

    server_state.information[connection_uuid] = GameInformation()
    server_state.connections[connection_uuid] = websocket
    
    try:
        await send_data(websocket, {"Result": "true"})
        await subscribe_events(websocket)

        async for message in websocket:
            data = json.loads(message)
            await handle_event(websocket, data, conversation)
    
    except websockets.exceptions.ConnectionClosed:
        print(f"客户端 {connection_uuid} 连接已断开")
    
    except Exception as e:
        print(f"发生错误: {e}")
    
    finally:
        print(f"客户端 {connection_uuid} 已断开连接，正在清理资源")
        await conversation.close()

        del server_state.connections[connection_uuid]
        del server_state.information[connection_uuid]

async def main():
    async with websockets.serve(handle_connection, ip, port):
        print(f"WebSocket服务器已启动，正在监听 {ip}:{port}")
        await asyncio.gather(
            asyncio.Future(),
            periodic_update()
        )

if __name__ == "__main__":
    asyncio.run(main())