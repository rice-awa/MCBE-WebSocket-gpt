from typing import Optional
import traceback
from functools import wraps
import json

class MinecraftGPTError(Exception):
    """基础异常类"""
    pass

class ConnectionError(MinecraftGPTError):
    """连接相关错误"""
    pass

class AuthenticationError(MinecraftGPTError):
    """认证相关错误"""
    pass

def handle_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except MinecraftGPTError as e:
            # 处理已知异常
            print(f"已知错误: {str(e)}")
            websocket = kwargs.get('websocket')
            if websocket:
                await websocket.send(json.dumps({
                    "error": str(e),
                    "type": e.__class__.__name__
                }))
        except Exception as e:
            # 处理未知异常
            print(f"未知错误: {str(e)}")
            traceback.print_exc()
            websocket = kwargs.get('websocket')
            if websocket:
                await websocket.send(json.dumps({
                    "error": "内部服务器错误",
                    "type": "InternalError"
                }))
    return wrapper 