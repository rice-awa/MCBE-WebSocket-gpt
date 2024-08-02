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
        "description": "这是一个与MC交互的函数，能够获取MC当前的玩家数量，可能只有一个玩家",  # 函数描述
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
        "name": "gpt_player_localtion",  # 函数名称
        "description": "这是一个与MC交互的函数，能够获取MC对应的玩家位置信息以及一些参数，当没有选定玩家名时，请不要传入玩家名参数",  # 函数描述
        "parameters": {  # 函数参数
            "type": "object",
            "properties": {
                "player_name": {
                    "type": "string",  # 参数类型
                    "description": "指定查询的玩家名",  # 参数描述  
                }
            }
        }
    },
]

