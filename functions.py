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
        "description": "获取当前维度的时间，游戏时间gametime按tick算，day为游戏天数，玩家询问时间时，请直接告诉玩家换算后的结果，如：早上，正午，晚上",  # 函数描述"
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
        "name": "gpt_run_command",  # 函数名称
        "description": "能够在游戏执行命令，命令须符合MCBE的命令格式，否则可能无效",  # 函数描述
        "parameters": {  # 函数参数
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",  # 参数类型
                    "description": "需要执行的命令:'say hello,world!'"  # 参数描述
                }
            },
            "required": ["command"]  # 必需参数
        }
    },
    {
        "name": "gpt_world_entity",  # 函数名称
        "description": "此函数能够将实体加入获取队列，能获取队列中实体的id，坐标等信息，实体id参数不需要前缀，如果return为空，需要重新调用该函数刷新",  # 函数描述
        "parameters": {  # 函数参数
            "type": "object",
            "properties": {
                "entityid": {
                    "type": "string",  # 参数类型
                    "description": "查询的实体，例如：pig , zombie"  # 参数描述
                }
            },
            "required": ["entityid"]  # 必需参数
        }
    },
]

