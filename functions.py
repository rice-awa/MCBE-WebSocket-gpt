# functions.py

import asyncio
import json

# 定义Chat API接口所需的函数参数和描述
functions = [
    {
        "name": "gpt_game_weather",  # 函数名称
        "description": "这是一个与MC交互的函数，能够获取MC当前维度的天气",  # 函数描述
        "parameters": {  # 函数参数
            "type": "object",
            "properties": {
                "dimension": {
                    "type": "string",  # 参数类型
                    "description": "玩家目前的维度，例如:'overworld'",  # 参数描述
                    "enum": ["overworld", "nether", "the_end"]  # 参数可选值
                }
            },
            "required": ["dimension"]  # 必需参数
        }
    },
    {
        "name": "gpt_game_players",  # 函数名称
        "description": "这是一个与MC交互的函数，能够获取MC当前的玩家数量，坐标，维度，等信息，该函数返回玩家信息json，回答时不要特殊格式，坐标每次都重新获取不能用上次坐标，小数保留一位小数，除非特殊要求",  # 函数描述
        "parameters": {  # 函数参数
            "type": "object",
            "properties": {
                "dimension": {
                    "type": "string",  # 参数类型
                    "description": "玩家目前的维度，例如:'overworld'",  # 参数描述
                    "enum": ["overworld", "nether", "the_end"]  # 参数可选值
                }
            }
        }
    },
    {
        "name": "gpt_get_time",  # 函数名称
        "description": "获取当前维度的时间",  # 函数描述
        "parameters": {  # 函数参数
            "type": "object",
            "properties": {
                "dimension": {
                    "type": "string",  # 参数类型
                    "description": "玩家目前的维度，例如:'overworld'",  # 参数描述
                    "enum": ["overworld", "nether", "the_end"]  # 参数可选值
                }
            },
            "required": ["dimension"]  # 必需参数
        }
    },
]

