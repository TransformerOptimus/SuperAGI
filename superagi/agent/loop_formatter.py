from typing import Any
from superagi.lib.logger import logger

class LoopFormatter:
    def __init__(self, llm):
        self.llm = llm
        
    def _loop_formatter(self, prompt_question):
        logger.info("_____________LOOP FORMATTER________________")
        system_prompt = ""
        with open("superagi/agent/prompts/loop_formatter.txt", "r") as f:
            system_prompt = f.read()
        msgs = []
        msg = {"role": "system", "content": system_prompt}
        logger.info(f"########    {msg['role']}\n\n{msg['content']}\n\n")
        msgs.append(msg)
        msg = {"role": "user", "content": prompt_question}
        logger.info(f"########    {msg['role']}\n\n{msg['content']}\n\n")
        msgs.append(msg)
        c = self.llm.chat_completion(messages=msgs)
        content = c['content']
        msg = {"role": "assistant", "content": content}
        logger.info(f"########    {msg['role']}\n\n{msg['content']}\n\n")
        return content