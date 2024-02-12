# MCBE_Websocket 服务器使用GPT

这个项目提供了一个基于Python的Minecraft Bedrock Edition (***MCBE***) 服务器端的WebSocket服务，它可以获取玩家的**聊天信息**，并调用GPT API实现在游戏内使用**chatGPT**，最终将GPT回复传回到游戏中。项目使用aiohttp和Websockets异步。

## 功能

- 获取玩家发送的消息
- 利用GPT API生成回复
- 将GPT的回复发送回MCBE游戏中
- 支持GPT上下文（需要将`enable_history`设为`True`

## 开始

在开始之前，请确保你已经安装了Python 3.7+ , `websockets`以及`aiohttp` 库。

1. 克隆仓库到本地：

```bash
git clone https://github.com/rice-awa/MCBE_WebSocket_gpt.git
cd MCBE_WebSocket_gpt
```

2. 安装所需的Python依赖：
```bash
pip install -r requirements.txt
```
或者使用
```bash
pip install aiohttp
pip install websockets
```

3. 配置API密钥和地址：

编辑 `Websocket.py` 文件夹中的 `api_url` 和 `api_key` 变量，填入你的GPT API信息。

这里推荐使用第三方的转发key（当然官网api也可以）
视频中使用的是：[免费的apikey](https://gpt-houtar.koyeb.app/)
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
- 请确保你有权在MCBE的联机世界中使用/wsserver指令
- 本项目仅供学习和研究使用，作者不承担任何由于滥用API或违反游戏规则导致的责任。

## 反馈

- 有问题？
[联系我](https://space.bilibili.com/521856101)

## 待办事项

- [ ] 添加更详细的安装和配置指南。
- [ ] 实现更多的游戏内交互功能。
- [ ] 提供一个安全的方式来存储API密钥