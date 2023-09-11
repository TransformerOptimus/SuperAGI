
from sqlalchemy.orm import Session  # Import your database session setup here
from superagi.models.agent_execution_config import AgentExecutionConfiguration 
from superagi.models.agent_execution_feed import AgentExecutionFeed 
from superagi.llms.openai import OpenAi
from superagi.helper.feed_parser import parse_feed
from superagi.lib.logger import logger
class TrajectoryFinetuning:

    @classmethod
    def Trajectory_finetuning( session, agent_execution_id):
         
         agent_configs = AgentExecutionConfiguration.fetch_configuration(session=session, execution_id=agent_execution_id) 
         goals = agent_configs.get("goal", [])
         instructions = agent_configs.get("instructions", [])
         agent_feeds= AgentExecutionFeed.fetch_agent_execution_feeds(session=session, execution_id=agent_execution_id)
         parsed_feed=parsed_feed(agent_feeds)
         if parsed_feed["role"] == "assistant":
           thoughts = parsed_feed["feed"].get("Thoughts:", "")
           plan = parsed_feed["feed"].get("Plan:", "")
           tool_name = parsed_feed["feed"].get("Tool:", "")
        
         logger.info(goals)
         logger.info(instructions)
         logger.info(thoughts)
         logger.info(tool_name)
         logger.info(plan)
        #  response=OpenAi.chat_completion(goals,instructions,thoughts,plan,tool_name,"You are an optimization agent. You are analyzing the thoughts, plan of action and tools used by an agent to achieve a given set of goals. You will understand the path taken by the previous agent execution using the thought, tool and plan of action of the previous agent. Analyze the thoughts, tools, plan of action and then criticize the path taken to achieve the goal. Create a list of suggestions based on the criticism so that the agent follows the most optimal path for the exact given set of goals.")
        #  return response


