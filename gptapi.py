import aiohttp
import asyncio
import os
import json
import datetime
import aiofiles

class GPTAPIConversation:
    def __init__(self, api_key, api_url, model, functions, functions_map, websocket, system_prompt="", enable_logging=False):
        self.api_key = api_key
        self.url = api_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.messages = []
        self.model = model
        self.system_prompt = system_prompt
        self.enable_logging = enable_logging
        self.functions = functions
        self.functions_map = functions_map
        self.websocket = websocket
        self.session = None  # 延迟创建会话

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def log_message(self, message):
        if self.enable_logging:
            timestamp = datetime.datetime.now().isoformat()
            log_entry = f"{timestamp} - {message}"
            file_path = os.path.join(os.getcwd(), "message.log")
            async with aiofiles.open(file_path, 'a+', encoding='utf-8') as f:
                await f.write(f"{log_entry}\n")

    def add_system_prompt(self):
        if not self.messages or (self.messages and self.messages[0]["role"] != "system"):
            self.messages.insert(0, {
                "role": "system",
                "content": self.system_prompt
            })

    async def call_gpt(self, prompt):
        if not self.session:
            raise RuntimeError("Session has not been initialized. Use 'async with' to create the session.")

        self.add_system_prompt()
        await self.log_message(f"系统提示词：{self.system_prompt}")
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

        await self.log_message("发送给gpt的提示: " + prompt)

        response = None
        try:
            async with self.session.post(self.url, headers=self.headers, json=data) as response:
                response.raise_for_status()
                result = await response.json()
                return await self.handle_response(result)
        except aiohttp.ContentTypeError as e:
            print("JSON decode error:", e)
        except aiohttp.ClientResponseError as errh:
            print("Http Error:", errh)
            if response:
                print("Status code:", response.status)
        except Exception as e:
            print("Unexpected error:", e)

    async def handle_response(self, result):
        if 'choices' in result and result['choices']:
            content = ""
            for choice in result['choices']:
                if 'message' in choice:
                    if 'function_call' in choice['message']:
                        function_name = choice['message']['function_call']['name']
                        function_args = json.loads(choice['message']['function_call']['arguments'])
                        print(f"调用函数: {function_name}, 参数: {function_args}")
                        await self.log_message(f"调用函数: {function_name}, 参数: {function_args}")
                        if function_name in self.functions_map:
                            func = self.functions_map[function_name]
                            params = func.__code__.co_varnames[:func.__code__.co_argcount]
                            
                            kwargs = {}
                            if 'websocket' in params:
                                kwargs['websocket'] = self.websocket
                            
                            for param, value in function_args.items():
                                if param in params:
                                    kwargs[param] = value
                            
                            if asyncio.iscoroutinefunction(func):
                                function_response = await func(**kwargs)
                            else:
                                function_response = func(**kwargs)

                            self.messages.append({
                                "role": "function",
                                "name": function_name,
                                "content": function_response,
                            })
                            return await self.call_gpt(prompt="")
                    else:
                        content = choice['message']['content']
                        await self.log_message(f"gpt:{content}")
                        self.messages.append({
                            "role": "assistant",
                            "content": content
                        })
            return content

    async def save_conversation(self):
        file_path = os.path.join(os.getcwd(), 'conversation.json')
        await self.log_message(f"保存对话文件,文件路径:{file_path},保存数据:{self.messages}")

        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(self.messages, ensure_ascii=False, indent=4))

    async def close(self):
        await self.session.close()

    async def restart(self):
        await self.__aexit__(None, None, None)
        await asyncio.sleep(1)
        await self.__aenter__()
        self.messages = []

