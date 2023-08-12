import importlib.util
import inspect
import json
import os
import sys
import zipfile
from urllib.parse import urlparse

import requests

from superagi.config.config import get_config
from superagi.lib.logger import logger
from superagi.models.tool import Tool
from superagi.models.tool_config import ToolConfig
from superagi.models.toolkit import Toolkit
from superagi.tools.base_tool import BaseTool, ToolConfiguration
from superagi.tools.base_tool import BaseToolkit


def parse_github_url(github_url):
    parts = github_url.split('/')
    owner = parts[3]
    repo = parts[4]
    branch = "main"
    return f"{owner}/{repo}/{branch}"


def download_tool(tool_url, target_folder):
    parsed_url = parse_github_url(tool_url)
    parts = parsed_url.split("/")
    path = "/"
    owner, repo, branch = parts[0], parts[1], parts[2]
    archive_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"
    response = requests.get(archive_url)
    tool_zip_file_path = os.path.join(target_folder, 'tool.zip')

    with open(tool_zip_file_path, 'wb') as f:
        f.write(response.content)

    logger.info("Reading Zip")
    with zipfile.ZipFile(tool_zip_file_path, 'r') as z:
        members = [m for m in z.namelist() if m.startswith(f"{owner}-{repo}") and f"{path}" in m]

        # Extract only folders in the root directory
        root_folders = [member for member in members if member.count('/') > 1]
        for member in root_folders:
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
    logger.info("Donwload Success!")
    os.remove(tool_zip_file_path)


def get_classes_in_file(file_path, clazz):
    classes = []

    module = load_module_from_file(file_path)

    for name, member in inspect.getmembers(module):
        if inspect.isclass(member) and issubclass(member, clazz) and member != clazz:
            class_dict = {}
            class_dict['class_name'] = member.__name__

            class_obj = getattr(module, member.__name__)
            try:
                obj = class_obj()
                if clazz == BaseToolkit:
                    get_toolkit_info(class_dict, classes, obj)
                elif clazz == BaseTool:
                    get_tool_info(class_dict, classes, obj)
            except:
                class_dict = None
    return classes


def get_tool_info(class_dict, classes, obj):
    """
        Get tool information from an object.
    """
    class_dict['tool_name'] = obj.name
    class_dict['tool_description'] = obj.description
    classes.append(class_dict)


def get_toolkit_info(class_dict, classes, obj):
    """
        Get toolkit information from an object.
    """
    class_dict['toolkit_name'] = obj.name
    class_dict['toolkit_description'] = obj.description
    class_dict['toolkit_tools'] = obj.get_tools()
    class_dict['toolkit_keys'] = obj.get_env_keys()
    classes.append(class_dict)


