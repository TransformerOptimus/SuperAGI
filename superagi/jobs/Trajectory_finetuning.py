from sqlalchemy.orm import Session  # Import your database session setup here
from superagi.models.agent_execution_config import AgentExecutionConfiguration 
from superagi.models.agent_execution_feed import AgentExecutionFeed 
 
 
from superagi.lib.logger import logger

 
import json,ast
from superagi.config.config import get_config
from superagi.vector_store.base import VectorStore
import datetime
class TrajectoryFinetuning:
     def __init__(self,
                  organisation_id: int,
                  session,  
                  agent_execution_id: int,
                  llm,
                  memory:VectorStore=None
                 ):
     
        self.agent_execution_id = agent_execution_id
        self.memory=memory
        self.session = session
        self.organisation_id=organisation_id
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

         
        
         prompt="You are an optimization agent. You are analyzing the `{text_string1}`, plan and `{text_string2}` used by an agent to achieve a given set of `{goals}`. You will understand the path taken by the previous agent execution using the `{instructions}`, thought, tool and plan of action of the previous agent. Analyze the thoughts, tools, plan of action and then criticize the path taken to achieve the goal. Create a list of suggestions based on the criticism so that the agent follows the most optimal path for the exact given set of goals."

         prompt = prompt.replace("{text_string1}", str(text_string1))
         prompt = prompt.replace("{text_string2}", str(text_string2))
         prompt = prompt.replace("{goals}", str(goals))
         prompt = prompt.replace("{instructions}", str(instructions))


         print("Here is the final prompt: ",prompt,"END")
         msg= [{"role": "system", "content": prompt}]
         try:

            response=self.llm.chat_completion(msg)
            current_timestamp = datetime.datetime.now()
            # org_id=self.organisation_id
            agent_ex_id=self.agent_execution_id
            
            # print("_________________________ORG ID", org_id)
           
         except Exception as e:
             
             print(f"Error occurred: {str(e)}")
         # Format the timestamp as mm:ss
         formatted_timestamp = current_timestamp.strftime("%M:%S")
         print("___________________the timestamp is:",formatted_timestamp)
         print("_____________________the content is:",response)

         #metadata = {"response_time_stamp": formatted_timestamp, "Organisation_id": org_id }
        #  metadata = {"agent_execution_id": self.agent_execution_id}
         response_str=json.dumps(response)
         print("___________________STRING RSPONSE IS:",response_str)
         metadata = {"response_time_stamp": formatted_timestamp, "agent_execution_id": agent_ex_id }
         print("____________memory entry")
         if self.memory is not None:
            try:
                self.memory.add_texts([response_str],[metadata])
            except Exception as exception:
                logger.error(f"Exception: {exception}")
         print("_______________the memory is:",self.memory)
         query = "You are a query retrieval agent. You must write a query that will be used by the agent to retrieve the most relevant suggestions for creating the thoughts, tools to use and plan of action to achieve the given goals. The query should be framed to properly retrieve the most relevant feedback and improve the path to achieve the goals."
        #  print("_______________the memory is:",self.memory)
         if self.memory is None:
            return ""
         print(metadata)
         ft_response = self.memory.get_matching_text(query,top_k=2,metadata=metadata)
         #print("_______________________similarity response",ft_response['documents'])
         return ft_response['documents']
     
        

