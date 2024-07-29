import hashlib
import time
import jwt
import os
import json

# 密码和密钥可以从环境变量中获取
PASSWORD = os.getenv("WEBSOCKET_PASSWORD", "123456")
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key:qwqqwqqwqwqwqwqwqwqqawawawaawaawa")

if not PASSWORD:
    raise ValueError("PASSWORD 环境变量未设置")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY 环境变量未设置")
# 令牌过期时间（秒）
TOKEN_EXPIRATION = 3600  # 1小时
TOKEN_FILE = "tokens.json"

def hash_password(password):
    """对密码进行哈希处理"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(provided_password):
    """验证提供的密码是否正确"""
    return hash_password(provided_password) == hash_password(PASSWORD)

def generate_token():
    """生成JWT令牌"""
    payload = {
        'exp': time.time() + TOKEN_EXPIRATION,
        'iat': time.time()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """验证JWT令牌"""
    try:
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

def save_token(token):
    """将令牌保存到本地文件"""
    tokens = load_tokens()
    tokens["token"] = token
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)

def load_tokens():
    """从本地文件加载令牌"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return {}

def get_stored_token():
    """获取存储的令牌"""
    tokens = load_tokens()
    return tokens.get("token")

def is_token_valid():
    """检查现有令牌是否有效"""
    token = get_stored_token()
    return token and verify_token(token)
