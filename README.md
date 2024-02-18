# MCBE Websocket Server 游戏内使用GPT
[English](./README_EN.md)

这个项目提供了一个基于Python的Minecraft Bedrock Edition (***MCBE***) 服务器端的WebSocket服务，它可以获取玩家的**聊天信息**，并调用GPT API实现在游戏内使用**chatGPT**，最终将GPT回复传回到游戏中。项目使用aiohttp和Websockets异步。

~~如果你问我就一个小项目，自述文件写那么多干嘛？我闲的（~~

---

**目录**

- [功能特点](#功能特点)
- [快速开始](#快速开始)
- [配置指南](#配置指南)
- [使用说明](#使用说明)
- [注意事项](#注意事项)
- [如何贡献](#如何贡献)
- [许可信息](#许可信息)
- [问题反馈](#问题反馈)
- [待办清单](#待办清单)

---

## 功能特点

- **捕获玩家消息**：实时获取玩家在游戏中的聊天信息。
- **GPT回复生成**：通过 GPT API 生成回复内容。
- **游戏显示**：将 GPT 生成的回复直接发送至 MCBE 中。
- **支持上下文**：通过设置 `enable_history` 为 `True` 来启用会话历史记录。

---

## 快速开始

确保你的环境已安装 Python 3.7+，`websockets` 和 `aiohttp`。

1. **克隆项目**：

    ```bash
    git clone https://github.com/rice-awa/MCBE_WebSocket_gpt.git
    cd MCBE_WebSocket_gpt
    ```

2. **安装依赖**：

    ```bash
    pip install -r requirements.txt
    ```

    或者单独安装：

    ```bash
    pip install aiohttp
    pip install websockets
    ```

---

## 配置指南

- **设置 API 密钥**：

  在 `Websocket.py` 文件中找到 `api_url` 和 `api_key`，并填入你的 GPT API 信息。

  这里推荐使用第三方转发key，推荐使用这个 [免费的apikey](https://gpt-houtar.koyeb.app) 当然官方APIKEY也可以。

- **服务器设置**：

  根据你的服务器配置，修改 `ip` 和 `port` 参数。
  
  启用 `enable_history` 来控制是否记录会话上下文。

---

## 使用说明

1. **启动 WebSocket 服务器**：

    ```bash
    python Websocket.py
    ```

2. **连接服务器**：

    在 Minecraft 聊天框输入 `/wsserver localhost:8080`。

    ![wsserver](https://s11.ax1x.com/2024/02/13/pF8y0dU.png)

3. **使用聊天命令**：

    聊天输入 `GPT 聊天 {内容}` 与 GPT 对话。这里注意每个参数需要空格隔开

    ![GPT聊天](https://s11.ax1x.com/2024/02/13/pF8yRL6.png)

    GPT 回复为绿色字体。

4. **保存对话**：
    - 输入`GPT 保存`来保存对话。注意"保存"的后面不要有空格
    - 保存和关闭会话后，会在根目录生成对话记录和日志。

    ![对话日志](https://s11.ax1x.com/2024/02/13/pF8yXef.png)

5. **上下文**
    - `GPT 上下文` 查看当前上下文状态
    - `GPT 上下文 启用` 开启GPT上下文
    - `GPT 上下文 关闭` 关闭GPT上下文

---

## 注意事项

- **保护你的 API 密钥**：不要在**公共代码库中直接编写你的API密钥**，可以使用环境变量或其他安全方法。
- **合法使用 API**：确保你有权使用 GPT API 并遵守相关条款。不要滥用API。
- **遵守游戏规则**：确保你有使用 `/wsserver` 指令的权限，不要违反联机服务器的游戏规则。
- 本项目仅供学习和研究使用，作者不承担任何由于滥用API或违反游戏规则导致的责任。

---

## 如何贡献

欢迎为项目贡献代码：

1. Fork 仓库。
2. 创建新的特性分支 (`git checkout -b feature/fooBar`)。
3. 提交更改 (`git commit -am 'Add some fooBar'`)。
4. 推送至分支 (`git push origin feature/fooBar`)。
5. 提交 Pull Request。

---

## 许可证

[MIT](https://github.com/rice-awa/MCBE_WebSocket_gpt/blob/main/LICENSE.txt)

---

## 问题反馈

有问题？[联系我](https://space.bilibili.com/521856101)。

---

## 待办清单

- ~~[ ] 提供详细的安装和配置教程。~~
- [ ] 增加更多游戏内交互功能。
- [ ] 设计安全存储 API 密钥的方法。

---

## README.md 部分内容使用GPT4生成