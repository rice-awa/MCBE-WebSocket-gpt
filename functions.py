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
    "name": "gpt_run_command",
    "description": "能够在游戏中执行一个或多个命令，命令须符合MCBE的命令格式，否则可能无效",
    "parameters": {
        "type": "object",
        "properties": {
            "commands": {
                "type": "array",
                "items": {
                    "type": "string",
                    "description": "需要执行的命令，如 'say hello, world!'"
                },
                "description": "需要执行的一个或多个命令"
            }
        },
        "required": ["commands"]
    }
    },
    {
        "name": "gpt_world_entity",  # 函数名称
        "description": "此函数能够将实体加入获取队列，能获取队列中实体的id，坐标等信息，实体id参数不需要前缀，只能同时获取一个，如果return为查询中，需要告诉玩家再次发起聊天获取",  # 函数描述
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
    {
        "name": "gpt_player_inventory",  # 函数名称
        "description": "此函数能够获取玩家的背包信息(背包物品索引从0开始，只有有物品的格子才有数据，当前格子数为索引值+1)，回答时返回正确格子数而不是索引值，默认不需要指定玩家，返回json格式，回答时不要特殊格式",  # 函数描述
        "parameters": {  # 函数参数
            "type": "object",
            "properties": {
                "player_name": {
                    "type": "string",  # 参数类型
                    "description": "指定查询的玩家,例如：'player1'"  # 参数描述
                }
            }
        }
    },
    {
        "name": "gpt_get_commandlog",  # 函数名称
        "description": "此函数能够获取命令执行的响应,返回上次执行命令的和执行结果,一些需要查看命令执行结果的，需要提示玩家查看",  # 函数描述   
    }
]
