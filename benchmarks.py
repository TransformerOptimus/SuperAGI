import sys
import requests
import json


baseUrl = "http://localhost:3000/api"


def run_specific_agent(task: str) -> None:
    # Call server to run SuperAgi
    payload = {
        "name": "Agent",
        "project_id": 1,
        "description": "AI assistant to solve complex problems",
        "goal": [
            "Please fulfill the task you are given to the best of your ability. Make sure to output relevant information into the workspace."
        ],
        "instruction": [f"{task}"],
        "agent_type": "Don't Maintain Task Queue",
        "constraints": [
            "~4000 word limit for short term memory.",
            "Your short term memory is short, so immediately save important information to files.",
            "If you are unsure how you previously did something or want to recall past events, thinking about similar events will help you remember.",
            "No user assistance",
            'Exclusively use the commands listed in double quotes e.g. "command name"',
        ],
        "toolkits": [95, 96],
        "tools": [],
        "exit": "Exit strategy",
        "iteration_interval": 500,
        "model": "gpt-3.5-turbo",
        "permission_type": "Type 1",
        "LTM_DB": "Database Pinecone",
        "memory_window": 10,
        "max_iterations": 1,
    }

    headers = {"Content-Type": "application/json"}

    response = requests.request(
        "POST", f"{baseUrl}/agents/create", headers=headers, data=json.dumps(payload)
    )

    print(response.text)

    # parse the JSON response
    response_data = response.json()

    payload2 = {"agent_id": response_data["id"], "name": response_data["name"]}

    response2 = requests.request(
        "POST",
        f"{baseUrl}/agentexecutions/add",
        headers=headers,
        data=json.dumps(payload2),
    )

    print(response2.text)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <task>")
        sys.exit(1)
    task = sys.argv[1]
    run_specific_agent(task)
