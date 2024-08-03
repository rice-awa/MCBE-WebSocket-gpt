import asyncio
import json
import os
import re
import auth
import uuid
import websockets
from gptapi import GPTAPIConversation
from functions import functions

api_url = os.getenv("API_URL")  # API地址
api_key = os.getenv("API_KEY")  # API密钥

if not api_url:
    raise ValueError("API_URL 环境变量未设置")
if not api_key:
    raise ValueError("API_KEY 环境变量未设置")

model = "gpt-4o"  # gpt模型
system_prompt = "你是一个MCBE的AI助手，根据游戏内玩家的要求和游戏知识回答，请始终保持积极和专业的态度。回答尽量保持一段话不要太长，适当添加换行符"  # 系统提示词

# 获取本地IP地址
ip = "0.0.0.0"
port = "8080"  # 端口

welcome_message_template = """-----------
成功连接WebSocket服务器
服务器ip:{ip}
端口:{port}
GPT上下文:function-call不支持关闭上下文，请使用GPT保存
GPT模型:{model}
连接UUID:{uuid}
-----------
"""

COMMANDS = ["#登录", "GPT 聊天", "GPT 保存", "运行命令", "GPT 脚本", "测试天气", "脚本命令"]
EVENT_LISTS = ["PlayerMessage", "PlayerTransform"]
# 使用uuid映射的方式来存储信息
information = {}
connections = {}  # 新增，用于存储所有活动的 WebSocket 连接

async def get_game_information(websocket, connection_uuid):
    await run_command(websocket, "weather query")
    await run_command(websocket, "list")
    await asyncio.sleep(0.5)
    await run_command(websocket, "time query day")
    await run_command(websocket, "time query gametime")
    print(f"已发送信息查询命令给 {connection_uuid}")

async def periodic_update():
    while True:
        for connection_uuid, websocket in connections.items():
            await get_game_information(websocket, connection_uuid)
        await asyncio.sleep(10)

async def gpt_run_command(websocket, command):
    print(f"已发送命令: {command}")
    await run_command(websocket, command)
    #asyncio.sleep(3)
    
    return f"已发送命令: {command}，命令稍后执行"

async def gpt_get_time(websocket, dimension):
    global information
    connection_uuid = websocket.uuid
    gametime = information[connection_uuid]["game_time"]
    gameday = information[connection_uuid]["game_day"]

    json_data = {
        "dimension": dimension,
        "time": gametime,
        "day": gameday,
    }
    return json.dumps(json_data)

async def gpt_game_weather(websocket, dimension):
    global information
    connection_uuid = websocket.uuid
    dimension = dimension #information[connection_uuid]["PlayerTransform_messages"][player_name]["dimension"]
    weather = information[connection_uuid]["game_weather"]
    print(f"收到天气信息: {weather}")
    
    json_data = {
        "dimension": dimension,
        "weather": weather,
    }
    return json.dumps(json_data)

async def gpt_game_players(websocket, dimension):
    global information

    players = information.get(websocket.uuid, {})["players"]
    playersinfo = information.get(websocket.uuid, {})["PlayerTransform_messages"]
    all_players_info = [{"all_players":players}]

    if not playersinfo:
        return json.dumps({"error": "No player transform messages found."})
    
    for player_name, player_info in playersinfo.items():
        if player_info:
            json_data = {
                "player_name": player_info["player_name"],
                "player_yRot": player_info["player_yRot"],
                "player_dimension": player_info["dimension"],
                "position": player_info["position"],
            }
            all_players_info.append(json_data)
    
    return json.dumps(all_players_info)

# 函数映射
functions_map = {
    "gpt_game_weather": gpt_game_weather,
    "gpt_game_players": gpt_game_players,
    "gpt_get_time": gpt_get_time,
    "gpt_run_command": gpt_run_command
}

async def gpt_main(conversation, player_prompt):
    # 发送提示到GPT并获取回复
    gpt_message = await conversation.call_gpt(player_prompt)

    if gpt_message is None:
        gpt_message = '错误: GPT回复为None，模型可能不支持function-call'

    print(f"gpt消息: {gpt_message}")

    return gpt_message

async def send_data(websocket, message):
    """向客户端发送数据"""
    await websocket.send(json.dumps(message))

