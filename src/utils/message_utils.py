import json
import uuid
from typing import Dict, Any
from src.models.server_state import ServerState
from src.utils.logger import Logger

async def send_data(websocket, message: Dict[str, Any]):
    await websocket.send(json.dumps(message))

async def send_game_message(websocket, message):
    say_message = message.replace('"', '\\"').replace(':', '：').replace('%', '\\%')
    say_message = "§a" + say_message
    complete_message = json.dumps(say_message, ensure_ascii=False)
    Logger.debug(f"发送游戏消息: {complete_message}")
    commandLine = f'tellraw @a {{"rawtext":[{{"text":{complete_message}}}]}}'
    
    game_message = {
        "body": {
            "origin": {"type": "say"},
            "commandLine": commandLine,
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

async def run_command(websocket, command: str, requestid: str = None):
    Logger.debug(f"执行命令: {command}")
    if not requestid:
        requestid = str(uuid.uuid4())
        
    message = {
        "body": {
            "origin": {"type": "player"},
            "commandLine": command,
            "version": 1
        },
        "header": {
            "requestId": requestid,
            "messagePurpose": "commandRequest",
            "version": 1,
            "EventName": "commandRequest"
        }
    }
    
    await send_data(websocket, message)
    return requestid

async def send_script_data(websocket, command: str, script_type: str):
    Logger.debug(f"发送脚本命令: {command}")
    message = {
        "body": {
            "origin": {"type": script_type},
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
    await send_data(websocket, message)