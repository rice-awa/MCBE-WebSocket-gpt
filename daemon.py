import time
import subprocess
import signal
import sys
import psutil
import os

# 监控的Python脚本
script_to_run = 'main_server.py'
process = None

def is_running(script_name):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and script_name in cmdline:
                print(f"Found running process: {cmdline}")
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def start_script(script_name):
    global process
    # 使用subprocess.Popen启动脚本
    process = subprocess.Popen(['python3', script_name], stdout=open('output.log', 'a'), stderr=open('error.log', 'a'))

def stop_script():
    global process
    if process:
        process.terminate()
        process.wait()
        process = None

def signal_handler(sig, frame):
    print('Stopping daemon...')
    stop_script()
    sys.exit(0)

def main():
    script_path = os.path.join(os.getcwd(), script_to_run)
    if not os.path.isfile(script_path):
        print(f"Error: {script_to_run} not found in the current directory.")
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)  # 捕获Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # 捕获终止信号

    while True:
        if not is_running(script_to_run):
            print(f"{script_to_run} is not running. Starting it...")
            start_script(script_to_run)
        else:
            print(f"{script_to_run} is running.")
        time.sleep(10)  # 每10秒检查一次

if __name__ == '__main__':
    main()
