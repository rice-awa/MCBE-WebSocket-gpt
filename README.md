# MCBE_Websocket 服务器

这个项目提供了一个基于Python的Minecraft Bedrock Edition (MCBE) 服务器端的WebSocket服务，它可以获取玩家信息，并利用GPT API提供智能聊天功能，最终将回复传回到游戏中。

## 功能

- 获取玩家发送的消息
- 利用GPT API生成回复
- 将GPT的回复发送回MCBE游戏中

## 安装

在开始之前，请确保你已经安装了Python 3.7+ 和 `websockets` 库。

1. 克隆仓库到本地：

```bash
git clone https://github.com/rice-awa/MCBE_WebSocket_gpt.git
cd MCBE_WebSocket_gpt
```

2. 安装所需的Python依赖：

```bash
pip install -r requirements.txt
```

3. 配置API密钥和地址：

编辑 `Websocket.py` 文件夹中的 `api_url` 和 `api_key` 变量，填入你的GPT API信息。
4. 其他:
这里推荐使用第三方的转发key（当然官网api也可以）
视频中使用的是：
[免费的apikey](https://gpt-houtar.koyeb.app/)
## 使用

启动服务器：

```bash
python Websocket.py
```

## 配置

- `ip` 和 `port` 可以根据你服务器的配置进行修改。
- `enable_history` 选项允许你控制是否启用上下文。

## 贡献

如果你想为这个项目贡献代码，请遵循以下步骤：

1. Fork 这个仓库
2. 创建你的特性分支 (`git checkout -b feature/fooBar`)
3. 提交你的改动 (`git commit -am 'Add some fooBar'`)
4. 推送到分支 (`git push origin feature/fooBar`)
5. 创建一个新的 Pull Request

## 许可证

[MIT](https://github.com/rice-awa/MCBE_WebSocket_gpt/blob/main/LICENSE.txt)

## 注意

- **请不要在公共仓库中硬编码你的API密钥**。你可以使用环境变量或其他安全措施来保护你的密钥。
- 你需要确保你有权使用GPT API，并遵守相关的使用条款。
- 本项目仅供学习和研究使用，作者不承担任何由于滥用API或违反游戏规则导致的责任。

## 待办事项

- [ ] 添加更详细的安装和配置指南。
- [ ] 实现更多的游戏内交互功能。
- [ ] 提供一个安全的方式来存储API密钥