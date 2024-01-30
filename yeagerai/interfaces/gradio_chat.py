import os
import getpass
import uuid

import gradio as gr

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

    return has_api_key, openai_api_key, username, env_path, root_path


def set_session_variables(username, model_name, request_timeout, root_path, session_id):
    session_path = os.path.join(root_path, session_id)
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
            )
        ),
    )
    yeager_kit.register_tool(
        CreateToolMockedTestsRun(
            api_wrapper=CreateToolMockedTestsAPIWrapper(
                session_path=session_path,
                model_name=model_name,
                request_timeout=request_timeout,
            )
        ),
    )
    yeager_kit.register_tool(
        CreateToolSourceRun(
            api_wrapper=CreateToolSourceAPIWrapper(
                session_path=session_path,
                model_name=model_name,
                request_timeout=request_timeout,
            )
        ),
    )

    yeager_kit.register_tool(
        LoadNFixNewToolRun(
            api_wrapper=LoadNFixNewToolAPIWrapper(
                session_path=session_path,
                model_name=model_name,
                request_timeout=request_timeout,
                toolkit=yeager_kit,
            )
        ),
    )
    return y_context, callbacks, yeager_kit


def load_state():
    has_api_key, openai_api_key, username, env_path, root_path = pre_load()
    session_id = str(uuid.uuid1())[:7] + "-" + username
    session_path = os.path.join(root_path, session_id)
    model_name = "gpt-4"
    request_timeout = 300
    y_context, callbacks, yeager_kit = set_session_variables(
        username, model_name, request_timeout, root_path, session_id
    )
    return {
        "has_api_key": has_api_key,
        "openai_api_key": openai_api_key,
        "username": username,
        "env_path": env_path,
        "root_path": root_path,
        "session_id": session_id,
        "session_path": session_path,
        "model_name": model_name,
        "request_timeout": request_timeout,
        "y_context": y_context,
        "callbacks": callbacks,
        "yeager_kit": yeager_kit,
    }


def update_state_from_settings(
    session_id, model_name, request_timeout, openai_api_key, session_data
):
    session_data["session_id"] = session_id
    session_data["model_name"] = model_name
    session_data["request_timeout"] = request_timeout
    if openai_api_key != session_data["openai_api_key"]:
        session_data["openai_api_key"] = openai_api_key
        with open(session_data.value["env_path"], "w") as f:
            f.write(f"OPENAI_API_KEY={openai_api_key}")
    return session_data


############### GRADIO CHATBOT ###############


def add_text(history, text):
    history = history + [(text, None)]
    return history, ""


def bot(history, session_data):
    agent = YeagerAIAgent(
        username=session_data["username"],
        model_name=session_data["model_name"],
        request_timeout=session_data["request_timeout"],
        session_id=session_data["session_id"],
        session_path=session_data["session_path"],
        callbacks=session_data["callbacks"],
        yeager_kit=session_data["yeager_kit"],
        context=session_data["y_context"],
    )

    response = agent.run(history[-1][0])
    history[-1][1] = response

    return history


def main():
    with gr.Blocks() as demo:
        session_data = gr.State(load_state)
        gr.Markdown(
            """
        ## Welcome to the [yAgents](https://github.com/yeagerai/yeagerai-agent) Gradio Interface!

        This is a demo of the yAgents agent (aka yeagerai-agent) which is the first AI-Agent that builds AI-Agents with human feedback.
        
        designed to help you build, prototype, and deploy AI-powered agents with ease.
        """
        )

        with gr.Tab("yAgents Chat"):
            chatbot = gr.Chatbot([], elem_id="chatbot", show=False).style(height=650)
            with gr.Row():
                with gr.Column(scale=0.85):
                    message_input = gr.Textbox(
                        name="message",
                        show_label=False,
                        placeholder="Write a message and press enter",
                    ).style(container=False)
                with gr.Column(scale=0.15, min_width=0):
                    stop_button = gr.Button(value="Stop conversation")
            message_submission = message_input.submit(
                add_text, [chatbot, message_input], [chatbot, message_input]
            ).then(bot, [chatbot, session_data], chatbot)
            stop_button.click(
                fn=None, inputs=None, outputs=None, cancels=[message_submission]
            )
        with gr.Tab("Settings"):
            gr.Markdown(
                """
            **IMPORTANT:** If this is your first time using the yAgents, you should paste your OpenAI API key in the API Key field and click Submit. You can also change the model name and request timeout.
            GPT-4 is highly recommended.
            """
            )
            session_id_input = gr.Textbox(
                name="session_id",
                label="Session ID",
                placeholder="Enter a session ID to continue a conversation, or leave blank to create a new one",
            )
            model_name_radio = gr.Radio(
                ["gpt-4", "gpt-3.5-turbo"],
                label="Model Name",
                name="model_name",
                value=session_data.value["model_name"],
            )
            request_timeout_input = gr.Number(
                name="request_timeout",
                label="Request Timeout",
                value=session_data.value["request_timeout"],
                min=200,
                max=1000,
            )
            api_key_input = gr.Textbox(
                label="API Key",
                name="api_key",
                type="password",
                value=session_data.value["openai_api_key"],
            )
            submit_settings_button = gr.Button(
                "Update",
                action="submit",
                name="submit_settings_button",
                variant="primary",
            )
            submit_settings_button.click(
                fn=update_state_from_settings,
                inputs=[
                    session_id_input,
                    model_name_radio,
                    request_timeout_input,
                    api_key_input,
                    session_data,
                ],
                outputs=[session_data],
            )
    demo.queue(concurrency_count=2, max_size=20).launch()


if __name__ == "__main__":
    main()
