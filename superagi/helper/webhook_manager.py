from superagi.models.agent import Agent
from superagi.models.agent_execution import AgentExecution
from superagi.models.web_hooks import WebHooks
from superagi.models.web_hook_events import WebHookEvents
import requests
import json
from superagi.lib.logger import logger
class WebHookManager:
    def __init__(self,session):
        self.session=session

    def agentStatusChangeCallback(self,agent_execution_id, val,old_val):
        if val=="CREATED" or agent_execution_id is None:
            return
        agent_id=AgentExecution.get_agent_execution_from_id(self.session,agent_execution_id).agent_id
        agent=Agent.get_agent_from_id(self.session,agent_id)
        org=agent.get_agent_organisation(self.session)
        org_id=org.id
        org_webhooks=self.session.query(WebHooks).filter(org_id==org_id).all()
        print("**********",org_webhooks)

        for webhook_obj in org_webhooks:
            webhook_obj_body={"agent_id":agent_id,"org_id":org_id,"event":f"{old_val} to {val}"}
            error=None
            r=None
            status='sent'
            try:
                r = requests.post(webhook_obj.url.strip(), data=json.dumps(webhook_obj_body), headers=webhook_obj.headers)
            except Exception as e:
                logger.error(f"Exception occured in webhooks {e}")
                error=str(e)
            print(error,'************(((((((')
            if r.status_code not in [200,201] and error is None:
                error=r.text
            if error is not None:
                status='Error'
            web_hook_event=WebHookEvents(agent_id=agent_id,run_id=agent_execution_id,event=f"{old_val} to {val}",status=status,errors=error)
            self.session.add(web_hook_event)
            self.session.commit()
        return

    # def send_post_req(self,url,headers,body):
    #     try:
    #         r = requests.post(url, data=json.dumps(body), headers=headers)
    #     except Exception as e:
    #         logger.error(f"Exception occured in webhooks {e}")
    #     return
    