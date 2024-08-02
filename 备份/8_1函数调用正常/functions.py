# functions.py

import asyncio
import json

# 定义Chat API接口所需的函数参数和描述
functions = [
    {
        "name": "get_current_weather",  # 函数名称
        "description": "获取指定地点的当前天气",  # 函数描述
        "parameters": {  # 函数参数
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",  # 参数类型
                    "description": "城市和地区，例如: 上海, 上海市",  # 参数描述
                },
                "unit": {
                    "type": "string",  # 参数类型
                    "enum": ["摄氏", "华氏"]  # 参数可选值
                },
            },
            "required": ["location"],  # 必需参数
        },
    },
    {
        "name": "gpt_game_weather",  # 函数名称
        "description": "这是一个与MC交互的函数，能够获取MC当前维度的天气",  # 函数描述
        "parameters": {  # 函数参数
            "type": "object",
            "properties": {
                "dimension": {
                    "type": "string",  # 参数类型
                    "description": "玩家目前所在的维度，例如:'overworld'",  # 参数描述
                    "enum": ["overworld", "nether", "the_end"]  # 参数可选值
                }
            },
            "required": ["dimension"]  # 必需参数
        },
    }
]

