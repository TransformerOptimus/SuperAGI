from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from superagi.models.webhooks import Webhooks
from superagi.models.webhook_events import WebhookEvents
import requests
import json
from superagi.lib.logger import logger
class WebHookManager:
    def __init__(self,session):
        self.session=session

    def agent_status_change_callback(self, agent_execution_id, curr_status, old_status):
        if curr_status=="CREATED" or agent_execution_id is None:
            return
        agent_id=AgentExecution.get_agent_execution_from_id(self.session,agent_execution_id).agent_id
        agent=Agent.get_agent_from_id(self.session,agent_id)
        org=agent.get_agent_organisation(self.session)
        org_webhooks=self.session.query(Webhooks).filter(Webhooks.org_id == org.id).all()

        for webhook_obj in org_webhooks:
            webhook_obj_body={"agent_id":agent_id,"org_id":org.id,"event":f"{old_status} to {curr_status}"}
            error=None
            request=None
            status='sent'
            try:
                request = requests.post(webhook_obj.url.strip(), data=json.dumps(webhook_obj_body), headers=webhook_obj.headers)
            except Exception as e:
                logger.error(f"Exception occured in webhooks {e}")
                error=str(e)
            if request is not None and request.status_code not in [200,201] and error is None:
                error=request.text
            if error is not None:
                status='Error'
            webhook_event=WebhookEvents(agent_id=agent_id, run_id=agent_execution_id, event=f"{old_status} to {curr_status}", status=status, errors=error)
            self.session.add(webhook_event)
            self.session.commit()

