from openai import AsyncOpenAI
import asyncio
import os
import json
import datetime

class GPTAPIConversation:
    def __init__(self, api_key, api_url, model, system_prompt="", enable_logging=False):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=api_key, base_url=api_url)
        self.url = api_url
        self.messages = []
        self.model = model
        self.system_prompt = system_prompt
        self.enable_logging = enable_logging

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

    async def check_connection(self):
        try:
            # 发送一个简单的请求测试连接
            await self.client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model=self.model,
                max_tokens=1
            )
            return True
        except Exception as e:
            print(f"连接测试失败: {str(e)}")
            self.log_message(f"连接测试失败: {str(e)}")
            return False
        
    async def call_gpt(self, prompt, timeout=60):
        try:
            async with asyncio.timeout(timeout):
                if not await self.check_connection():
                    yield {"error": "API连接失败"}
                    return
                self.add_system_prompt()
                self.log_message(f"系统提示词：{self.system_prompt}")
                self.messages.append({ "role": "user","content": prompt })

                data = {
                    "messages": self.messages,
                    "model": self.model,
                    "temperature": 0.5,
                    "stream": True,  # 启用流式响应
                    "max_tokens": None
                }
                self.log_message("发送给gpt的提示: " + prompt)
                
                try:
                    response = await self.client.chat.completions.create(**data)
                    async for chunk in self.handle_stream_response(response):
                        yield chunk
                except Exception as e:
                    print(f"调用GPT API时出错: {str(e)}")
                    self.log_message(f"调用GPT API时出错: {str(e)}")
                    yield None

        except asyncio.TimeoutError:
            self.log_message("API调用超时")
            yield {"type": "error", "content": "API请求超时"}
    
    async def handle_stream_response(self, response):
        reasoning_content = ""
        content = ""
        
        try:
            async for chunk in response:
                try:
                    #print(chunk)
                    if chunk.choices:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                            reasoning_content += delta.reasoning_content
                            yield {"reasoning_content": delta.reasoning_content, "content": None}
                        elif hasattr(delta, 'content') and delta.content is not None:  # 添加 None 检查
                            content += delta.content
                            yield {"reasoning_content": None, "content": delta.content}
                except Exception as e:
                    print(f"处理数据块时出错: {str(e)}")
                    self.log_message(f"处理数据块时出错: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"流式响应处理出错: {str(e)}")
            self.log_message(f"流式响应处理出错: {str(e)}")
            
        finally:
            self.log_message(f"Final Reasoning Content: {reasoning_content}")
            self.log_message(f"Final Content: {content}")
            
            if content:  # 只在有内容时添加消息
                self.messages.append({
                    "role": "assistant",
                    "content": content
                })


    def save_conversation(self):
        file_path = os.path.join(os.getcwd(), 'conversation.json')
        self.log_message(f"保存对话文件,文件路径:{file_path},保存数据:{self.messages}")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=4)

    async def clean_history(self):
        self.messages = []
        self.log_message("已经清除上下文")
        self.add_system_prompt()
