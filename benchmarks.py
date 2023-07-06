import os
import sys
from typing import Tuple
import subprocess


def run_specific_agent(task: str) -> None:
    # Run the mini-agi command
    subprocess.run(
        [
            "python",
            "test.py --name",
            "MyAgent --description",
            "Perform the goals you are given to the best of your ability --goals",
            task,
        ],
        text=True,
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <task>")
        sys.exit(1)
    task = sys.argv[1]
    run_specific_agent(task)
