import json
import os
import sys
import time
import requests
import yaml
from superagi.lib.logger import logger

baseUrl = "http://localhost:3000/api"


def create_endpoint(
    endpoint, method="GET", data=None, headers=None, exit_on_error=True
):
    response = requests.request(
        method, f"{baseUrl}{endpoint}", data=data, headers=headers
    )
    logger.info(response.json())
    if response.status_code not in [200, 201] and exit_on_error:
        logger.info(f"Error connecting to API endpoint: {baseUrl}{endpoint}")
        sys.exit(1)
    return response.json()


class SuperAgiKey:
    def __init__(self, config_data):
        self.api_key = config_data.get(
            "SUPERAGI_API_KEY", os.getenv("SUPERAGI_API_KEY")
        )
        self.config_data = config_data
        self.headers = {"Content-Type": "application/json"}

    def create_key(self, name="Test API KEY"):
        self.api_key = create_endpoint(
            "/api-keys", "POST", data=json.dumps({"name": name}), headers=self.headers
        )["api_key"]

    def update_config(self):
        with open("config.yaml", "w") as file:
            yaml.dump(self.config_data, file)

    def check_or_create_data(self, endpoint, data):
        response = create_endpoint(
            endpoint + "/get/1", headers=self.headers, exit_on_error=False
        )
        if response.get("id", None) is None:
            response = create_endpoint(
                endpoint + "/add",
                "POST",
                headers=self.headers,
                data=json.dumps(data),
                exit_on_error=False,
            )
            if response.get("id", None) is None:
                logger.info(f"Error creating {endpoint.split('/')[-1]}")
                sys.exit(1)

    def setup(self):
        if self.api_key is None:
            self.check_or_create_data(
                "/organisations",
                {"name": "Test Organization", "description": "Test Organization"},
            )
            self.check_or_create_data(
                "/users",
                {
                    "name": "Test User",
                    "email": "super6@agi.com",
                    "password": "dummypass",
                    "organisation_id": 1,
                },
            )
            self.check_or_create_data(
                "/projects",
                {
                    "name": "Test Project",
                    "description": "Test Project",
                    "organization_id": 1,
                },
            )
            self.create_key()

            self.config_data["SUPERAGI_API_KEY"] = self.api_key

        create_endpoint(
            "/validate-llm-api-key",
            "POST",
            json.dumps(
                {
                    "model_source": "OpenAI",
                    "model_api_key": self.config_data["OPENAI_API_KEY"],
                }
            ),
            headers=self.headers,
        )
        create_endpoint(
            "/models_controller/store_api_keys",
            "POST",
            json.dumps(
                {
                    "model_provider": "OpenAI",
                    "model_api_key": self.config_data["OPENAI_API_KEY"],
                }
            ),
            headers=self.headers,
        )
        with open("config.yaml", "w") as file:
            yaml.dump(self.config_data, file)

        return self.api_key


class Agent:
    def __init__(self, superagi_api_key):
        self.superagi_api_key = superagi_api_key
        self.tools = [
            {"name": "File Toolkit", "tools": ["Read File", "Write File"]},
            {"name": "Google SERP Toolkit", "tools": ["GoogleSerp"]},
            {"name": "Web Scrapper Toolkit", "tools": ["WebScraperTool"]},
            {"name": "CodingToolkit", "tools": ["RunCodeTool"]},
        ]

    def create_agent(self, task):
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.superagi_api_key,
        }
        payload = {
            "name": f"{task[:20]}",
            "description": "AI assistant to solve complex problems",
            "goal": [f"{task}"],
            "agent_workflow": "Goal Based Workflow",
            "instruction": [
                "Please fulfill the goals you are given to the best of your ability. Sometimes complete instruction could be given in a file .",
                "Avoid redundancy, such as unnecessary immediate verification of actions.",
                "DO NOT modify the test.py file",
                "If file/funtion names are given strictly follow them",
            ],
            "constraints": [
                "If you are unsure how you previously did something or want to recall past events, thinking about similar events will help you remember.",
                "Ensure the tool and args are as per current plan and reasoning",
                "Exclusively use the tools listed under 'TOOLS'",
                "REMEMBER to format your response as JSON, using double quotes ("
                ") around keys and string values, and commas (,) to separate items in arrays and objects. IMPORTANTLY, to use a JSON object as a string in another JSON object, you need to escape the double quotes.",
            ],
            "tools": self.tools,
            "exit": "No exit criterion",
            "iteration_interval": 0,
            "model": "gpt-4",
            "max_iterations": 25,
        }
        response = create_endpoint(
            "/v1/agent", "POST", data=json.dumps(payload), headers=headers
        )
        self.agent_id = response["agent_id"]
        response = create_endpoint(
            f"/v1/agent/{self.agent_id}/run",
            "POST",
            data=json.dumps({}),
            headers=headers,
        )
        return response

    def check_time(self, start_time, current_time, limit=300):
        if current_time - start_time > limit:
            payload = {"status": "PAUSED"}
            response = create_endpoint(
                f"/v1/agent/{self.agent_id}/pause",
                "PUT",
                data=json.dumps(payload),
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": self.superagi_api_key,
                },
            )
            return True

    def run_specific_agent(self, task):
        start_time = time.perf_counter()
        response = self.create_agent(task)
        print(response)
        agent_execution_id = response["run_id"]

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.superagi_api_key,
        }
        check_time_lambda = lambda: self.check_time(start_time, time.perf_counter())
        while not check_time_lambda():
            agent_stream = create_endpoint(
                f"/agentexecutionfeeds/get/execution/{agent_execution_id}",
                headers=headers,
            )
            if agent_stream["status"] == "COMPLETED":
                break

            time.sleep(5)


def main():
    task = sys.argv[1]

    with open("config.yaml", "r") as file:
        config_data = yaml.safe_load(file)

    superagi_api_key = SuperAgiKey(config_data).setup()
    agent = Agent(superagi_api_key)
    agent.run_specific_agent(task)


if __name__ == "__main__":
    main()
