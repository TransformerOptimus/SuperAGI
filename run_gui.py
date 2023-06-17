import os
import sys
import subprocess
from time import sleep
import shutil
from superagi.lib.logger import logger

def check_command(command, message):
    if not shutil.which(command):
        logger.info(message)
        sys.exit(1)

def run_npm_commands():
    os.chdir("gui")
    try:
        subprocess.run(["npm", "install"], check=True)
    except subprocess.CalledProcessError:
        logger.error(f"Error during '{' '.join(sys.exc_info()[1].cmd)}'. Exiting.")
        sys.exit(1)
    os.chdir("..")

def run_server():
    api_process = subprocess.Popen(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"])
    os.chdir("gui")
    ui_process = subprocess.Popen(["npm", "run", "dev"])
    os.chdir("..")
    return api_process, ui_process

def cleanup(api_process, ui_process):
    logger.info("Shutting down processes...")
    api_process.terminate()
    ui_process.terminate()
    logger.info("Processes terminated. Exiting.")
    sys.exit(1)

if __name__ == "__main__":
    check_command("node", "Node.js is not installed. Please install it and try again.")
    check_command("npm", "npm is not installed. Please install npm to proceed.")
    check_command("uvicorn", "uvicorn is not installed. Please install uvicorn to proceed.")

    run_npm_commands()

    try:
        api_process, ui_process = run_server()
        while True:
            try:
                sleep(30)
            except KeyboardInterrupt:
                cleanup(api_process, ui_process)
    except Exception as e:
        cleanup(api_process, ui_process)