import sys
import requests
import json
import time
import os

baseUrl = "http://localhost:3000/api"


def run_specific_agent(task: str) -> None:
    # create and start the agent here and dynamically pass in the task
    # must have File Toolkit, Search Toolkit minimum

    headers = {"Content-Type": "application/json"}

    payload = {
        'status': 'Running',
        'name': 'agent',
        'project_id': 1,
        'description': 'AI assistant to solve complex problems',
        'goal': [
            f"{task}"
        ],
        'instruction': ['Please fulfill the goals you are given to the best of your ability. Make sure to output relevant information into the workspace.'],
        'agent_workflow': 'Goal Based Workflow',
        'constraints': [
            "~4000 word limit for short term memory.",
            "Your short term memory is short, so immediately save important information to files.",
            "If you are unsure how you previously did something or want to recall past events, thinking about similar events will help you remember.",
            "No user assistance",
            'Exclusively use the commands listed in double quotes e.g. "command name"',
        ],
        'toolkits': [],
        'tools': [
            1,
            21,
            22,
            25
        ],
        'exit': 'No exit criterion',
        'iteration_interval': 500,
        'model': 'gpt-3.5-turbo-16k',
        'max_iterations': 25,
        'permission_type': 'God Mode',
        'LTM_DB': 'Pinecone',
        'user_timezone': 'Asia/Kolkata',
        'knowledge': None,
    }

    response = requests.request(
        "POST", f"{baseUrl}/agents/create", headers=headers, data=json.dumps(payload)
    )

    agent_execution_id = response.json()['execution_id']
    _ = requests.request(
        "PUT", f"{baseUrl}/agentexecutions/update/{agent_execution_id}", headers=headers,
        data=json.dumps({'status': 'RUNNING'}))

    with open("agbenchmark/config.json", "r") as f:
        config = json.load(f)

    # Update the output workspace path depending on agentexecution and agentid
    print(response.json(), 'response')
    response = response.json()
    output_path = f"workspace/output/"
    input_path = f"workspace/input/"
    config["workspace"]["output"] = output_path
    config["workspace"]["input"] = input_path
    # config["workspace"]["output"] = os.path.join(
    #     "workspace","output", f"{response['id']}", f"{response['execution_id']}")
    #
    # config["workspace"]["input"] = os.path.join(
    #     "workspace","input", f"{response['id']}", f"{response['execution_id']}")

    with open("agbenchmark/config.json", "w") as f:
        json.dump(config, f)

    # agent execution stream

    # add manual timeout of 120 seconds
    start_time = time.time()
    pause_payload = {"status": "PAUSED"}
    while True:
        agent_stream = requests.request(
            "GET", f"{baseUrl}/agentexecutionfeeds/get/execution/{response['id']}", headers=headers
        )

        if time.time() - start_time > 60:
            response = requests.request(
                "PUT", f"{baseUrl}/agentexecutions/update/{response['execution_id']}", headers=headers,
                data=json.dumps(pause_payload)
            )
            break
        time.sleep(5)

    # terminate the agent


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <task>")
        sys.exit(1)
    task = sys.argv[1]
    print(sys.argv)
    run_specific_agent(task)
