import logging
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from superagi.models.call_logs import CallLogs
from superagi.models.agent import Agent
from superagi.models.tool import Tool
from superagi.models.toolkit import Toolkit

class CallLogHelper:

    def __init__(self, session: Session, organisation_id: int):
        self.session = session
        self.organisation_id = organisation_id

    def create_call_log(self, agent_execution_name: str, agent_id: int, tokens_consumed: int, tool_used: str, model: str) -> Optional[CallLogs]:
        try:
            call_log = CallLogs(
                agent_execution_name=agent_execution_name,
                agent_id=agent_id,
                tokens_consumed=tokens_consumed,
                tool_used=tool_used,
                model=model,
                org_id=self.organisation_id,
            )
            self.session.add(call_log)
            self.session.commit()
            return call_log
        except SQLAlchemyError as err:
            logging.error(f"Error while creating call log: {str(err)}")
            return None

    def fetch_data(self, model: str):
        try:
            result = self.session.query(
                func.sum(CallLogs.tokens_consumed),
                func.count(CallLogs.id),
                func.count(distinct(CallLogs.agent_id))
            ).filter(CallLogs.model == model, CallLogs.org_id == self.organisation_id).first()

            if result is None:
                return None

            model_data = {
                'model': model,
                'total_tokens': result[0],
                'total_calls': result[1],
                'total_agents': result[2],
                'runs': []
            }

            # Fetch all runs for this model
            runs = self.session.query(CallLogs).filter(CallLogs.model == model, CallLogs.org_id == self.organisation_id).all()
            for run in runs:
                # Get agent's name using agent_id as a foreign key
                agent = self.session.query(Agent).filter(Agent.id == run.agent_id).first()

                # Get toolkit's name using tool_used as a linking key
                toolkit = None
                tool = self.session.query(Tool).filter(Tool.name == run.tool_used).first()
                if tool:
                    toolkit = self.session.query(Toolkit).filter(Toolkit.id == tool.toolkit_id).first()

                model_data['runs'].append({
                    'id': run.id,
                    'agent_execution_name': run.agent_execution_name,
                    'agent_id': run.agent_id,
                    'agent_name': agent.name if agent is not None else None, # add agent_name to dictionary
                    'tokens_consumed': run.tokens_consumed,
                    'tool_used': run.tool_used,
                    'toolkit_name': toolkit.name if toolkit is not None else None, # add toolkit_name to dictionary
                    'org_id': run.org_id,
                    'created_at': run.created_at,
                    'updated_at': run.updated_at,
                })

            return model_data

        except SQLAlchemyError as err:
            logging.error(f"Error while fetching call log data: {str(err)}")
            return None