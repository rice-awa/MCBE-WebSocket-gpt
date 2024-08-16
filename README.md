# MCBE Websocket Server 游戏内使用 GPT

## 本页面为 function-call 版本

[English](./README_EN.md)

这个项目提供了一个基于 Python 的 Minecraft Bedrock Edition (**_MCBE_**) 服务器端的 WebSocket 服务，它可以获取玩家的**聊天信息**，并调用 GPT API 实现在游戏内使用**chatGPT**，最终将 GPT 回复传回到游戏中。项目使用 aiohttp 和 Websockets 异步。

在这里可以看到函数描述文档：[函数描述文档](https://blog.rice-awa.top/blog/MCBE-websockets_doc)

---

## 更新

**2024/8/2** (新增)

- 1.新增 function-call 功能(见 function-call 分支)
- 2.循环获取游戏数据，可能会导致服务器卡顿
- 3.function-call 功能需要服务器端支持，目前仅支持服务器端
- 4.function-call 不支持关闭上下文，请手动保存关闭(断开连接也会关闭)

**2024/7/31** (新增)

- 1.添加了身份验证功能
- 2.增加了进程守护功能

**2024/7/6**

- 1.将 api 调用改为非流式传输
- 2.简化了`gptapi.py`的代码逻辑
- 3.更换过期第三方 apikey

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
- **GPT 回复生成**：通过 GPT API 生成回复内容。
- **游戏显示**：将 GPT 生成的回复直接发送至 MCBE 中。
- **支持上下文**：通过设置 `enable_history` 为 `True` 来启用会话历史记录。
- **支持多个连接**: 每个连接为一个实例，可以多个实例同时连接。
- **身份验证**：支持登录验证，防止 API 被滥用。
- **进程守护**：使用 daemon.py 实现进程监控和自动重启。

---

## 快速开始

确保你的环境已安装 Python 3.8+。

1. **克隆项目**：

   ```bash
   git clone -b function-call https://github.com/rice-awa/MCBE_WebSocket_gpt.git
   cd MCBE_WebSocket_gpt
   ```

2. **安装依赖**：

   ```bash
   pip install -r requirements.txt
   ```

3. **\*配置环境变量**

   请参考 [配置指南](#配置指南)。

4. **运行 WebSocket 服务器**：

   - 本地测试
     修改 `main_server.py` 中的 `api_url` 和 `api_key`默认值，然后运行：

     ```bash
     python main_server.py
     ```

   - 服务器运行(**如果使用 Linux，自带进程守护(daemon.py)**)
     使用提供的脚本设置服务：

     ```bash
     chmod +x setup_service.sh
     sudo ./setup_service.sh <API_URL> <API_KEY>
     ```

     这将设置一个系统服务，自动启动并在重启服务器后也可以使用。

---

## 配置指南

- **API 设置**：

  - 本地测试：设置 `api_url` 和 `api_key`

    根据需要 修改 `ip` 和 `port` 参数。

  - 服务器：使用 `setup_service.sh` 脚本设置环境变量`API_URL` 和 `API_KEY`。注意：需要把`$`删掉，替换`\`后面的值即可
  - 这里推荐使用第三方转发 key，推荐使用这个 [apikey](https://burn.hair/) 当然官方 APIKEY 也可以。

- **身份验证**：
  设置环境变量 `WEBSOCKET_PASSWORD` 和 `SECRET_KEY`。默认密码为 "123456"。

- **服务器设置**：
  修改 `ip` 和 `port` 参数。服务器需保持 `ip` 为 "0.0.0.0"。

---

## 使用说明

1. **启动服务器**：
   按照快速开始中的说明运行服务器。

2. **连接服务器**：
   在 Minecraft 聊天框输入 `/wsserver <服务器ip>:<服务器端口>`。
   ![wsserver](https://s11.ax1x.com/2024/02/13/pF8y0dU.png)
3. **登录**：
   使用 `#登录 <密码>` 进行身份验证(默认 123456)。
   ![登录验证](https://s3.bmp.ovh/imgs/2024/07/31/82bdff9f34ad14d6.png)

4. **使用聊天命令**：
   聊天输入 `GPT 聊天 {内容}` 与 GPT 对话。这里注意每个参数需要空格隔开

   ![GPT聊天](https://s11.ax1x.com/2024/02/13/pF8yRL6.png)

   GPT 回复为绿色字体。

   - `GPT 上下文 <状态/启用/关闭>`: 管理上下文
   - `GPT 脚本 <内容>`: 使用脚本事件发送数据
   - `运行命令 <命令>`: 执行游戏命令

5. **保存对话**：

   - 输入`GPT 保存`来保存对话。
   - 保存和关闭会话后，会在根目录生成对话记录和日志。

   ![对话日志](https://s11.ax1x.com/2024/02/13/pF8yXef.png)

---

## 注意事项

- 保护 API 密钥和身份验证信息。
- 合法使用 API，遵守相关条款和游戏规则。
- 本项目仅供学习和研究使用。

---

## 如何贡献

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/fooBar`)
3. 提交更改 (`git commit -am 'Add some fooBar'`)
4. 推送至分支 (`git push origin feature/fooBar`)
5. 创建新的 Pull Request

---

## 许可证

[MIT](https://github.com/rice-awa/MCBE_WebSocket_gpt/blob/main/LICENSE.txt)

---

## 问题反馈

有问题？[联系我](https://space.bilibili.com/521856101)。

---

## 待办清单

- [x] 提供详细的安装和配置教程
- [x] 增加身份验证功能
- [x] 实现进程守护
- [x] 增加更多游戏内交互功能
- [ ] 优化 API 密钥的安全存储方法

---

**感谢使用！**
