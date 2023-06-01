import os
import sys
import subprocess
from time import sleep
import shutil
from sys import platform
from multiprocessing import Process


def check_command(command, message):
    if not shutil.which(command):
        print(message)
        sys.exit(1)


def run_npm_commands(shell=False):
    os.chdir("gui")
    try:
        subprocess.run(["npm", "install"], check=True, shell=shell)
    except subprocess.CalledProcessError:
        print(f"Error during '{' '.join(sys.exc_info()[1].cmd)}'. Exiting.")
        sys.exit(1)
    os.chdir("..")


def run_server(shell=False,a_name=None,a_description=None,goals=None):
    api_process = Process(target=subprocess.run, args=(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],), kwargs={"shell": shell})
    celery_process = Process(target=subprocess.run, args=(["celery", "-A", "celery_app", "worker", "--loglevel=info"],), kwargs={"shell": shell})
    ui_process = Process(target=subprocess.run, args=(["python", "test.py","--name",a_name,"--description",a_description,"--goals"]+goals,), kwargs={"shell": shell})

    api_process.start()
    celery_process.start()
    ui_process.start()

    return api_process, ui_process, celery_process


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

    agent_name = input("Enter an agent name: ")
    agent_description = input("Enter an agent description: ")
    goals = []
    while True:
        goal = input("Enter a goal (or 'q' to quit): ")
        if goal == 'q':
            break
        goals.append(goal)
    isWindows = False
    if platform == "win32" or platform == "cygwin":
        isWindows = True
    run_npm_commands(shell=isWindows)

    try:
        api_process, ui_process, celery_process = run_server(isWindows, agent_name, agent_description, goals)
        while True:
            try:
                sleep(30)
            except KeyboardInterrupt:
                cleanup(api_process, ui_process, celery_process)
    except Exception as e:
        cleanup(api_process, ui_process, celery_process)