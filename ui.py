import os
import sys
import subprocess
from time import sleep
import shutil
from sys import platform


def check_command(command, message):
    if not shutil.which(command):
        print(message)
        sys.exit(1)


def run_npm_commands(shell=False):
    os.chdir("gui")
    try:
        subprocess.run(["npm", "install"], check=True,shell=shell)
    except subprocess.CalledProcessError:
        print(f"Error during '{' '.join(sys.exc_info()[1].cmd)}'. Exiting.")
        sys.exit(1)
    os.chdir("..")


def run_server(shell=False):
    api_process = subprocess.Popen(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"], shell=shell)
    # celery_process = None
    celery_process = subprocess.Popen(["celery", "-A", "superagi.worker", "worker", "--loglevel=info"], shell=shell)
    os.chdir("gui")
    ui_process = subprocess.Popen(["npm", "run", "dev"], shell=shell)
    os.chdir("..")
    return api_process, ui_process , celery_process


def cleanup(api_process, ui_process, celery_process):
    print("Shutting down processes...")
    api_process.terminate()
    ui_process.terminate()
    celery_process.terminate()
    print("Processes terminated. Exiting.")
    sys.exit(1)


if __name__ == "__main__":
    check_command("node", "Node.js is not installed. Please install it and try again.")
    check_command("npm", "npm is not installed. Please install npm to proceed.")
    check_command("uvicorn", "uvicorn is not installed. Please install uvicorn to proceed.")

    isWindows = False
    if platform == "win32" or platform == "cygwin":
        isWindows = True
    run_npm_commands(shell=isWindows)

    try:
        api_process, ui_process, celery_process = run_server(isWindows)
        while True:
            try:
                sleep(30)
            except KeyboardInterrupt:
                cleanup(api_process, ui_process, celery_process)
    except Exception as e:
        cleanup(api_process, ui_process, celery_process)