async def subscribe_events(websocket):
    """订阅事件"""
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
    """向游戏内发送聊天信息"""
    say_message = message.replace('"', '\\"').replace(':', '：').replace('%', '\\%')  # 转义特殊字符，避免报错
    print(say_message)
    game_message = {
        "body": {
            "origin": {
                "type": "say"
            },
            "commandLine": f'tellraw @a {{"rawtext":[{{"text":"§a{say_message}"}}]}}',  #
            "version": 1
        },
        "header": {
            "requestId": str(uuid.uuid4()),  # uuid
            "messagePurpose": "commandRequest",
            "version": 1,
            "EventName": "commandRequest"
        }
    }
    await send_data(websocket, game_message)

async def run_command(websocket, command):
    """运行命令"""
    print(f"命令{command}开始发送")
    message = {
        "body": {
            "origin": {
                "type": "player"
            },
            "commandLine": command,
            "version": 17039360
        },
        "header": {
            "requestId": "9b84bcb2-5390-11ea-9e87-0221860e9b7e",  # uuidstr(uuid.uuid4())
            "messagePurpose": "commandRequest",
            "version": 1,
            "EventName": "commandRequest"
        }
    }
    await send_data(websocket, message)

async def send_script_data(websocket, content, messageid="server:data"):
    """使用脚本事件命令给游戏发送数据"""
    message = {
        "body": {
            "origin": {
                "type": "player"
            },
            "commandLine": f"scriptevent {messageid} {content}",
            "version": 17039360
        },
        "header": {
            "requestId": str(uuid.uuid4()),  # uuid
            "messagePurpose": "commandRequest",
            "version": 1,
            "EventName": "commandRequest"
        }
    }
    await send_data(websocket, message)

async def handle_event_message(websocket, data):
    """处理事件消息事件"""
    global information

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

        # 将 dimension 的数字 ID 转换为对应的字符串值
        dimension_map = {
            0: 'overworld',
            1: 'nether',
            2: 'the_end'
        }
        dimension = dimension_map.get(dimension_id, 'Unknown')

        # 获取位置坐标
        x = player_pos.get('x', 'Unknown')
        y = player_pos.get('y', 'Unknown')
        z = player_pos.get('z', 'Unknown')

        # 构建JSON对象
        player_transform_message = {
            "player_name": player_name,
            "player_id": player_id,
            "player_color": player_color,
            "player_type": player_type,
            "player_variant": player_variant,
            "player_yRot": player_yRot,
            "dimension": dimension,
            "position": {
                "x": x,
                "y": y,
                "z": z
            }
        }

        # 存储在information中
        connection_uuid = websocket.uuid
        if connection_uuid not in information:
            information[connection_uuid] = {}

        if "PlayerTransform_messages" not in information[connection_uuid]:
            information[connection_uuid]["PlayerTransform_messages"] = {}
        
        # 检查是否已经存在该玩家的信息，如果存在则更新
        if player_name in information[connection_uuid]["PlayerTransform_messages"]:
            existing_message = information[connection_uuid]["PlayerTransform_messages"][player_name]
            if existing_message["player_id"] == player_id:
                # 更新现有玩家信息
                information[connection_uuid]["PlayerTransform_messages"][player_name] = player_transform_message
        else:
            # 添加新的玩家信息
            information[connection_uuid]["PlayerTransform_messages"][player_name] = player_transform_message

        # 打印或处理获取到的信息
        # print(f"Player Name: {player_name}")
        # print(f"Player ID: {player_id}")
        # print(f"Player Color: {player_color}")
        # print(f"Player Type: {player_type}")
        # print(f"Player Variant: {player_variant}")
        # print(f"Player yRot: {player_yRot}")
        # print(f"Dimension: {dimension}")
        # print(f"Position - x: {x}, y: {y}, z: {z}")
        print(f"存储在字典的信息： {information[connection_uuid]}")
        #print(f"PlayerTransform_messages: {information[connection_uuid]['PlayerTransform_messages']}")

        
