#!/bin/bash

# 检查是否为root用户
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# 设置变量
SERVICE_NAME="daemon-wsfunction-call"
SCRIPT_PATH="$(pwd)/daemon.py"
PYTHON_PATH="/usr/bin/python3"
USER_NAME=$(whoami)
GROUP_NAME=$(id -gn $USER_NAME)
ENV_FILE="/etc/daemon-wsfunction-call.env"
API_URL=\$1
API_KEY=\$2
WEBSOCKET_PASSWORD=\YOUR_WEBSOCKET_PASSWORD
SECRET_KEY=\YOUR_SECRET_KEY


# 检查脚本路径是否存在
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Script file $SCRIPT_PATH does not exist."
    exit 1
fi

# 检查Python路径是否存在
if [ ! -f "$PYTHON_PATH" ]; then
    echo "Python interpreter $PYTHON_PATH does not exist."
    exit 1
fi

# 检查是否传入了API_URL、API_KEY、SECRET_KEY和WEBSOCKET_PASSWORD参数
if [ -z "\$1" ] || [ -z "\$2" ] || [ -z "\$3" ] || [ -z "\$4" ]; then
    echo "Usage: \$0 <API_URL> <API_KEY> <SECRET_KEY> <WEBSOCKET_PASSWORD>"
    exit 1
fi

# 停止并禁用现有服务
echo "Stopping and disabling existing $SERVICE_NAME service if it exists..."
systemctl stop $SERVICE_NAME 2>/dev/null
systemctl disable $SERVICE_NAME 2>/dev/null

# 删除现有的服务文件
if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
    echo "Removing existing service file..."
    rm /etc/systemd/system/$SERVICE_NAME.service
fi

# 重新加载Systemd守护进程以应用更改
echo "Reloading systemd daemon..."
systemctl daemon-reload

# 创建或更新环境变量文件
echo "Creating or updating $ENV_FILE..."
if grep -q "^API_URL=" $ENV_FILE; then
    sed -i "s|^API_URL=.*|API_URL=$API_URL|" $ENV_FILE
else
    echo "API_URL=$API_URL" >> $ENV_FILE
fi

if grep -q "^API_KEY=" $ENV_FILE; then
    sed -i "s|^API_KEY=.*|API_KEY=$API_KEY|" $ENV_FILE
else
    echo "API_KEY=$API_KEY" >> $ENV_FILE
fi

if grep -q "^SECRET_KEY=" $ENV_FILE; then
    sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|" $ENV_FILE
else
    echo "SECRET_KEY=$SECRET_KEY" >> $ENV_FILE
fi

if grep -q "^WEBSOCKET_PASSWORD=" $ENV_FILE; then
    sed -i "s|^WEBSOCKET_PASSWORD=.*|WEBSOCKET_PASSWORD=$WEBSOCKET_PASSWORD|" $ENV_FILE
else
    echo "WEBSOCKET_PASSWORD=$WEBSOCKET_PASSWORD" >> $ENV_FILE
fi

# 确认环境变量文件内容
echo "Environment file content:"
cat $ENV_FILE

# 创建Systemd服务文件
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

echo "Creating $SERVICE_FILE..."

cat <<EOL > $SERVICE_FILE
[Unit]
Description=My Python Daemon
After=network.target

[Service]
ExecStart=$PYTHON_PATH $SCRIPT_PATH
Restart=always
User=$USER_NAME
Group=$GROUP_NAME
EnvironmentFile=$ENV_FILE
Environment=PYTHONUNBUFFERED=1
WorkingDirectory=$(dirname $SCRIPT_PATH)
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOL

# 重新加载Systemd守护进程
echo "Reloading systemd daemon again..."
systemctl daemon-reload

# 启动并启用服务
echo "Starting and enabling $SERVICE_NAME service..."
systemctl start $SERVICE_NAME
systemctl enable $SERVICE_NAME

echo "Service $SERVICE_NAME has been set up and enabled to start on boot."
