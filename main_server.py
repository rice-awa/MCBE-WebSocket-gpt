import asyncio
import json
import os
import re
import auth
import uuid
import websockets
from gptapi import GPTAPIConversation

api_url = "https://api.siliconflow.cn" # API地址
api_key = os.getenv("siliconflow_apikey")  # API密钥

# api_url = "https://burn.hair/v1" # API地址
# api_key = os.getenv("API_KEY")  # API密钥

if not api_url:
    raise ValueError("API_URL 环境变量未设置")
if not api_key:
    raise ValueError("API_KEY 环境变量未设置")

model = "deepseek-ai/DeepSeek-R1" # 模型
#model = "gpt-4o" # 模型
system_prompt = "请始终保持积极和专业的态度。回答尽量保持一段话不要太长，适当添加换行符，尽量不要使用markdown" # 系统提示词

# 上下文（临时）
enable_history = True
output_think = True

# 获取本地IP地址
ip = "0.0.0.0"
port = "8080" # 端口

welcome_message_template = """-----------
成功连接WebSocket服务器
服务器ip:{ip}
端口:{port}
上下文:{enable_history}
模型:{model}
思维链输出:{output_think}
连接UUID:{uuid}
-----------"""

SENDERS = ['外部']
COMMANDS = ["#登录", "GPT 聊天", "GPT 保存", "GPT 上下文", "运行命令", "GPT 脚本"]

async def gpt_main(conversation, player_prompt):
    try:
        reasoning_buffer = ""  # 缓存思考过程
        content_buffer = ""  # 缓存最终内容

        async for chunk in conversation.call_gpt(player_prompt):
            if chunk is None:
                content = '错误: GPT回复为None'
                conversation.log_message(content)
                yield {"type": "error", "content": content}
                return

            if chunk["reasoning_content"] and output_think:
                reasoning_buffer += chunk["reasoning_content"]
                # 检查是否有完整的句子
                sentences = re.split(r'(?<=[。．.])', reasoning_buffer)
                if len(sentences) > 1:  # 有完整的句子
                    for sentence in sentences[:-1]:  # 发送完整的句子，保留未完成的句子
                        if sentence.strip():
                            yield {"type": "reasoning", "content": sentence}
                    reasoning_buffer = sentences[-1]  # 更新缓存区为未完成的句子

            if chunk["content"]:
                content_buffer += chunk["content"]
                # 检查是否有完整的句子
                sentences = re.split(r'(?<=[。．.])', content_buffer)
                if len(sentences) > 1:  # 有完整的句子
                    for sentence in sentences[:-1]:  # 发送完整的句子，保留未完成的句子
                        if sentence.strip():
                            yield {"type": "content", "content": sentence}
                    content_buffer = sentences[-1]  # 更新缓存区为未完成的句子

        # 发送缓存区剩余的内容
        if reasoning_buffer.strip():
            yield {"type": "reasoning", "content": reasoning_buffer}
        if content_buffer.strip():
            yield {"type": "content", "content": content_buffer}

        if not enable_history:
            await conversation.clean_history()

    except Exception as e:
        conversation.log_message(f"gpt_main 函数中发生错误: {e}")
        yield {"type": "error", "content": f"错误: {str(e)}"}

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
        # 过滤服务器消息
        if sender not in SENDERS:
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
    is_thinking = False
    
    async for result in gpt_main(conversation, prompt):
        if result["type"] == "reasoning" and output_think:
            if not is_thinking:
                # 开始思考，发送开始标签
                await send_game_message(websocket, "|think-start|\n")
                is_thinking = True
            await send_game_message(websocket, f"{result['content']}")
        
        elif result["type"] == "content":
            if is_thinking:
                # 如果之前在思考，现在要发送内容了，先发送结束标签
                await send_game_message(websocket, "|think-end|\n")
                is_thinking = False
            await send_game_message(websocket, result["content"])
        
        elif result["type"] == "error":
            if is_thinking:
                is_thinking = False
            await send_game_message(websocket, result["content"])

        await asyncio.sleep(0.1)  # 暂停0.1秒，避免消息发送过快
    
    # 如果循环结束时还在思考状态，确保发送结束标签
    if is_thinking:
        await send_game_message(websocket, "|think-end|\n")

async def handle_gpt_script(websocket, content, conversation):
    prompt = content
    is_thinking = False

    async for result in gpt_main(conversation, prompt):
        if result["type"] == "reasoning" and output_think:
            if not is_thinking:
                await send_script_data(websocket, "|think-start|\n")
                is_thinking = True
            await send_script_data(websocket, f"{result['content']}")
        elif result["type"] == "content":
            if is_thinking:
                await send_script_data(websocket, "|think-end|\n")
                is_thinking = False
            await send_script_data(websocket, result["content"])
    if is_thinking:
        await send_script_data(websocket, "|think-end|\n")

async def handle_gpt_save(websocket, conversation):
    if not conversation:
        await send_game_message(websocket, "上下文已关闭，无法保存！")
        return 
    else:
        conversation.save_conversation()
    await conversation.clean_history()
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
    # else:
    #     print(data)
    #     print()

async def handle_connection(websocket, path):
    global connection_uuid
    connection_uuid = str(uuid.uuid4())
    print(f"客户端:{connection_uuid}已连接")
    conversation = GPTAPIConversation(api_key, api_url, model, system_prompt, enable_logging=True)
    welcome_message = welcome_message_template.format(
        ip=ip, port=port, enable_history=enable_history, output_think=output_think, model=model, uuid=connection_uuid
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
        print(f"客户端{connection_uuid}已断开连接")
        await conversation.clean_history()


websocket_config = {
    'ping_interval': 30,
    'ping_timeout': 15,
    'close_timeout': 15,
    'max_size': 10 * 1024 * 1024,  # 10MB
    'max_queue': 32,
    'read_limit': 65536,
    'write_limit': 65536,
}

async def main():
    async with websockets.serve(handle_connection, ip, port, **websocket_config):
        print(f"WebSocket服务器已启动，正在监听 {ip}:{port}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
