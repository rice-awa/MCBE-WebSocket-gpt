# MCBE Websocket Server In-game GPT Usage

[简体中文](./README.md)

This project provides a Python-based WebSocket service for Minecraft Bedrock Edition (**_MCBE_**) servers. It can capture players' **chat messages**, call the GPT API to enable **chatGPT** usage in-game, and ultimately send the GPT responses back to the game. The project uses asynchronous programming with aiohttp and Websockets.

---

## Updates

**2024/7/31** (New)

- 1.Added authentication feature
- 2.Added process monitoring functionality

**2024/7/6**

- 1.Changed API calls to non-streaming transmission
- 2.Simplified code logic in `gptapi.py`
- 3.Replaced expired third-party API key

**Table of Contents**

- [Features](#features)
- [Quick Start](#quick-start)
- [Configuration Guide](#configuration-guide)
- [Usage Instructions](#usage-instructions)
- [Notes](#notes)
- [How to Contribute](#how-to-contribute)
- [License Information](#license-information)
- [Feedback](#feedback)
- [To-Do List](#to-do-list)

---

## Features

- **Capture Player Messages**: Real-time acquisition of players' chat messages in the game.
- **GPT Response Generation**: Generate reply content through the GPT API.
- **Game Display**: Send GPT-generated responses directly to MCBE.
- **Context Support**: Enable conversation history by setting `enable_history` to `True`.
- **Multiple Connection Support**: Each connection is an instance, allowing multiple instances to connect simultaneously. Note: Only supported for servers (main_server), not effective for local testing (main_local).
- **Authentication**: Supports login verification to prevent API abuse.
- **Process Monitoring**: Implements process monitoring and automatic restart using daemon.py.

---

## Quick Start

Ensure that your environment has Python 3.8+ installed.

1. **Clone the project**:

   ```bash
   git clone https://github.com/rice-awa/MCBE_WebSocket_gpt.git
   cd MCBE_WebSocket_gpt
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **\*Configure environment variables**
   Please refer to the [Configuration Guide](#configuration-guide).

4. **Run the WebSocket server**:
   - Local testing
     Modify `api_url` and `api_key` in `main_local.py`, then run:
     ```bash
     python main_local.py
     ```
   - Server operation (**If using Linux, process monitoring (daemon.py) is included**)
     Use the provided script to set up the service:
     ```bash
     chmod +x setup_service.sh
     sudo ./setup_service.sh <API_URL> <API_KEY>
     ```
     This will set up a system service that starts automatically and can be used even after server restarts.

---

## Configuration Guide

- **API Settings**:

  - Local testing: Set `api_url` and `api_key` in `main_local.py`.
  - Server: Use the `setup_service.sh` script to set environment variables.
  - It's recommended to use a third-party forwarded key. We recommend using this [apikey](https://burn.hair/). Of course, official APIKEYs also work.

- **Authentication**:
  Set environment variables `WEBSOCKET_PASSWORD` and `SECRET_KEY`. The default password is "123456".

- **Server Settings**:
  Modify the `ip` and `port` parameters. Servers need to keep `ip` as "0.0.0.0".

---

## Usage Instructions

1. **Start the server**:
   Follow the instructions in the Quick Start section to run the server.

2. **Connect to the server**:
   In the Minecraft chat box, enter `/wsserver <server ip>:<server port>`.
   ![wsserver](https://s11.ax1x.com/2024/02/13/pF8y0dU.png)

3. **Log in**:
   Use `#登录 <password>` for authentication.
   ![Login verification](https://s3.bmp.ovh/imgs/2024/07/31/82bdff9f34ad14d6.png)

4. **Use chat commands**:
   Chat input `GPT 聊天 {content}` to converse with GPT. Note that each parameter needs to be separated by a space.
   ![GPT chat](https://s11.ax1x.com/2024/02/13/pF8yRL6.png)
   GPT replies are in green text.

   - `GPT 上下文 <status/enable/disable>`: Manage context
   - `GPT 脚本 <content>`: Use script events to send data
   - `运行命令 <command>`: Execute game commands

5. **Save conversations**:
   - Enter `GPT 保存` to save the conversation. Note that there should be no space after "保存"
   - After saving and closing the session, conversation records and logs will be generated in the root directory.
     ![Conversation log](https://s11.ax1x.com/2024/02/13/pF8yXef.png)

---

## Notes

- Protect API keys and authentication information.
- Use the API legally and comply with relevant terms and game rules.
- This project is for learning and research purposes only.

---

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

---

## License

[MIT](https://github.com/rice-awa/MCBE_WebSocket_gpt/blob/main/LICENSE.txt)

---

## Feedback

Got questions? [Contact me](https://space.bilibili.com/521856101).

---

## To-Do List

- [x] Provide detailed installation and configuration tutorials
- [x] Add authentication feature
- [x] Implement process monitoring
- [ ] Add more in-game interaction features
- [ ] Optimize secure storage method for API keys

---

**Thanks for using!**
