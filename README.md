# MCBE_Websocket 服务器使用GPT

这个项目提供了一个基于Python的Minecraft Bedrock Edition (***MCBE***) 服务器端的WebSocket服务，它可以获取玩家的**聊天信息**，并调用GPT API实现在游戏内使用**chatGPT**，最终将GPT回复传回到游戏中。项目使用aiohttp和Websockets异步。

## 目录

- [功能](#功能)
- [开始](#开始)
- [配置](#配置)
- [使用](#使用)
- [注意](#注意)
- [贡献](#贡献)
- [许可证](#许可证)
- [反馈](#反馈)
- [待办事项](#待办事项)

## 功能

- 获取玩家发送的消息
- 利用GPT API生成回复
- 将GPT的回复发送回MCBE游戏中
- 支持GPT上下文（需要将`enable_history`设为`True`）

## 开始

在开始之前，请确保你已经安装了Python 3.7+，`websockets`以及`aiohttp`库。

1. 克隆仓库到本地：

    ```bash
    git clone https://github.com/rice-awa/MCBE_WebSocket_gpt.git
    cd MCBE_WebSocket_gpt
    ```

2. 安装所需的Python依赖：

    ```bash
    pip install -r requirements.txt
    ```
    
    或者使用：
    
    ```bash
    pip install aiohttp
    pip install websockets
    ```

## 配置

- 配置API密钥和地址：

  编辑 `Websocket.py` 文件中的 `api_url` 和 `api_key` 变量，填入你的GPT API信息。

  这里推荐使用第三方的转发key（当然官网api也可以）。
  
  视频中使用的是：[免费的apikey](https://gpt-houtar.koyeb.app)

- `ip` 和 `port` 可以根据你服务器的配置进行修改。
- `enable_history` 选项允许你控制是否启用上下文。

## 使用

1. 启动服务器：

    ```bash
    python Websocket.py
    ```

2. 打开Minecraft在聊天框输入：

    ```base
    /wsserver localhost:8080
    ```
    
    ![wsserver](https://s11.ax1x.com/2024/02/13/pF8y0dU.png)
    
    这里的localhost:8080是ip加端口，根据自己的设置填写，默认为上面提到的配置。

3. 聊天命令`GPT 聊天 {内容}`注意需要空格分开，例如：

    ![](https://s11.ax1x.com/2024/02/13/pF8yRL6.png)
    
    **GPT回复为绿色字体**

4. 保存和关闭会话：

    ![](https://s11.ax1x.com/2024/02/13/pF8y4oD.png)
    
    保存完毕后根目录会有对话记录和日志。
    
    ![](https://s11.ax1x.com/2024/02/13/pF8yXef.png)

## 注意

- **请不要在公共仓库中硬编码你的API密钥**。你可以使用环境变量或其他安全措施来保护你的密钥。
- 你需要确保你有权使用GPT API，并遵守相关的使用条款。
- 请确保你有权在MCBE的联机世界中使用`/wsserver`指令。
- 本项目仅供学习和研究使用，作者不承担任何由于滥用API或违反游戏规则导致的责任。

## 贡献

如果你想为这个项目贡献代码，请遵循以下步骤：

1. Fork 这个仓库。
2. 创建你的特性分支 (`git checkout -b feature/fooBar`)。
3. 提交你的改动 (`git commit -am 'Add some fooBar'`)。
4. 推送到分支 (`git push origin feature/fooBar`)。
5. 创建一个新的 Pull Request。

## 许可证

[MIT](https://github.com/rice-awa/MCBE_WebSocket_gpt/blob/main/LICENSE.txt)

## 反馈

- 有问题？[联系我](https://space.bilibili.com/521856101)

## 待办事项

- [ ] 添加更详细的安装和配置指南。
- [ ] 实现更多的游戏内交互功能。
- [ ] 提供一个安全的方式来存储API密钥。