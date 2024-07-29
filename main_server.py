import asyncio
import json
import os
import re
import auth
import uuid
import websockets
from gptapi import GPTAPIConversation

api_url = os.getenv("API_URL")  # API地址
api_key = os.getenv("API_KEY")  # API密钥

if not api_url:
    raise ValueError("API_URL 环境变量未设置")
if not api_key:
    raise ValueError("API_KEY 环境变量未设置")

model = "gpt-4o-mini" # gpt模型
system_prompt = "请始终保持积极和专业的态度。回答尽量保持一段话不要太长，适当添加换行符" # 系统提示词

# 上下文（临时）
enable_history = False # 默认关闭

# 获取本地IP地址
ip = "0.0.0.0"
port = "8080" # 端口

welcome_message_template = """-----------
成功连接WebSocket服务器
服务器ip:{ip}
端口:{port}
GPT上下文:{enable_history}
GPT模型:{model}
连接UUID:{uuid}
-----------"""

COMMANDS = ["#登录", "GPT 聊天", "GPT 保存", "GPT 上下文", "运行命令", "GPT 脚本"]

async def gpt_main(conversation, player_prompt):
    # 发送提示到GPT并获取回复
    gpt_message = await conversation.call_gpt(player_prompt)

    if gpt_message is None:
        gpt_message = '错误: GPT回复为None'

    print(f"gpt消息: {gpt_message}")

    if not enable_history:
        await conversation.close()

    return gpt_message

async def send_data(websocket, message):
    """向客户端发送数据"""
    await websocket.send(json.dumps(message))

async def subscribe_events(websocket):
    """订阅事件"""
    message = {
        "body": {
            "eventName": "PlayerMessage"
        },
        "header": {
            "requestId": str(uuid.uuid4()),  # uuid
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
    message = {
        "body": {
            "origin": {
                "type": "player"
            },
            "commandLine": command,
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

async def handle_player_message(websocket, data, conversation):
    global enable_history, connection_uuid
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
            elif command == "GPT 上下文":
                await handle_gpt_context(websocket, content)
            elif command == "运行命令":
                await handle_run_command(websocket, content)

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
    sentences = re.split(r'(?<=[。．.])', gpt_message)
    
    for sentence in sentences:
        if sentence.strip():  # 跳过空句子
            await send_game_message(websocket, sentence)  # 使用脚本处理数据
            await asyncio.sleep(0.1)  # 暂停0.1秒，避免消息发送过快

async def handle_gpt_script(websocket, content, conversation):
    prompt = content
    gpt_message = await gpt_main(conversation, prompt)  # 使用 await 调用异步函数
    
    await send_script_data(websocket, gpt_message)  # 使用脚本处理数据
    await asyncio.sleep(0.1)  # 暂停0.1秒，避免消息发送过快

async def handle_gpt_save(websocket, conversation):
    if not conversation:
        await send_game_message(websocket, "上下文已关闭，无法保存！")
        return 
    else:
        await conversation.save_conversation()
    await conversation.close()
    await send_game_message(websocket, "对话关闭，数据已保存！")

async def handle_gpt_context(websocket, content):
    global enable_history
    
    if content == "启用":
        enable_history = True
        await send_game_message(websocket, f"GPT上下文状态: {enable_history}")
        await send_game_message(websocket, "GPT上下文已启用，注意tokens消耗!")
    elif content == "关闭":
        enable_history = False
        await send_game_message(websocket, f"GPT上下文状态: {enable_history}")
        await send_game_message(websocket, "GPT上下文已关闭")
    elif content == "状态":
        await send_game_message(websocket, f"GPT上下文状态: {enable_history}")
    else:
        await send_game_message(websocket, "无效的上下文指令，请输入启用或关闭")

async def handle_run_command(websocket, content):
    command = content
    await run_command(websocket, command)

async def handle_event(websocket, data, conversation):
    """根据事件类型处理事件"""
    header = data.get('header', {})
    event_name = header.get('eventName')
    if event_name == "PlayerMessage":
        await handle_player_message(websocket, data, conversation)
    # 屏蔽玩家操作事件，避免刷屏打印数据
    if event_name != "PlayerTransform":
        print(data)
        print()

async def handle_connection(websocket, path):
    global connection_uuid
    print("客户端已连接")
    connection_uuid = str(uuid.uuid4())
    conversation = GPTAPIConversation(api_key, api_url, model, system_prompt, enable_logging=True)
    welcome_message = welcome_message_template.format(
        ip=ip, port=port, enable_history=enable_history, model=model, uuid=connection_uuid
    )
    await send_game_message(websocket, welcome_message)
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
        print("客户端已断开连接")
        await conversation.close()

async def main():
    async with websockets.serve(handle_connection, ip, port):
        print(f"WebSocket服务器已启动，正在监听 {ip}:{port}")
        await asyncio.Future()  # 保持服务器运行

if __name__ == "__main__":
    asyncio.run(main())
