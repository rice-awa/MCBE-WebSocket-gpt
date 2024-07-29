import unittest
import os
import time
import jwt
import hashlib
import json
import threading

# 清理环境变量
if "WEBSOCKET_PASSWORD" in os.environ:
    del os.environ["WEBSOCKET_PASSWORD"]
if "SECRET_KEY" in os.environ:
    del os.environ["SECRET_KEY"]

# 设置环境变量
os.environ["WEBSOCKET_PASSWORD"] = "123456"
os.environ["SECRET_KEY"] = "qwqqwqqwqwqwqwqwqwqqawawawaawaawa"

# 导入模块
import auth as module

class TestPasswordHashing(unittest.TestCase):
    def test_hash_password(self):
        self.assertEqual(module.hash_password("123456"), "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92")

class TestPasswordVerification(unittest.TestCase):
    def test_verify_password(self):
        self.assertTrue(module.verify_password("123456"))
        self.assertFalse(module.verify_password("wrongpassword"))

class TestTokenGeneration(unittest.TestCase):
    def test_generate_token(self):
        token = module.generate_token()
        self.assertTrue(module.verify_token(token))

class TestTokenVerification(unittest.TestCase):
    def test_verify_token(self):
        token = module.generate_token()
        self.assertTrue(module.verify_token(token))
        time.sleep(6)  # 等待令牌过期
        self.assertFalse(module.verify_token(token))

class TestTokenStorage(unittest.TestCase):
    def setUp(self):
        module.tokens = []
        module.load_tokens()

    def test_save_token(self):
        connection_uuid = "123456"
        token = module.generate_token()
        module.save_token(connection_uuid, token)
        self.assertEqual(module.get_stored_token(connection_uuid), token)

    def test_load_tokens(self):
        connection_uuid = "123456"
        token = module.generate_token()
        module.save_token(connection_uuid, token)
        module.tokens = []
        module.load_tokens()
        self.assertEqual(module.get_stored_token(connection_uuid), token)

    def test_is_token_valid(self):
        connection_uuid = "123456"
        token = module.generate_token()
        module.save_token(connection_uuid, token)
        self.assertTrue(module.is_token_valid(connection_uuid))
        time.sleep(6)  # 等待令牌过期
        self.assertFalse(module.is_token_valid(connection_uuid))

    def test_remove_token(self):
        connection_uuid = "123456"
        token = module.generate_token()
        module.save_token(connection_uuid, token)
        module.remove_token(connection_uuid)
        self.assertIsNone(module.get_stored_token(connection_uuid))

if __name__ == '__main__':
    unittest.main()
