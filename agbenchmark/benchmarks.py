import sys
import requests
import json
import time
import os

baseUrl = "http://localhost:3000/api"


def run_specific_agent(task: str) -> None:
    org_payload = {
        "name": "Test Org",
        "description": "Testing agents",
    }

    headers = {"Content-Type": "application/json"}

    org_response = requests.request(
        "POST",
        f"{baseUrl}/organisations/add",
        headers=headers,
        data=json.dumps(org_payload),
    )

    org_json = org_response.json()

    print("Org response", org_response.text)

    setup_payload = {
        "name": "Project1",
        "description": "Project Description!",
        "organisation_id": org_json["id"],
    }

    proj_response = requests.request(
        "POST",
        f"{baseUrl}/projects/add",
        headers=headers,
        data=json.dumps(setup_payload),
    )

    print("Org response", proj_response.text)

    proj_json = proj_response.json()

    # Call server to run SuperAgi
    payload = {
        "name": "Agent",
        "project_id": proj_json["id"],
        "description": "AI assistant to solve complex problems",
        "goal": [
            "Please fulfill the instructions you are given to the best of your ability. Make sure to output relevant information into the workspace."
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
        "toolkits": [],
        "tools": [
            1,
            7,
            8,
            9,
            10,
            11,
            19,
        ],  # CodingTool, Append File, Delete File, List File, Read File, Write File, GoogleSearch
        "exit": "Exit strategy",
        "iteration_interval": 500,
        "model": "gpt-3.5-turbo",
        "permission_type": "God Mode",
        "LTM_DB": "Pinecone",
        "memory_window": 10,
        "max_iterations": 100,
    }

    response = requests.request(
        "POST", f"{baseUrl}/agents/create", headers=headers, data=json.dumps(payload)
    )

    print(response.text)

    # parse the JSON response
    response_data = response.json()

    payload2 = {"status": "RUNNING"}
    response2 = requests.request(
        "PUT",
        f"{baseUrl}/agentexecutions/update/{response_data['execution_id']}",
        headers=headers,
        data=json.dumps(payload2),
    )
    print("Response 2", response2.text)

    with open("agbenchmark/config.json", "r") as f:
        config = json.load(f)

    # Update the output workspace path in the config
    config["workspace"]["output"] = os.path.join(
        "workspace/output", str(response_data["id"])
    )

    with open("agbenchmark/config.json", "w") as f:
        json.dump(config, f)

    # this prints the logs
    start_time = time.time()
    completed = False
    while True:
        # cutoff on the benchmark side, needs to be changed in actual implementation
        if time.time() - start_time > 20:  # TODO: config["cutoff"]
            break

        response = requests.get(
            f"{baseUrl}/agentexecutions/get/agent/{response_data['id']}"
        )
        print("Agent execution GET", response.text)

        # response = requests.get(
        #     f"{baseUrl}/agentexecutionfeeds/get/{response_data['execution_id']}"
        # )
        # print("Agent execution FEED:", response.text)

        # feed_json = response.json()

        # if feed_json["feed"] == "COMPLETE":
        #     completed = True
        #     break

        time.sleep(5)

    if not completed:
        payload3 = {"status": "TERMINATED"}
        response3 = requests.request(
            "PUT",
            f"{baseUrl}/agentexecutions/update/{response_data['execution_id']}",
            headers=headers,
            data=json.dumps(payload3),
        )
        print("Response 3", response3.text)
        print("Execution timed out and was paused")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <task>")
        sys.exit(1)
    task = sys.argv[1]
    run_specific_agent(task)
