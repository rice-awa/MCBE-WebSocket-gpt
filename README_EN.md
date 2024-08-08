# MCBE WebSocket Server: Using GPT in Minecraft

## This Page is for the Function-Call Version

[简体中文](./README.md)

This project provides a Python-based WebSocket service for the Minecraft Bedrock Edition (**_MCBE_**) server. It can capture players' **chat messages** and call the GPT API to use **chatGPT** within the game, ultimately sending GPT replies back to the game. The project uses asynchronous aiohttp and Websockets.

---

## Updates

**2024/8/2** (New)

- 1. Added function-call feature (see the function-call branch)
- 2. Looping to fetch game data may cause server lag
- 3. The function-call feature requires server-side support, currently only supported on the server side; local testing (main_local) is ineffective
- 4. Function-call does not support closing context automatically; please save and close manually (disconnecting will also close)

**2024/7/31** (New)

- 1. Added authentication feature
- 2. Added process daemon feature

**2024/7/6**

- 1. Changed API calls to non-streaming
- 2. Simplified the code logic in `gptapi.py`
- 3. Replaced expired third-party API key

**Contents**

- [Features](#features)
- [Quick Start](#quick-start)
- [Configuration Guide](#configuration-guide)
- [Usage Instructions](#usage-instructions)
- [Notes](#notes)
- [How to Contribute](#how-to-contribute)
- [License](#license)
- [Feedback](#feedback)
- [To-Do List](#to-do-list)

---

## Features

- **Capture Player Messages**: Real-time capture of players' chat messages in the game.
- **GPT Reply Generation**: Generate reply content using the GPT API.
- **In-Game Display**: Send GPT-generated replies directly to MCBE.
- **Context Support**: Enable conversation history by setting `enable_history` to `True`.
- **Multiple Connections**: Each connection is an instance, allowing multiple instances to connect simultaneously. Note: Only supported on the server (main_server); local testing (main_local) is ineffective.
- **Authentication**: Support for login authentication to prevent API misuse.
- **Process Daemon**: Use daemon.py for process monitoring and automatic restart.

---

## Quick Start

Ensure your environment has Python 3.8+ installed.

1. **Clone the project**:

   ```bash
   git clone https://github.com/rice-awa/MCBE_WebSocket_gpt.git
   cd MCBE_WebSocket_gpt
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:

   Refer to the [Configuration Guide](#configuration-guide).

4. **Run the WebSocket server**:

   - Local testing:
     Modify `main_local.py` to set `api_url` and `api_key`, then run:

     ```bash
     python main_local.py
     ```

   - Server operation (**If using Linux, includes process daemon (daemon.py)**):
     Use the provided script to set up the service:

     ```bash
     chmod +x setup_service.sh
     sudo ./setup_service.sh <API_URL> <API_KEY>
     ```

     This will set up a system service that automatically starts and can be used after server reboots.

---

## Configuration Guide

- **API Settings**:

  - Local testing: Set `api_url` and `api_key` in `main_local.py`.
  - Server: Use `setup_service.sh` script to set environment variables `API_URL` and `API_KEY`. Note: Remove the backticks and replace the values accordingly.
  - It is recommended to use a third-party key forwarding service, such as this [apikey](https://burn.hair/). Official API keys are also supported.

- **Authentication**:
  Set environment variables `WEBSOCKET_PASSWORD` and `SECRET_KEY`. The default password is "123456".

- **Server Settings**:
  Modify the `ip` and `port` parameters. The server should keep `ip` as "0.0.0.0".

---

## Usage Instructions

1. **Start the server**:
   Follow the instructions in the Quick Start section to run the server.

2. **Connect to the server**:
   Enter `/wsserver <server_ip>:<server_port>` in the Minecraft chat box.
   ![wsserver](https://s11.ax1x.com/2024/02/13/pF8y0dU.png)

3. **Login**:
   Use `#login <password>` to authenticate (default is 123456).
   ![Login Authentication](https://s3.bmp.ovh/imgs/2024/07/31/82bdff9f34ad14d6.png)

4. **Use chat commands**:
   Enter `GPT chat {content}` to converse with GPT. Note that each parameter should be separated by spaces.

   ![GPT Chat](https://s11.ax1x.com/2024/02/13/pF8yRL6.png)

   GPT replies will be displayed in green text.

   - `GPT context <status/enable/disable>`: Manage context
   - `GPT script <content>`: Send data using script events
   - `run command <command>`: Execute game commands

5. **Save conversations**:

   - Enter `GPT save` to save the conversation.
   - After saving and closing the session, conversation logs and records will be generated in the root directory.

   ![Conversation Logs](https://s11.ax1x.com/2024/02/13/pF8yXef.png)

---

## Notes

- Protect your API key and authentication information.
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

Have questions? [Contact me](https://space.bilibili.com/521856101).

---

## To-Do List

- [x] Provide detailed installation and configuration tutorials
- [x] Add authentication feature
- [x] Implement process daemon
- [ ] Add more in-game interaction features
- [ ] Optimize API key security storage methods

---

**Thank you for using!**
