import os
from pathlib import Path

import requests
import zipfile
import json

def parse_github_url(github_url):
    parts = github_url.split('/')
    owner = parts[3]
    repo = parts[4]
    branch = "main"
    return f"{owner}/{repo}/{branch}"

def download_tool(tool_url, target_folder):
    parsed_url = parse_github_url(tool_url)
    parts = parsed_url.split("/")
    owner, repo, branch, path = parts[0], parts[1], parts[2], "/".join(parts[3:])

    archive_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"

    response = requests.get(archive_url)

    tool_zip_file_path = os.path.join(target_folder, 'tool.zip')

    with open(tool_zip_file_path, 'wb') as f:
        f.write(response.content)

    with zipfile.ZipFile(tool_zip_file_path, 'r') as z:
        members = [m for m in z.namelist() if m.startswith(f"{owner}-{repo}") and f"{path}" in m]
        for member in members:
            archive_folder = f"{owner}-{repo}"
            target_name = member.replace(f"{archive_folder}/", "", 1)

            # Skip the unique hash folder while extracting:
            segments = target_name.split('/', 1)
            if len(segments) > 1:
                target_name = segments[1]
            else:
                continue

            target_path = os.path.join(target_folder, target_name)

            if not target_name:
                continue

            if member.endswith('/'):
                os.makedirs(target_path, exist_ok=True)
            else:
                with open(target_path, 'wb') as outfile, z.open(member) as infile:
                    outfile.write(infile.read())

    os.remove(tool_zip_file_path)


def load_tools_config():
    tool_config_path = str(Path(__file__).parent.parent)
    with open(tool_config_path + "/tools.json", "r") as f:
        config = json.load(f)
        return config["tools"]


def download_and_extract_tools():
    tools_config = load_tools_config()

    for tool_name, tool_url in tools_config.items():
        tool_folder = os.path.join("superagi", "tools", tool_name)
        if not os.path.exists(tool_folder):
            os.makedirs(tool_folder)
        download_tool(tool_url, tool_folder)


if __name__ == "__main__":
    download_and_extract_tools()