from sqlalchemy.orm import Session  # Import your database session setup here
from superagi.models.agent_execution_config import AgentExecutionConfiguration 
from superagi.models.agent_execution_feed import AgentExecutionFeed 
from superagi.llms.openai import OpenAi
from superagi.helper.feed_parser import parse_feed
from superagi.lib.logger import logger
from superagi.jobs.agent_executor import AgentExecutor
from superagi.models.agent import Agent
import json
from superagi.config.config import get_config
from superagi.vector_store.base import VectorStore
class TrajectoryFinetuning:
     def __init__(self,session,agent_execution_id: int,
                 llm, 
                 ):
     
        self.agent_execution_id = agent_execution_id
        # self.memory=memory
        self.session = session
        self.llm = llm
 
     def Trajectory_finetuning(self):
         
         agent_configs = AgentExecutionConfiguration.fetch_configuration(session=self.session, execution_id=self.agent_execution_id)
         goals = agent_configs.get("goal")
         instructions = agent_configs.get("instruction")
         agent_feeds= AgentExecutionFeed.fetch_agent_execution_feeds(session=self.session, agent_execution_id=self.agent_execution_id)
         parsed=parse_feed(agent_feeds)  
         if parsed["role"] == "assistant":
           thoughts = parsed["feed"].get("Thoughts:", "")
           plan = parsed["feed"].get("Plan:", "")
           tool_name = parsed["feed"].get("Tool:", "")
         
        
         prompt="You are an optimization agent. You are analyzing the {thoughts}, {plan} and {tools} used by an agent to achieve a given set of {goals}. You will understand the path taken by the previous agent execution using the {instruction}, thought, tool and plan of action of the previous agent. Analyze the thoughts, tools, plan of action and then criticize the path taken to achieve the goal. Create a list of suggestions based on the criticism so that the agent follows the most optimal path for the exact given set of goals."
         for_prompt=prompt.format(thoughts=thoughts, plan=plan, tools=tool_name, goals=goals,instruction=instructions)
         msg= [{"role": "system", "content": for_prompt}]
         response=self.llm.chat_completion(msg)
         print("RESPONSE____________________________",response)
         return response