def load_module_from_file(file_path):
    spec = importlib.util.spec_from_file_location("module_name", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def init_tools(folder_paths, session, tool_name_to_toolkit):
    # Iterate over all subfolders
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            continue
        for folder_name in os.listdir(folder_path):
            folder_dir = os.path.join(folder_path, folder_name)
            # Iterate over all files in the subfolder
            if not os.path.isdir(folder_dir):
                continue
                # sys.path.append(os.path.abspath('superagi/tools/email'))
            sys.path.append(folder_dir)
            for file_name in os.listdir(folder_dir):
                file_path = os.path.join(folder_dir, file_name)
                if file_name.endswith(".py") and not file_name.startswith("__init__"):
                    # Get classes
                    classes = get_classes_in_file(file_path=file_path, clazz=BaseTool)
                    update_base_tool_class_info(classes, file_name, folder_name, session, tool_name_to_toolkit)


def update_base_tool_class_info(classes, file_name, folder_name, session, tool_name_to_toolkit):
    for clazz in classes:
        if clazz["class_name"] is not None:
            tool_name = clazz['tool_name']
            tool_description = clazz['tool_description']
            toolkit_id = tool_name_to_toolkit.get((tool_name, folder_name), None)
            if toolkit_id is not None:
                new_tool = Tool.add_or_update(session, tool_name=tool_name, folder_name=folder_name,
                                              class_name=clazz['class_name'], file_name=file_name,
                                              toolkit_id=tool_name_to_toolkit[(tool_name, folder_name)],
                                              description=tool_description)


def init_toolkits(code_link, existing_toolkits, folder_paths, organisation, session):
    tool_name_to_toolkit = {}
    new_toolkits = []
    # Iterate over all subfolders
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            continue
        for folder_name in os.listdir(folder_path):
            folder_dir = os.path.join(folder_path, folder_name)

            if not os.path.isdir(folder_dir):
                continue
                # sys.path.append(os.path.abspath('superagi/tools/email'))
            sys.path.append(folder_dir)
            # Iterate over all files in the subfolder
            for file_name in os.listdir(folder_dir):
                file_path = os.path.join(folder_dir, file_name)
                if file_name.endswith(".py") and not file_name.startswith("__init__"):
                    # Get classes
                    classes = get_classes_in_file(file_path=file_path, clazz=BaseToolkit)
                    tool_name_to_toolkit = update_base_toolkit_info(classes, code_link, folder_name, new_toolkits,
                                                                    organisation, session, tool_name_to_toolkit)
    # Delete toolkits that are not present in the updated toolkits
    delete_extra_toolkit(existing_toolkits, new_toolkits, session)
    return tool_name_to_toolkit


def delete_extra_toolkit(existing_toolkits, new_toolkits, session):
    for toolkit in existing_toolkits:
        if toolkit.name not in [new_toolkit.name for new_toolkit in new_toolkits]:
            session.query(Tool).filter(Tool.toolkit_id == toolkit.id).delete()
            session.query(ToolConfig).filter(ToolConfig.toolkit_id == toolkit.id).delete()
            session.delete(toolkit)
    # Commit the changes to the database
    session.commit()


def update_base_toolkit_info(classes, code_link, folder_name, new_toolkits, organisation, session,
                             tool_name_to_toolkit):
    for clazz in classes:
        if clazz["class_name"] is not None:
            toolkit_name = clazz["toolkit_name"]
            toolkit_description = clazz["toolkit_description"]
            tools = clazz["toolkit_tools"]
            tool_config_keys = clazz["toolkit_keys"]
            # Create a new ToolKit object
            new_toolkit = Toolkit.add_or_update(
                session,
                name=toolkit_name,
                description=toolkit_description,
                show_toolkit=True if len(tools) > 1 else False,
                organisation_id=organisation.id,
                tool_code_link=code_link
            )
            new_toolkits.append(new_toolkit)
            tool_mapping = {}
            # Store the tools in the database
            for tool in tools:
                new_tool = Tool.add_or_update(session, tool_name=tool.name, folder_name=folder_name,
                                              class_name=None, file_name=None,
                                              toolkit_id=new_toolkit.id, description=tool.description)
                tool_mapping[tool.name, folder_name] = new_toolkit.id
            tool_name_to_toolkit = {**tool_mapping, **tool_name_to_toolkit}

            # Store the tools config in the database
            for tool_config_key in tool_config_keys:
                if isinstance(tool_config_key, ToolConfiguration):
                    new_config = ToolConfig.add_or_update(session, toolkit_id=new_toolkit.id,
                                                      key=tool_config_key.key,
                                                      key_type=tool_config_key.key_type,
                                                      is_required=tool_config_key.is_required,
                                                      is_secret=tool_config_key.is_secret)
                else:
                    ToolConfig.add_or_update(session, toolkit_id=new_toolkit.id,
                                                          key = tool_config_key)
    return tool_name_to_toolkit


def process_files(folder_paths, session, organisation, code_link=None):
    existing_toolkits = session.query(Toolkit).filter(Toolkit.organisation_id == organisation.id).all()

    tool_name_to_toolkit = init_toolkits(code_link, existing_toolkits, folder_paths, organisation, session)
    init_tools(folder_paths, session, tool_name_to_toolkit)


def get_readme_content_from_code_link(tool_code_link):
    if tool_code_link is None:
        return None
    parsed_url = urlparse(tool_code_link)
    path_parts = parsed_url.path.split("/")

    # Extract username, repository, and branch from the URL
    username = path_parts[1]
    repository = path_parts[2]
    branch = path_parts[4] if len(path_parts) > 4 else "main"

    readme_url = f"https://raw.githubusercontent.com/{username}/{repository}/{branch}/README.MD"
    response = requests.get(readme_url)
    if response.status_code == 404:
        readme_url = f"https://raw.githubusercontent.com/{username}/{repository}/{branch}/README.md"
        response = requests.get(readme_url)
    readme_content = response.text
    return readme_content


def register_toolkits(session, organisation):
    tool_paths = ["superagi/tools", "superagi/tools/external_tools"]
    # if get_config("ENV", "DEV") == "PROD":
    #     tool_paths.append("superagi/tools/marketplace_tools")
    if organisation is not None:
        process_files(tool_paths, session, organisation)
        logger.info(f"Toolkits Registered Successfully for Organisation ID : {organisation.id}!")

def register_marketplace_toolkits(session, organisation):
    tool_paths = ["superagi/tools", "superagi/tools/external_tools","superagi/tools/marketplace_tools"]
    if organisation is not None:
        process_files(tool_paths, session, organisation)
        logger.info(f"Marketplace Toolkits Registered Successfully for Organisation ID : {organisation.id}!")

def extract_repo_name(repo_link):
    # Extract the repository name from the link
    # Assuming the GitHub link format: https://github.com/username/repoName
    repo_name = repo_link.rsplit('/', 1)[-1]

    return repo_name


def add_tool_to_json(repo_link):
    # Read the content of the tools.json file
    with open('tools.json', 'r') as file:
        tools_data = json.load(file)

    # Extract the repository name from the link
    repo_name = extract_repo_name(repo_link)

    # Add a new key-value pair to the tools object
    tools_data['tools'][repo_name] = repo_link

    # Write the updated JSON object back to tools.json
    with open('tools.json', 'w') as file:
        json.dump(tools_data, file, indent=2)


def handle_tools_import():
    print("Handling tools import")
    tool_paths = ["superagi/tools", "superagi/tools/marketplace_tools", "superagi/tools/external_tools"]
    for tool_path in tool_paths:
        if not os.path.exists(tool_path):
            continue
        for folder_name in os.listdir(tool_path):
            folder_dir = os.path.join(tool_path, folder_name)
            if os.path.isdir(folder_dir):
                sys.path.append(folder_dir)

def compare_tools(tool1, tool2):
    fields = ["name", "description"]
    return any(tool1.get(field) != tool2.get(field) for field in fields)


def compare_configs(config1, config2):
    fields = ["key"]
    return any(config1.get(field) != config2.get(field) for field in fields)


def compare_toolkit(toolkit1, toolkit2):
    main_toolkit_fields = ["description", "show_toolkit", "name", "tool_code_link"]
    toolkit_diff = any(toolkit1.get(field) != toolkit2.get(field) for field in main_toolkit_fields)

    tools1 = sorted(toolkit1.get("tools", []), key=lambda tool: tool.get("name", ""))
    tools2 = sorted(toolkit2.get("tools", []), key=lambda tool: tool.get("name", ""))

    if len(tools1) != len(tools2):
        tools_diff = True
    else:
        tools_diff = any(compare_tools(tool1, tool2) for tool1, tool2 in zip(tools1, tools2))

    tool_configs1 = sorted(toolkit1.get("configs", []), key=lambda config: config.get("key", ""))
    tool_configs2 = sorted(toolkit2.get("configs", []), key=lambda config: config.get("key", ""))
    if len(tool_configs1) != len(tool_configs2):
        tool_configs_diff = True
    else:
        tool_configs_diff = any(compare_configs(config1, config2) for config1, config2 in zip(tool_configs1,
                                                                                              tool_configs2))

    print("toolkit_diff : ", toolkit_diff)
    print("tools_diff : ", tools_diff)
    print("tool_configs_diff : ", tool_configs_diff)
    return toolkit_diff or tools_diff or tool_configs_diff