async def handle_command_response(websocket, data):
    global information
    
    print("命令响应处理开始")
    body = data.get('body', {})
    if 'statusMessage' in body:
        message = body['statusMessage']
        print(f"命令响应: {message}")
        
        message_part = message.split('：', 1)
        message_part_space = message.split(' ', 1)

        connection_uuid = websocket.uuid

        if message_part[0] == '天气状态是':
            weather = message_part[1].strip()
            if connection_uuid in information:
                information[connection_uuid]["game_weather"] = weather
            print(f"当前天气: {weather}")
        elif message_part[0][9:13] == '玩家在线':
            players = message_part[1].strip()
            if connection_uuid in information:
                information[connection_uuid]["players"] = players
        elif message_part_space[0] == '游戏时间为':
            gametime = message_part_space[1].strip()
            if connection_uuid in information:
                information[connection_uuid]["game_time"] = gametime
        elif message_part_space[0] == '日期为':
            gameday = message_part_space[1].strip()
            if connection_uuid in information:
                information[connection_uuid]["game_day"] = gameday
        else:
            print("未识别的命令响应")

async def handle_player_message(websocket, data, conversation):
    global connection_uuid
    """处理玩家消息事件"""
    sender = data['body']['sender']
    message = data['body']['message']

    if sender and message:
        print(f"玩家 {sender} 说: {message}")

        command, content = parse_message(message)

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
                await send_game_message(websocket, f"测试结果: {information[connection_uuid]['game_weather']}")
            elif command == "脚本命令":
                await handle_script_run_command(websocket, content)

        if command and not auth.verify_token(stored_token):
            await send_game_message(websocket, "请先登录")

def parse_message(message):
    """解析消息，返回指令和实际内容"""
    for cmd in COMMANDS:
        if message.startswith(cmd):
            return cmd, message[len(cmd):].strip()
    return "", message

async def handle_gpt_chat(websocket, content, conversation):
    prompt = content
    gpt_message = await gpt_main(conversation, prompt)  # 使用 await 调用异步函数
    
    # 使用正则表达式按句号（包括英文句号和中文句号）分割消息
    sentences = re.split(r'(?<=[。])', gpt_message)
    
    for sentence in sentences:
        if sentence.strip():  # 跳过空句子
            await send_game_message(websocket, sentence)
            #await send_script_data(websocket, sentence)  # 使用脚本处理数据
            # await asyncio.sleep(0.1)  # 暂停0.1秒，避免消息发送过快

async def handle_gpt_script(websocket, content, conversation):
    prompt = content
    gpt_message = await gpt_main(conversation, prompt)  # 使用 await 调用异步函数
    
    await send_script_data(websocket, gpt_message)  # 使用脚本处理数据
    await asyncio.sleep(0.1)  # 暂停0.1秒，避免消息发送过快

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
    """根据事件类型处理事件"""
    header = data.get('header', {})
    event_name = header.get('eventName')
    message_purpose = header.get('messagePurpose')

    if event_name == "PlayerMessage":
        await handle_player_message(websocket, data, conversation)
    # 屏蔽玩家操作事件，避免刷屏打印数据
    # if event_name == "PlayerTransform":
    #     pass
    if message_purpose == "commandResponse":
        await handle_command_response(websocket, data)
    print(data)
    print()
    if message_purpose == "event":
        await handle_event_message(websocket, data)

async def handle_connection(websocket, path):
    global connection_uuid
    connection_uuid = str(uuid.uuid4())
    websocket.uuid = connection_uuid
    print(f"客户端:{connection_uuid}已连接")
    conversation = GPTAPIConversation(api_key, api_url, model, functions, functions_map, websocket, system_prompt=system_prompt, enable_logging=True)
    welcome_message = welcome_message_template.format(
        ip=ip, port=port, model=model, uuid=connection_uuid
    )
    await send_game_message(websocket, welcome_message)
    # 初始化uuid对应的信息
    information[connection_uuid] = {
        "game_weather": '',
        "game_time": '',
        "game_day":'',
        "players": ''
    }
    
    # 将连接添加到 connections 字典
    connections[connection_uuid] = websocket
    
    try:
        await send_data(websocket, {"Result": "true"})
        await subscribe_events(websocket)
        async for message in websocket:
            data = json.loads(message)
            await handle_event(websocket, data, conversation)
    except websockets.exceptions.ConnectionClosed:
        print("连接已断开")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        print(f"客户端{connection_uuid}已断开连接")
        await conversation.close()
        # 从 connections 和 information 字典中删除连接
        del connections[connection_uuid]
        del information[connection_uuid]

async def main():
    async with websockets.serve(handle_connection, ip, port):
        print(f"WebSocket服务器已启动，正在监听 {ip}:{port}")
        await asyncio.gather(
            asyncio.Future(),  # 保持服务器运行
            periodic_update()  # 启动定期更新任务
        )

if __name__ == "__main__":
    asyncio.run(main())
