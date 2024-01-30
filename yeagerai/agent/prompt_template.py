from typing import List
from langchain.prompts import BaseChatPromptTemplate
from langchain.schema import HumanMessage, BaseMessage, messages_to_dict
from langchain.memory import ChatMessageHistory
from yeagerai.toolkit import YeagerAITool


class YeagerAIPromptTemplate(BaseChatPromptTemplate):
    template: str
    tools: List[YeagerAITool]
    chat_history: ChatMessageHistory

    def format_messages(self, **kwargs) -> List[BaseMessage]:
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "

        kwargs["agent_scratchpad"] = thoughts

        kwargs["tools"] = "\n".join(
            [f"{tool.name}: {tool.description}" for tool in self.tools]
        )
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        kwargs["tools_final_answer_formats"] = "\n- ".join(
            [tool.name + ":\n\t- " + tool.final_answer_format for tool in self.tools]
        )

        dicts = messages_to_dict(self.chat_history.messages)
        if len(dicts) == 0:
            kwargs["chat_history"] = "No previous messages in the chat."
        else:
            kwargs["chat_history"] = "\n".join(
                [
                    message["type"] + ": (" + message["data"]["content"] + ")"
                    for message in dicts
                ]
            )

        formatted = self.template.format(**kwargs)
        # print(formatted)
        return [HumanMessage(content=formatted)]
