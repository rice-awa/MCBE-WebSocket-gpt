from typing import Dict, Any, Optional, List
import json
import datetime
import os
import asyncio
from openai import AsyncOpenAI
from ..utils.error_handler import handle_errors
from ..utils.logger import Logger

class GPTAPIConversation:
    def __init__(self, 
                 api_key: str,
                 api_url: str,
                 model: str,
                 functions: List[Dict[str, Any]], 
                 functions_map: Dict[str, Any],
                 websocket,
                 system_prompt: str = "",
                 enable_logging: bool = False):
        """
        初始化GPT对话管理器
        
        Args:
            api_key: OpenAI API密钥
            api_url: API基础URL
            model: 使用的模型名称
            functions: 可用函数列表
            functions_map: 函数映射字典
            websocket: WebSocket连接实例
            system_prompt: 系统提示词
            enable_logging: 是否启用日志
        """
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=api_key, base_url=api_url)
        self.model = model
        self.messages: List[Dict[str, str]] = []
        self.system_prompt = system_prompt
        self.enable_logging = enable_logging
        self.functions = functions
        self.functions_map = functions_map
        self.websocket = websocket

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()

    def log_message(self, message: str) -> None:
        """记录日志消息"""
        if self.enable_logging:
            timestamp = datetime.datetime.now().isoformat()
            log_entry = f"{timestamp} - {message}"
            file_path = os.path.join(os.getcwd(), "message.log")
            with open(file_path, 'a+', encoding='utf-8') as f:
                f.write(f"{log_entry}\n")

    def add_system_prompt(self) -> None:
        """添加系统提示词到消息列表"""
        if not self.messages or (self.messages and self.messages[0]["role"] != "system"):
            self.messages.insert(0, {
                "role": "system",
                "content": self.system_prompt
            })

    @handle_errors
    async def call_gpt(self, prompt: str) -> Optional[str]:
        """
        调用GPT API发送消息并处理响应
        
        Args:
            prompt: 用户输入的提示词
            
        Returns:
            Optional[str]: GPT的响应内容
        """
        self.add_system_prompt()
        Logger.debug(f"系统提示词：{self.system_prompt}")
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
            Logger.debug(f"启用函数调用功能，可用函数列表：{[f['name'] for f in self.functions]}")

        try:
            Logger.debug(f"发送给GPT的完整数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            response = await self.client.chat.completions.create(**data)
            return await self.handle_response(response)
        except Exception as e:
            Logger.error(f"调用GPT API时出错: {str(e)}")
            return None

    async def handle_response(self, response) -> Optional[str]:
        """
        处理GPT API的响应
        
        Args:
            response: GPT API的响应对象
            
        Returns:
            Optional[str]: 处理后的响应内容
        """
        if response.choices:
            choice = response.choices[0]
            Logger.debug(f"GPT原始响应: {choice}")
            
            if choice.message.function_call:
                function_name = choice.message.function_call.name
                function_args = json.loads(choice.message.function_call.arguments)
                
                Logger.debug(f"检测到函数调用:")
                Logger.debug(f"- 函数名称: {function_name}")
                Logger.debug(f"- 函数参数: {json.dumps(function_args, ensure_ascii=False, indent=2)}")
                
                if function_name in self.functions_map:
                    func = self.functions_map[function_name]
                    params = func.__code__.co_varnames[:func.__code__.co_argcount]
                    Logger.debug(f"- 函数期望的参数: {params}")

                    kwargs = {}
                    if 'websocket' in params:
                        kwargs['websocket'] = self.websocket
                        Logger.debug("- 已注入websocket参数")

                    for param, value in function_args.items():
                        if param in params:
                            kwargs[param] = value

                    Logger.debug(f"- 最终调用参数: {kwargs}")
                    function_response = await func(**kwargs)
                    Logger.debug(f"- 函数返回值: {function_response}")
                    
                    self.messages.append({
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                    })
                    return await self.call_gpt(prompt="")
                else:
                    Logger.error(f"未找到函数 {function_name}，可用函数: {list(self.functions_map.keys())}")
            else:
                content = choice.message.content
                Logger.debug(f"GPT文本响应: {content}")
                self.messages.append({
                    "role": "assistant",
                    "content": content
                })
                return content
        return None

    def save_conversation(self) -> None:
        """保存当前对话到文件"""
        file_path = os.path.join(os.getcwd(), 'conversation.json')
        self.log_message(f"保存对话文件,文件路径:{file_path},保存数据:{self.messages}")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=4)

    async def close(self) -> None:
        """关闭API客户端连接"""
        await self.client.close()

    async def restart(self) -> None:
        """重启对话管理器"""
        await self.close()
        await asyncio.sleep(1)  # 确保会话完全关闭
        self.client = AsyncOpenAI(api_key=self.api_key)  # 创建新的客户端
        self.messages = []  # 清空消息列表

class ConversationManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.conversations: Dict[str, GPTAPIConversation] = {}
        
    async def get_or_create_conversation(self, connection_uuid: str) -> GPTAPIConversation:
        if connection_uuid not in self.conversations:
            self.conversations[connection_uuid] = await self.create_conversation()
        return self.conversations[connection_uuid]
        
    async def create_conversation(self) -> GPTAPIConversation:
        return GPTAPIConversation(
            api_key=self.config['api_key'],
            api_url=self.config['api_url'],
            model=self.config['model'],
            functions=self.config['functions'],
            functions_map=self.config['functions_map'],
            websocket=self.config['websocket'],
            system_prompt=self.config['system_prompt'],
            enable_logging=self.config['enable_logging']
        ) 