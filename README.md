# MCBE Websocket Server 游戏内使用 GPT

[English](./README_EN.md)

这个项目提供了一个基于 Python 的 Minecraft Bedrock Edition (**_MCBE_**) 服务器端的 WebSocket 服务，它可以获取玩家的**聊天信息**，并调用 GPT API 实现在游戏内使用**chatGPT**，最终将 GPT 回复传回到游戏中。项目使用 aiohttp 和 Websockets 异步。

~~如果你问我就一个小项目，自述文件写那么多干嘛？我闲的（~~

---

## 更新

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
- **支持多个连接**: 每个连接为一个实例，可以多个实例同时连接。注：仅支持服务器(main_server)，本地测试(main_local)无效
- **支持登录验证，防止 api 被滥用** 请设置环境变量`WEBSOCKET_PASSWORD`和`WEBSOCKET_PASSWORD_HASH`，默认为`123456`和`123456`，请自行修改

---

## 快速开始

确保你的环境已安装 Python 3.8+，`websockets` 和 `aiohttp`。
如需配置服务器确保你的环境已安装`PyJwt` 和 `psutil`

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
   pip install psutil
   pip install PyJWT
   ```

3. **运行 WebSocket 服务器**：

   - 本地测试
     先修改好
     `main_local.py`中的`api_url`和`api_key`，然后运行

   ```bash
   python main_local.py
   ```

   - 服务器运行
     **如果使用 Linux，自带进程守护(daemon.py)**

   1. 在脚本的变量中配置好环境变量
      `API_KEY`和`API_URL`

      请参考 [配置指南](#配置指南)。

   2. 给予脚本权限

   ```bash
   chmod +x setup_service.sh
   ```

   3. 运行脚本

   ```bash
   sudo ./setup_service.sh.
   ```

---

## 配置指南

- **设置 API 密钥**：

- 本地测试

  在 `main_local.py` 文件中找到 `api_url` 和 `api_key`，并填入你的 GPT API 信息。

这里推荐使用第三方转发 key，推荐使用这个 [apikey](https://burn.hair/) 当然官方 APIKEY 也可以。

- **环境变量**
  直接在 bash 脚本`setup_service.sh.`中配置`API_KEY`和`API_URL`变量(仅适用于 Linux)

  或手动设置服务器设置环境变量

  ```bash
  export API_URL=" < API_URL >"
  export API_KEY="< API_KET>"
  ```

  例如

  ```bash
  export API_URL="https://api.openai.com/v1/chat/completions"
  export API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  ```

- **服务器设置**：

  根据你的需求，修改 `ip` 和 `port` 参数。 **配置服务器需保持 ip 为 0.0.0.0**

  启用 `enable_history` 来控制是否记录会话上下文。

---

## 使用说明

1. **启动 WebSocket 服务器**：

   ```bash
   python main_local.py
   ```

   或者在服务器上运行

   ```bash
   sudo ./setup_service.sh
   ```

2. **连接服务器**：

   在 Minecraft 聊天框输入 `/wsserver localhost:8080`。

   如果是服务器请输入
   `/wsserver <服务器ip>:<服务器端口>`。

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
   - `GPT 上下文 状态` 查看当前上下文状态
   - `GPT 上下文 启用` 开启 GPT 上下文
   - `GPT 上下文 关闭` 关闭 GPT 上下文

---

## 注意事项

- **保护你的 API 密钥**：不要在**公共代码库中直接编写你的 API 密钥**，可以使用环境变量或其他安全方法。
- **合法使用 API**：确保你有权使用 GPT API 并遵守相关条款。不要滥用 API。
- **遵守游戏规则**：确保你有使用 `/wsserver` 指令的权限，不要违反联机服务器的游戏规则。
- 本项目仅供学习和研究使用，作者不承担任何由于滥用 API 或违反游戏规则导致的责任。
- 在中国大陆，请遵守[《生成式人工智能服务管理暂行办法》](https://www.gov.cn/zhengce/202311/content_6917778.htm)

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

**感谢使用！**
