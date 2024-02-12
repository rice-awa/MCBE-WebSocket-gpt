import asyncio
import json
import websockets
from gptapi import GPTAPIConversation

# 请修改此处"API_URL"和"API_KEY"
#api_url = "API_URL" # API地址
#api_key = "API_KEY"  # 硬编码api用于本地测试
api_url = "https://gpt-houtar.koyeb.app/v1/chat/completions" # API地址
api_key = "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"  # 硬编码api用于本地测试
system_prompt = "请始终保持积极和专业的态度。回答尽量保持一段话不要太长，适当添加换行符" # 系统提示词

#WebSocket
ip = "localhost" # 如需配置服务器请修改ip
port = "8080"
welcome_message = ""
#初始化conversation变量
conversation = None

# 上下文（临时）
enable_history = False # 默认关闭

async def gpt_main(player_prompt):
    global conversation, enable_history
    # 创建实例
    if conversation is None:
        conversation = GPTAPIConversation(api_key, api_url, system_prompt, enable_logging=True)
    # 发送提示到GPT并获取回复
    gpt_message = await conversation.call_gpt_and_send(player_prompt)
    if gpt_message is None:
        gpt_message = '错误: GPT回复为None'
    print(f"gpt消息: {gpt_message}")

    if not enable_history:
        await conversation.close()
        conversation = None

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
            "requestId": "5511ca37-07ed-4654-93a0-d1784c4b3f8f",  # uuid
            "messagePurpose": "subscribe",
            "version": 1,
            "EventName": "commandRequest"
        }
    }
    await send_data(websocket, message)

async def send_game_message(websocket, message):
    """向游戏内发送聊天信息"""
    say_message = message.replace('"', '\\"').replace(':', '：').replace('%', '\\%') # 转义特殊字符，避免报错
    print(say_message)
    game_message = {
        "body": {
            "origin": {
                "type": "say"
            },
            "commandLine": f'tellraw @a {{"rawtext":[{{"text":"§a{say_message}"}}]}}',
            "version": 1
        },
        "header": {
            "requestId": "5511ca37-07ed-4654-93a0-d1784c4b3f8f",  # uuid
            "messagePurpose": "commandRequest",
            "version": 1,
            "EventName": "commandRequest"
        }
    }
    await send_data(websocket, game_message)

async def handle_player_message(websocket, data):
    global conversation, enable_history
    """处理玩家消息事件"""
    sender = data['body']['sender']
    message = data['body']['message']
    
    if sender and message:
        print(f"玩家{sender}说: {message}")
        if message.startswith("GPT 聊天"):
            prompt = message[len("GPT 聊天 "):]
            gpt_message = await gpt_main(prompt)  # 使用 await 调用异步函数
            # 分割消息为长度不超过50的多个部分
            message_parts = [gpt_message[i:i+50] for i in range(0, len(gpt_message), 50)]
            for part in message_parts:
                print(part)
                await send_game_message(websocket, part)
        elif message.startswith("GPT 保存"):
            await conversation.save_conversation()
            await conversation.close()
            conversation = None
            await send_game_message(websocket, "对话关闭，数据已保存！")
        elif message.startswith("GPT 上下文"):
            await send_game_message(websocket, f"GPT上下文状态:{enable_history}")
            if message[len("GPT 上下文 "):] == "启用":
                enable_history = True
                await send_game_message(websocket, "GPT上下文已启用，注意tokens消耗!")
            elif message[len("GPT 上下文 "):] == "关闭":
                enable_history = False
                await send_game_message(websocket, "GPT上下文已关闭")

async def handle_event(websocket, data):
    """根据事件类型处理事件"""
    header = data.get('header', {})
    event_name = header.get('eventName')
    if event_name == "PlayerMessage":
        await handle_player_message(websocket, data)

async def handle_connection(websocket, path):
    print("客户端已连接")
    await send_game_message(websocket, welcome_message)
    try:
        await send_data(websocket, {"Result": "true"})
        await subscribe_events(websocket)
        async for message in websocket:
            data = json.loads(message)
            await handle_event(websocket, data)
    except websockets.exceptions.ConnectionClosed:
        print("连接已断开")
    finally:
        print("客户端已断开连接")

async def main():
    async with websockets.serve(handle_connection, ip, port):
        await asyncio.Future()  

if __name__ == "__main__":
    asyncio.run(main())
