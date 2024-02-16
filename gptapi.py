import aiohttp
import os
import json
import datetime


# 定义一个类来管理与GPT API的会话和上下文
class GPTAPIConversation:
    def __init__(self, api_key, api_url, model,  system_prompt="", enable_logging=False):
        self.api_key = api_key  # API密钥
        self.session = aiohttp.ClientSession()  # 创建一个aiohttp会话
        self.url = api_url  # API URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"  # 设置认证头
        }
        self.messages = []  # 存储对话历史的列表
        self.messages_data = '' # 存储完整对话数据
        self.system_prompt = system_prompt  # 系统级提示词
        self.enable_logging = enable_logging  # 控制日志记录的开关
        self.model = model # GPT对话模型
        
    def log_message(self, message):
        if self.enable_logging:
            timestamp = datetime.datetime.now().isoformat()  # 获取当前时间的ISO格式字符串
            log_entry = f"{timestamp} - {message}"  # 创建日志条目
            # print(log_entry)
            # 这里也可以将日志条目写入到文件或其他日志记录系统中
            file_path = os.path.join(os.getcwd(), "message.log")
            with open(file_path, 'a+', encoding='utf-8') as f:
                f.write(f"{log_entry}\n")

    async def parse_sse_and_send(self, response):
        async for line in response.content:
            if line:
                try:
                    line_text = line.decode('utf-8').strip()
                    if line_text == 'data: [DONE]':  # 检测到结束标记，退出循环
                        break
                    if line_text.startswith("data:"):
                        json_event = json.loads(line_text[len("data:"):].strip())
                        if 'choices' in json_event and json_event['choices']:
                            choice = json_event['choices'][0]
                            content = choice.get('delta', {}).get('content', '')
                            self.messages_data += content # 把内容传入messages_data获取完整对话
                            if choice.get('finish_reason') == 'stop':
                                # 当GPT完成回复时，将整个回复添加到对话历史中
                                complete_message = self.messages_data
                                self.log_message(f"gpt:{complete_message}")
                                self.messages.append({
                                    "role": "assistant",
                                    "content": complete_message
                                })
                                self.messages_data = ''  # 清空messages_data以便下次使用
                except UnicodeDecodeError as e:
                    print("Unicode decode error:", e)
                except json.JSONDecodeError as e:
                    print("JSON decode error:", e)
        return complete_message  # 返回消息

    def add_system_prompt(self):
    # 只有当对话历史为空，或者第一条消息不是系统提示时，才添加系统提示
        if not self.messages or (self.messages and self.messages[0]["role"] != "system"):
            self.messages.insert(0, {
                "role": "system",
                "content": self.system_prompt
            })
            self.log_message(f"系统提示词：{self.system_prompt}")
    async def call_gpt_and_send(self, prompt):
        self.add_system_prompt()
        self.messages.append({
            "role": "user",
            "content": prompt
        })
        data = {
            "messages": self.messages,
            "stream": True,
            "model": self.model,
            "temperature": 0.5,
            "presence_penalty": 2
        }
        self.log_message("发送给gpt的提示: " + prompt)  # 记录发送给GPT的提示

        async with self.session.post(self.url, headers=self.headers, json=data) as response:
            try:
                response.raise_for_status()  # 检查响应是否成功
                return await self.parse_sse_and_send(response)  # 返回处理后的消息
            except aiohttp.ClientResponseError as errh:
                print("Http Error:", errh)
                print("Status code:", response.status)

    async def save_conversation(self):
        # 创建文件的完整路径

        file_path = os.path.join(os.getcwd(), 'conversation.json')
        self.log_message(f"保存对话文件,文件路径:{file_path},保存数据:{self.messages}")  # 记录保存对话的行为
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=4)
    async def close(self):
        await self.session.close()  # 关闭会话

# # 使用此类的异步代码示例
# async def main():
#     api_key = "your_api_key_here"
#     system_prompt = "This is a system prompt."
#     conversation = GPTAPIConversation(api_key, system_prompt, enable_logging=True)

#     # 发送提示到GPT并获取回复
#     messages = await conversation.call_gpt_and_send("Hello, GPT!")
#     print(messages)

#     # 保存对话
#     conversation.save_conversation()

#     # 关闭会话
#     await conversation.close()

# # 运行异步主函数
# asyncio.run(main())