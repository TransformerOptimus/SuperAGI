import os
import requests
import zipfile
import json
import inspect
from superagi.models.tool import Tool
from superagi.tools.base_tool import BaseTool
from superagi.tools.base_tool import BaseToolKit


def parse_github_url(github_url):
    parts = github_url.split('/')

    if len(parts) >= 7:
        owner = parts[3]
        repo = parts[4]
        branch = parts[6]
        path = '/'.join(parts[7:])

        return f"{owner}/{repo}/{branch}/{path}"
    else:
        raise ValueError("Invalid GitHub URL")


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


# def load_tools_config():
#     with open("tools.json", "r") as f:
#         config = json.load(f)
#         return config["TOOLS"]

# def download_and_extract_tools():
#     tools_config = load_tools_config()
#
#     for tool_name, tool_url in tools_config.items():
#         tool_folder = os.path.join("superagi", ".input_tools", tool_name)
#         if not os.path.exists(tool_folder):
#             os.makedirs(tool_folder)
#         download_tool(tool_url, tool_folder)
#
#
# if __name__ == "__main__":
#     download_and_extract_tools()




def get_classes_in_file(file_path):
    classes = []

    # Load the module from the file
    module = load_module_from_file(file_path)

    # Iterate over all members of the module
    for name, member in inspect.getmembers(module):
        # Check if the member is a class and extends BaseTool
        if inspect.isclass(member) and issubclass(member, BaseTool) and member != BaseTool:
            class_dict = {}
            class_dict['class_name'] = member.__name__

            class_obj = getattr(module, member.__name__)
            try:
                obj = class_obj()
                class_dict['class_attribute'] = obj.name
                classes.append(class_dict)
            except:
                class_dict['class_attribute'] = None
    return classes
def load_module_from_file(file_path):
    import importlib.util

    spec = importlib.util.spec_from_file_location("module_name", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


# Function to process the files and extract class information
def process_files(folder_path, session):
    existing_tools = session.query(Tool).all()

    new_tools = []
    # Iterate over all subfolders
    for folder_name in os.listdir(folder_path):
        folder_dir = os.path.join(folder_path, folder_name)

        if os.path.isdir(folder_dir):
            # Iterate over all files in the subfolder
            for file_name in os.listdir(folder_dir):
                file_path = os.path.join(folder_dir, file_name)
                if file_name.endswith(".py") and not file_name.startswith("__init__"):
                    # Get clasess
                    classes = get_classes_in_file(file_path=file_path)
                    for clazz in classes:
                        if clazz["class_attribute"] is not None:
                            new_tool = Tool(class_name=clazz["class_name"], folder_name=folder_name,
                                            file_name=file_name,
                                            name=clazz["class_attribute"])
                            new_tools.append(new_tool)

    # Delete tools that are not present in the updated tools
    for tool in existing_tools:
        if tool.name not in [new_tool.name for new_tool in new_tools]:
            Tool.delete_tool(session, tool.name)

    # Update the latest tool
    for tool in new_tools:
        Tool.add_or_update_tool(session, tool_name=tool.name, file_name=tool.file_name, folder_name=tool.folder_name,
                           class_name=tool.class_name)





def process_files(folder_path, session):
    existing_toolkits = session.query(ToolKit).all()

    new_toolkits = []
    # Iterate over all subfolders
    for folder_name in os.listdir(folder_path):
        folder_dir = os.path.join(folder_path, folder_name)

        if os.path.isdir(folder_dir):
            # Iterate over all files in the subfolder
            for file_name in os.listdir(folder_dir):
                file_path = os.path.join(folder_dir, file_name)
                if file_name.endswith(".py") and not file_name.startswith("__init__"):
                    # Get classes
                    classes = get_classes_in_file(file_path=file_path)
                    for clazz in classes:
                        if clazz["class_attribute"] is not None:
                            toolkit_name = clazz["class_attribute"]
                            toolkit_description = clazz["class_description"]
                            tools = clazz["tools"]

                            # Create a new ToolKit object
                            new_toolkit = ToolKit(
                                name=toolkit_name,
                                description=toolkit_description,
                                show_tool_kit=True,
                                organisation_id=1  # Set the organization ID as needed
                            )

                            # Store the new ToolKit object in the list
                            new_toolkits.append(new_toolkit)

                            # Store the tools in the database
                            for tool_name in tools:
                                new_tool = BaseTool(
                                    toolkit_id=new_toolkit.id,
                                    name=tool_name
                                )
                                session.add(new_tool)

    # Delete toolkits that are not present in the updated toolkits
    for toolkit in existing_toolkits:
        if toolkit.name not in [new_toolkit.name for new_toolkit in new_toolkits]:
            session.delete(toolkit)

    # Commit the changes to the database
    session.commit()
