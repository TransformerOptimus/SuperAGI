import os

import click
import getpass
import uuid

from dotenv import load_dotenv

from yeagerai.agent import YeagerAIAgent
from yeagerai.memory import YeagerAIContext
from yeagerai.memory.callbacks import KageBunshinNoJutsu
from yeagerai.interfaces.callbacks import GitLocalRepoCallbackHandler

from yeagerai.toolkit import (
    YeagerAIToolkit,
    CreateToolSourceAPIWrapper,
    CreateToolSourceRun,
    DesignSolutionSketchAPIWrapper,
    DesignSolutionSketchRun,
    CreateToolMockedTestsAPIWrapper,
    CreateToolMockedTestsRun,
    LoadNFixNewToolAPIWrapper,
    LoadNFixNewToolRun,
)


def pre_load():
    # Init variables
    has_api_key = True
    username = getpass.getuser()
    home_path = os.path.expanduser("~")
    root_path = os.path.join(home_path, ".yeagerai-sessions")
    os.makedirs(root_path, exist_ok=True)

    # Checking OPENAI_API_KEY
    env_path = os.path.join(root_path, ".env")
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write(f"OPENAI_API_KEY=1234")
        has_api_key = False
        print(
            "Please modify the .env file inside ~/.yeagerai-sessions/.env and add your OpenAI API key... "
        )

    load_dotenv(dotenv_path=env_path)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print(
            "Please modify the .env file inside ~/.yeagerai-sessions/.env and add your OpenAI API key... "
        )
        has_api_key = False

    # Create or restore session
    if has_api_key:
        previous_session_id = input(
            "Enter the session_id of an already existing session to continue working with it (leave empty if you want to start a new session): "
        )
        if previous_session_id:
            session_id = previous_session_id
            session_path = os.path.join(root_path, session_id)
            if os.path.exists(session_path):
                print(f"Session {session_id} already exists. Continuing with it.")
            else:
                print(f"Session {session_id} does not exist. Creating a new session.")
                session_id = str(uuid.uuid1())[:7] + "-" + username
                session_path = os.path.join(root_path, session_id)
        else:
            session_id = str(uuid.uuid1())[:7] + "-" + username
            session_path = os.path.join(root_path, session_id)
    else:
        session_id = None
        session_path = None

    return has_api_key, username, session_id, session_path, env_path


def chat_interface(
    username,
    model_name,
    request_timeout,
    streaming,
    session_id,
    session_path,
    callbacks,
    yeager_kit,
    y_context,
):
    while True:
        try:
            prompt_text = input("\n\nEnter your prompt (Type :q to quit):\n\n> ")
            if prompt_text == ":q":
                break

            agent = YeagerAIAgent(
                username=username,
                model_name=model_name,
                request_timeout=request_timeout,
                streaming=streaming,
                session_id=session_id,
                session_path=session_path,
                callbacks=callbacks,
                yeager_kit=yeager_kit,
                context=y_context,
            )
            agent.run(prompt_text)

        except KeyboardInterrupt:
            continue
        except EOFError:
            break


@click.command()
def main():
    has_api_key, username, session_id, session_path, env_path = pre_load()

    if not has_api_key:
        print("Exiting...")
        return

    model_name = "gpt-4"  # you can switch to gpt-3.5-turbo but is not tested
    request_timeout = 300
    streaming = True

    # build context
    y_context = YeagerAIContext(username, session_id, session_path)

    # build callbacks
    callbacks = [
        KageBunshinNoJutsu(y_context),
        GitLocalRepoCallbackHandler(username=username, session_path=session_path),
    ]

    # toolkit
    yeager_kit = YeagerAIToolkit()
    yeager_kit.register_tool(
        DesignSolutionSketchRun(
            api_wrapper=DesignSolutionSketchAPIWrapper(
                session_path=session_path,
                model_name=model_name,
                request_timeout=request_timeout,
                streaming=streaming,
            )
        ),
    )
    yeager_kit.register_tool(
        CreateToolMockedTestsRun(
            api_wrapper=CreateToolMockedTestsAPIWrapper(
                session_path=session_path,
                model_name=model_name,
                request_timeout=request_timeout,
                streaming=streaming,
            )
        ),
    )
    yeager_kit.register_tool(
        CreateToolSourceRun(
            api_wrapper=CreateToolSourceAPIWrapper(
                session_path=session_path,
                model_name=model_name,
                request_timeout=request_timeout,
                streaming=streaming,
            )
        ),
    )

    yeager_kit.register_tool(
        LoadNFixNewToolRun(
            api_wrapper=LoadNFixNewToolAPIWrapper(
                session_path=session_path,
                model_name=model_name,
                request_timeout=request_timeout,
                streaming=streaming,
                toolkit=yeager_kit,
            )
        ),
    )

    click.echo(click.style("Welcome to the @yeager.ai CLI!\n", fg="green", bold=True))
    click.echo(click.style("Loading The @yeager.ai Agent Interface...", fg="green"))
    chat_interface(
        username,
        model_name,
        request_timeout,
        streaming,
        session_id,
        session_path,
        callbacks,
        yeager_kit,
        y_context,
    )


if __name__ == "__main__":
    # start conversation
    main()
