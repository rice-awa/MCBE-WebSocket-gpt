# MCBE Websocket Server with In-Game GPT Usage
[中文](./README_ZH.md)

This project provides a Python-based WebSocket service for the Minecraft Bedrock Edition (***MCBE***) server, which captures players' **chat messages**, calls the GPT API to enable in-game use of **chatGPT**, and ultimately sends the GPT's responses back into the game. The project utilizes `aiohttp` and `Websockets` asynchronously.

---

**Table of Contents**

- [Features](#features)
- [Quick Start](#quick-start)
- [Configuration Guide](#configuration-guide)
- [Usage Instructions](#usage-instructions)
- [Precautions](#precautions)
- [How to Contribute](#how-to-contribute)
- [License](#license)
- [Feedback](#feedback)
- [To-Do List](#to-do-list)

---

## Features

- **Capture Player Messages**: Real-time retrieval of player chat messages in-game.
- **GPT Reply Generation**: Generate reply content through the GPT API.
- **In-Game Display**: Send the GPT-generated replies directly into MCBE.
- **Context Support**: Enable session history recording by setting `enable_history` to `True`.

---

## Quick Start

Make sure your environment has Python 3.7+, `websockets`, and `aiohttp` installed.

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/rice-awa/MCBE_WebSocket_gpt.git
    cd MCBE_WebSocket_gpt
    ```

2. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

    Or install separately:

    ```bash
    pip install aiohttp
    pip install websockets
    ```

---

## Configuration Guide

- **Set the API Key**:

  Locate `api_url` and `api_key` in the `Websocket.py` file and fill in your GPT API information.

  It is recommended to use a third-party forwarding key, such as this [free apikey](https://gpt-houtar.koyeb.app). Of course, the official APIKEY can also be used.

- **Server Settings**:

  Modify the `ip` and `port` parameters according to your server configuration.
  
  Enable `enable_history` to control whether to record session context.

---

## Usage Instructions

1. **Start the WebSocket Server**:

    ```bash
    python Websocket.py
    ```

2. **Connect to the Server**:

    Enter `/wsserver localhost:8080` in the Minecraft chat box.

    ![wsserver](https://s11.ax1x.com/2024/02/13/pF8y0dU.png)

3. **Use Chat Commands**:

    In chat, type `GPT chat {content}` to converse with GPT. Note that each argument should be separated by a space.

    ![GPT Chat](https://s11.ax1x.com/2024/02/13/pF8yRL6.png)

    GPT replies will be in green text.

4. **Save Conversations**:
    - Type `GPT save` to save the conversation. Note that there should be no space after "save".
    - After saving and closing the session, conversation logs and records will be generated in the root directory.

    ![Conversation Log](https://s11.ax1x.com/2024/02/13/pF8yXef.png)

5. **Context**
    - `GPT context` to check the current context status.
    - `GPT context enable` to enable GPT context.
    - `GPT context disable` to disable GPT context.

---

## Precautions

- **Protect Your API Key**: Do not write your API key directly in **public code repositories**. Use environment variables or other secure methods.
- **Legal Use of the API**: Ensure you have the right to use the GPT API and comply with the terms. Do not abuse the API.
- **Follow Game Rules**: Make sure you have permission to use the `/wsserver` command and do not violate the rules of online servers.
- This project is for educational and research purposes only, the author assumes no responsibility for any misuse of the API or violation of game rules.

---

## How to Contribute

Contributions to the project are welcome:

1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature/fooBar`).
3. Commit your changes (`git commit -am 'Add some fooBar'`).
4. Push to the branch (`git push origin feature/fooBar`).
5. Create a Pull Request.

---

## License

[MIT](https://github.com/rice-awa/MCBE_WebSocket_gpt/blob/main/LICENSE.txt)

---

## Contact me

Have any questions? [Contact me](https://space.bilibili.com/521856101).

---

## To-Do List

- [ ] Provide detailed installation and configuration tutorials.
- [ ] Add more in-game interaction features.
- [ ] Design a secure method to store API keys.

---

## Portions of the README.md content were generated with GPT-4
