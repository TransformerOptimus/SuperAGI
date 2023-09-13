from sqlalchemy.orm import Session  # Import your database session setup here
from superagi.models.agent_execution_config import AgentExecutionConfiguration 
from superagi.models.agent_execution_feed import AgentExecutionFeed 
from superagi.llms.openai import OpenAi
from superagi.helper.feed_parser import parse_feed
from superagi.lib.logger import logger
from superagi.jobs.agent_executor import AgentExecutor
from superagi.models.agent import Agent
import json,ast
from superagi.config.config import get_config
from superagi.vector_store.base import VectorStore
class TrajectoryFinetuning:
     def __init__(self,
                  session,
                  agent_execution_id: int,
                  llm,
                  memory:VectorStore=None
                 ):
     
        self.agent_execution_id = agent_execution_id
        self.memory=memory
        self.session = session
        self.llm = llm
 
     def Trajectory_finetuning(self):
         print("_________________entered trajectory finetuning")
         
         agent_configs = AgentExecutionConfiguration.fetch_configuration(session=self.session, execution_id=self.agent_execution_id)
         print("_________________agent config is:",agent_configs)
         goals = agent_configs.get("goal")
         instructions = agent_configs.get("instruction")
         agent_feeds= AgentExecutionFeed.fetch_agent_execution_feeds(session=self.session, agent_execution_id=self.agent_execution_id)
         print("___________________agent feed:",agent_feeds)

         thoughts = []
         tools = []

         for item in agent_feeds:
              if item[0] == 'assistant':
                  dictionary = ast.literal_eval(str(item[1]))
                  thoughts.append(dictionary.get('thoughts', None))
                  tools.append(dictionary.get('tool', None))

         print('Thoughts:', thoughts)
         print('Tools:', tools)


         though_str = [d['text'] for d in thoughts]
         tool_str = [d['name'] for d in tools]


         text_string1 = " ".join(though_str)  # Join all the texts into a single string, separated by space
         text_string2 = " ".join(tool_str)

         print("Here is the thought: ",text_string1,"END")
         print("Here is the tool: ",text_string2,"END")

         
        
         prompt="You are an optimization agent. You are analyzing the `{text_string1}`, plan and `{text_string2}` used by an agent to achieve a given set of `{goals}`. You will understand the path taken by the previous agent execution using the `{instruction}`, thought, tool and plan of action of the previous agent. Analyze the thoughts, tools, plan of action and then criticize the path taken to achieve the goal. Create a list of suggestions based on the criticism so that the agent follows the most optimal path for the exact given set of goals."

         prompt = prompt.replace("{text_string1}", str(text_string1))
         prompt = prompt.replace("{text_string2}", str(text_string2))
         prompt = prompt.replace("{goals}", str(goals))
         prompt = prompt.replace("{instructions}", str(instructions))


         print("Here is the final prompt: ",prompt,"END")
         msg= [{"role": "system", "content": prompt}]
         response=self.llm.chat_completion(msg)
          
        #  agent = db.session.query(Agent).filter(Agent.id == agent_execution.agent_id, Agent.is_deleted == False).first()
        #  metadata = {"organisation_id": self.agent_execution_id}
         self.memory.add_texts(response)
         return response
     
        

