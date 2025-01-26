import aiohttp
import asyncio
import os
import json
import datetime
from openai import AsyncOpenAI

class GPTAPIConversation:
    def __init__(self, api_key, api_url, model, functions, functions_map, websocket, system_prompt="", enable_logging=False):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=api_key, base_url=api_url)  # 使用OpenAI标准库
        self.model = model
        self.messages = []
        self.system_prompt = system_prompt
        self.enable_logging = enable_logging
        self.functions = functions
        self.functions_map = functions_map
        self.websocket = websocket

    async def __aenter__(self):
        """异步上下文管理器的入口方法"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器的退出方法"""
        await self.close()

    def log_message(self, message):
        if self.enable_logging:
            timestamp = datetime.datetime.now().isoformat()
            log_entry = f"{timestamp} - {message}"
            file_path = os.path.join(os.getcwd(), "message.log")
            with open(file_path, 'a+', encoding='utf-8') as f:
                f.write(f"{log_entry}\n")

    def add_system_prompt(self):
        if not self.messages or (self.messages and self.messages[0]["role"] != "system"):
            self.messages.insert(0, {
                "role": "system",
                "content": self.system_prompt
            })

    async def call_gpt(self, prompt):
        self.add_system_prompt()
        self.log_message(f"系统提示词：{self.system_prompt}")
        self.messages.append({
            "role": "user",
            "content": prompt
        })

        data = {
            "messages": self.messages,
            "model": self.model,
            "temperature": 0.5,
            "presence_penalty": 2
        }

        if self.functions:
            data["functions"] = self.functions
            data["function_call"] = "auto"

        self.log_message("发送给gpt的提示: " + prompt)

        try:
            response = await self.client.chat.completions.create(**data)
            return await self.handle_response(response)
        except Exception as e:
            print(f"调用GPT API时出错: {e}")
            return None

    async def handle_response(self, response):
        print(response)
        if response.choices:
            choice = response.choices[0]  # 直接获取第一个选择
            if choice.message.function_call:
                function_name = choice.message.function_call.name
                function_args = json.loads(choice.message.function_call.arguments)
                print(f"调用函数: {function_name}, 参数: {function_args}")
                self.log_message(f"调用函数: {function_name}, 参数: {function_args}")
                if function_name in self.functions_map:
                    func = self.functions_map[function_name]
                    params = func.__code__.co_varnames[:func.__code__.co_argcount]

                    kwargs = {}
                    if 'websocket' in params:
                        kwargs['websocket'] = self.websocket

                    for param, value in function_args.items():
                        if param in params:
                            kwargs[param] = value

                    function_response = await func(**kwargs)  # 等待异步函数完成
                    self.messages.append({
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                    })
                    return await self.call_gpt(prompt="")
            else:
                content = choice.message.content
                self.log_message(f"gpt:{content}")
                self.messages.append({
                    "role": "assistant",
                    "content": content
                })
            return content

    def save_conversation(self):
        file_path = os.path.join(os.getcwd(), 'conversation.json')
        self.log_message(f"保存对话文件,文件路径:{file_path},保存数据:{self.messages}")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=4)

    async def close(self):
        await self.client.close()  # 关闭OpenAI客户端

    async def restart(self):
        await self.close()  # 关闭当前客户端
        await asyncio.sleep(1)  # 确保会话关闭
        self.client = AsyncOpenAI(api_key=self.api_key)  # 创建一个新的客户端
        self.messages = []  # 清空消息列表