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


def _safe_extract_member(zip_file, member, target_folder):
    if '/' not in member:
        return
    target_name = member.split('/', 1)[1]
    normalized_path = os.path.abspath(os.path.join(target_folder, target_name))
    if not normalized_path.startswith(os.path.abspath(target_folder) + os.sep):
        return
    if member.endswith('/'):
        os.makedirs(normalized_path, exist_ok=True)
        return
    os.makedirs(os.path.dirname(normalized_path), exist_ok=True)
    with open(normalized_path, 'wb') as outfile, zip_file.open(member) as infile:
        outfile.write(infile.read())


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
            _safe_extract_member(z, member, target_folder)

    os.remove(tool_zip_file_path)


def download_marketplace_tool(tool_url, target_folder):
    parsed_url = tool_url.split("/")
    owner, repo = parsed_url[3], parsed_url[4]
    archive_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/main"
    response = requests.get(archive_url)
    tool_zip_file_path = os.path.join(target_folder, 'tool.zip')

    with open(tool_zip_file_path, 'wb') as f:
        f.write(response.content)

    with zipfile.ZipFile(tool_zip_file_path, 'r') as z:
        for member in z.namelist():
            if '/' not in member:
                continue
            target_name = os.path.abspath(os.path.join(target_folder, member.split('/', 1)[1]))
            if not target_name.startswith(os.path.abspath(target_folder) + os.sep):
                continue
            if member.endswith('/'):
                os.makedirs(target_name, exist_ok=True)
            elif not target_name.endswith('.md'):
                os.makedirs(os.path.dirname(target_name), exist_ok=True)
                with open(target_name, 'wb') as outfile, z.open(member) as infile:
                    outfile.write(infile.read())

    os.remove(tool_zip_file_path)


def get_marketplace_tool_links(repo_url):
    folder_links = {}
    api_url = f"https://api.github.com/repos/{repo_url}/contents"
    response = requests.get(api_url)
    contents = response.json()

    for content in contents:
        if content["type"] == "dir":
            folder_name = content["name"]
            folder_link = f"https://github.com/{repo_url}/tree/main/{folder_name}"
            folder_links[folder_name] = folder_link

    return folder_links


def update_tools_json(existing_tools_json_path, folder_links):
    with open(existing_tools_json_path, "r") as file:
        tools_data = json.load(file)
    if "tools" not in tools_data:
        tools_data["tools"] = {}
    tools_data["tools"].update(folder_links)
    with open(existing_tools_json_path, "w") as file:
        json.dump(tools_data, file, indent=4)


def load_tools_config():
    tool_config_path = str(Path(__file__).parent.parent)
    with open(tool_config_path + "/tools.json", "r") as f:
        config = json.load(f)
        return config["tools"]


def load_marketplace_tools():
    marketplace_url = "TransformerOptimus/SuperAGI-Tools"
    tools_config_path = str(Path(__file__).parent.parent)
    tools_json_path = tools_config_path + "/tools.json"
    # Get folder links from the repository
    marketplace_tool_urls = get_marketplace_tool_links(marketplace_url)
    # Update existing tools.json file
    update_tools_json(tools_json_path, marketplace_tool_urls)


def is_marketplace_url(url):
    return url.startswith("https://github.com/TransformerOptimus/SuperAGI-Tools/tree")

def download_and_extract_tools():
    tools_config = load_tools_config()

    for tool_name, tool_url in tools_config.items():
        if is_marketplace_url(tool_url):
            tool_folder = os.path.join("superagi/tools/marketplace_tools")
            if not os.path.exists(tool_folder):
                os.makedirs(tool_folder)
            download_marketplace_tool(tool_url, tool_folder)
        else:
            tool_folder = os.path.join("superagi/tools/external_tools", tool_name)
            if not os.path.exists(tool_folder):
                os.makedirs(tool_folder)
            download_tool(tool_url, tool_folder)


if __name__ == "__main__":
    load_marketplace_tools()
    download_and_extract_tools()
