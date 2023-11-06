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

            runs = self.session.query(CallLogs).filter(CallLogs.model == model,
                                                       CallLogs.org_id == self.organisation_id).all()

            run_agent_ids = [run.agent_id for run in runs]
            agents = self.session.query(Agent).filter(Agent.id.in_(run_agent_ids)).all()
            agent_id_name_map = {agent.id: agent.name for agent in agents}
            tools_used = [run.tool_used for run in runs]
            toolkit_ids_allowed = self.session.query(Toolkit.id).filter(Toolkit.organisation_id == self.organisation_id).all()
            toolkit_ids_allowed = [toolkit_id[0] for toolkit_id in toolkit_ids_allowed]
            tools = self.session.query(Tool).filter(Tool.name.in_(tools_used), Tool.toolkit_id.in_(toolkit_ids_allowed))\
                .all()
            tools_name_toolkit_id_map = {tool.name: tool.toolkit_id for tool in tools}

            for run in runs:
                model_data['runs'].append({
                    'id': run.id,
                    'agent_execution_name': run.agent_execution_name,
                    'agent_id': run.agent_id,
                    'agent_name': agent_id_name_map[run.agent_id] if run.agent_id in agent_id_name_map else None,
                    'tokens_consumed': run.tokens_consumed,
                    'tool_used': run.tool_used,
                    'toolkit_name': tools_name_toolkit_id_map[run.tool_used] if run.tool_used in tools_name_toolkit_id_map else None,
                    'org_id': run.org_id,
                    'created_at': run.created_at,
                    'updated_at': run.updated_at,
                })

            model_data['runs'] = model_data['runs'][::-1]

            return model_data

        except SQLAlchemyError as err:
            logging.error(f"Error while fetching call log data: {str(err)}")
            return None
