from sqlalchemy.orm import Session  # Import your database session setup here
from superagi.models.agent_execution_config import AgentExecutionConfiguration  
from superagi.agent.agent_message_builder import AgentLlmMessageBuilder
from superagi.lib.logger import logger 
import json
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
         agent_configs = AgentExecutionConfiguration.fetch_configuration(session=self.session, execution_id=self.agent_execution_id)
         goals = agent_configs.get("goal")
         instructions = agent_configs.get("instruction")
         prompt=AgentLlmMessageBuilder._build_prompt_for_trajectory_finetuning(self)
         msg= [{"role": "system", "content": prompt}]
         try:
            response=self.llm.chat_completion(msg)
            current_timestamp = datetime.datetime.now()
            agent_ex_id=self.agent_execution_id
         except Exception as e:
             print(f"Error occurred: {str(e)}")
         formatted_timestamp = current_timestamp.strftime("%M:%S")
         response_str=json.dumps(response)
         metadata = {"response_time_stamp": formatted_timestamp, "agent_execution_id": agent_ex_id }
         if self.memory is not None:
            try:
                self.memory.add_texts([response_str],[metadata])
            except Exception as exception:
                logger.error(f"Exception: {exception}")
         query = "Get the most relevant and matching response for the completion of the GOALS:`{goals}` and INSTRUCTIONS:`{instructions}` "
         query = query.replace("{goals}", str(goals))
         query = query.replace("{instructions}", str(instructions))
         if self.memory is None:
            return ""
         print(metadata)
         ft_response = self.memory.get_matching_text(query,top_k=2,metadata=metadata)
         return ft_response['documents']    
     
        

