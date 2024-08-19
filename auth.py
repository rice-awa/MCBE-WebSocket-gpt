import hashlib
import time
import jwt
import os
import json
import threading
from typing import Optional

# 配置参数
PASSWORD = os.getenv("WEBSOCKET_PASSWORD", "123456")
SECRET_KEY = os.getenv("SECRET_KEY", "qwqqwqqwqwqwqwqwqwqqawawawaawaawa")
TOKEN_EXPIRATION = 1800  # 令牌过期时间（秒）
TOKEN_FILE = "tokens.json"

# 检查环境变量
if not PASSWORD:
    raise ValueError("PASSWORD 环境变量未设置")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY 环境变量未设置")

# 用于存储每个连接的令牌
tokens = []
lock = threading.Lock()

def hash_password(password: str) -> str:
    """对密码进行哈希处理"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(provided_password: object) -> bool:
    """验证提供的密码是否正确"""
    if not isinstance(provided_password, str):
        raise ValueError("Provided password must be a string")
    return hash_password(provided_password) == hash_password(PASSWORD)

def generate_token() -> str:
    """生成JWT令牌"""
    payload = {
        'exp': time.time() + TOKEN_EXPIRATION,
        'iat': time.time()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token: str) -> bool:
    """验证JWT令牌"""
    try:
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

def save_token(connection_uuid: str, token: str) -> None:
    """将令牌保存到内存和文件"""
    with lock:
        # 查找是否已有该UUID的令牌
        for item in tokens:
            if item["uuid"] == connection_uuid:
                item["token"] = token
                break
        else:
            tokens.append({"uuid": connection_uuid, "token": token})
        
        try:
            with open(TOKEN_FILE, "w") as f:
                json.dump(tokens, f)
        except IOError as e:
            print(f"Error saving tokens to file: {e}")

def load_tokens() -> None:
    """从文件加载令牌"""
    global tokens
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as f:
                tokens = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading tokens from file: {e}")

def get_stored_token(connection_uuid: str) -> Optional[str]:
    """获取存储的令牌"""
    with lock:
        for item in tokens:
            if item["uuid"] == connection_uuid:
                return item["token"]
        return None

def is_token_valid(connection_uuid: str) -> bool:
    """检查现有令牌是否有效"""
    token = get_stored_token(connection_uuid)
    return token is not None and verify_token(token)

def remove_token(connection_uuid: str) -> None:
    """移除存储的令牌"""
    with lock:
        tokens[:] = [item for item in tokens if item["uuid"] != connection_uuid]
        try:
            with open(TOKEN_FILE, "w") as f:
                json.dump(tokens, f)
        except IOError as e:
            print(f"Error removing token from file: {e}")

# 在模块加载时加载令牌
load_tokens()