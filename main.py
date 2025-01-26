import asyncio
import yaml
import os
from src.utils.logger import Logger
from src.server.websocket_server import MinecraftGPTServer

def validate_config(config):
    """验证配置文件的完整性"""
    required_sections = [
        'server', 'gpt', 'commands', 'messages', 
        'functions_map', 'welcome_message_template',
        'event_lists'
    ]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"配置文件缺少必要的 '{section}' 部分")
    
    if 'host' not in config['server'] or 'port' not in config['server']:
        raise ValueError("server 配置缺少 host 或 port")
    
    gpt_required = ['api_url', 'model', 'system_prompt']
    for key in gpt_required:
        if key not in config['gpt']:
            raise ValueError(f"gpt 配置缺少 {key}")

async def main():
    try:
        # 检查环境变量
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise ValueError("环境变量 API_KEY 未设置")
        
        # 加载并验证配置
        config_path = 'config/config.yaml'
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        validate_config(config)
        Logger.info("配置验证通过")
        
        server = MinecraftGPTServer(
            host=config['server']['host'],
            port=config['server']['port'],
            config=config
        )
        
        # 启动定期更新任务和WebSocket服务器
        await asyncio.gather(
            server.start_periodic_updates(),
            server.start()
        )
        
    except Exception as e:
        Logger.error(f"启动服务器时发生错误: {str(e)}")
        import traceback
        Logger.error(f"堆栈跟踪:\n{traceback.format_exc()}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 