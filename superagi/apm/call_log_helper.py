import logging
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from superagi.models.call_logs import CallLogs

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