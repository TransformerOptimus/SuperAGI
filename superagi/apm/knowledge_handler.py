from sqlalchemy.orm import Session
from superagi.models.events import Event
from superagi.models.knowledges import Knowledges
from sqlalchemy import Integer, or_, label, case, and_
from fastapi import HTTPException
from typing import List, Dict, Union, Any
from sqlalchemy.sql import func
from sqlalchemy.orm import aliased
from superagi.models.agent_config import AgentConfiguration
import pytz
from datetime import datetime


class KnowledgeHandler:
    def __init__(self, session: Session, organisation_id: int):
        self.session = session
        self.organisation_id = organisation_id


    def get_knowledge_usage_by_name(self, knowledge_name: str) -> Dict[str, Dict[str, int]]:

        is_knowledge_valid = self.session.query(Knowledges.id).filter_by(name=knowledge_name).filter(Knowledges.organisation_id == self.organisation_id).first()
        if not is_knowledge_valid:
            raise HTTPException(status_code=404, detail="Knowledge not found")
        EventAlias = aliased(Event)

        knowledge_used_event = self.session.query(
            Event.event_property['knowledge_name'].label('knowledge_name'),
            func.count(Event.agent_id.distinct()).label('knowledge_unique_agents')
        ).filter(
            Event.event_name == 'knowledge_picked',
            Event.org_id == self.organisation_id,
            Event.event_property['knowledge_name'].astext == knowledge_name
        ).group_by(
            Event.event_property['knowledge_name']
        ).first()

        if knowledge_used_event is None:
            return {}

        knowledge_data = {
                'knowledge_unique_agents': knowledge_used_event.knowledge_unique_agents,
                'knowledge_calls': self.session.query(
                    EventAlias
                ).filter(
                    EventAlias.event_property['tool_name'].astext == 'knowledgesearch',
                    EventAlias.event_name == 'tool_used',
                    EventAlias.org_id == self.organisation_id,
                    EventAlias.agent_id.in_(self.session.query(Event.agent_id).filter(
                        Event.event_name == 'knowledge_picked',
                        Event.org_id == self.organisation_id,
                        Event.event_property['knowledge_name'].astext == knowledge_name
                    ))
                ).count()
            }

        return knowledge_data
    

    def get_knowledge_events_by_name(self, knowledge_name: str) -> List[Dict[str, Union[str, int, List[str]]]]:

        is_knowledge_valid = self.session.query(Knowledges.id).filter_by(name=knowledge_name).filter(Knowledges.organisation_id == self.organisation_id).first()

        if not is_knowledge_valid:
            raise HTTPException(status_code=404, detail="Knowledge not found")

        knowledge_events = self.session.query(Event).filter(
            Event.org_id == self.organisation_id,
            Event.event_name == 'knowledge_picked',
            Event.event_property['knowledge_name'].astext == knowledge_name
        ).all()

        knowledge_events = [ke for ke in knowledge_events if 'agent_execution_id' in ke.event_property]

        event_runs = self.session.query(Event).filter(
            Event.org_id == self.organisation_id,
            or_(Event.event_name == 'run_completed', Event.event_name == 'run_iteration_limit_crossed')
        ).all()

        agent_created_events = self.session.query(Event).filter(
            Event.org_id == self.organisation_id,
            Event.event_name == 'agent_created'
        ).all()

        results = []

        for knowledge_event in knowledge_events:
            agent_execution_id = knowledge_event.event_property['agent_execution_id']

            event_run = next((er for er in event_runs if er.agent_id == knowledge_event.agent_id and er.event_property['agent_execution_id'] == agent_execution_id), None)
            agent_created_event = next((ace for ace in agent_created_events if ace.agent_id == knowledge_event.agent_id), None)
            try:
                user_timezone = AgentConfiguration.get_agent_config_by_key_and_agent_id(session=self.session, key='user_timezone', agent_id=knowledge_event.agent_id)
                if user_timezone and user_timezone.value != 'None':
                    tz = pytz.timezone(user_timezone.value)
                else:
                    tz = pytz.timezone('GMT')       
            except AttributeError:
                tz = pytz.timezone('GMT')

            if event_run and agent_created_event:
                actual_time = knowledge_event.created_at.astimezone(tz).strftime("%d %B %Y %H:%M")

                result_dict = {
                    'agent_execution_id': agent_execution_id,
                    'created_at': actual_time,
                    'tokens_consumed': event_run.event_property['tokens_consumed'],
                    'calls': event_run.event_property['calls'],
                    'agent_execution_name': event_run.event_property['name'],
                    'agent_name': agent_created_event.event_property['agent_name'],
                    'model': agent_created_event.event_property['model']
                }
                if agent_execution_id not in [i['agent_execution_id'] for i in results]:
                    results.append(result_dict)

        results = sorted(results, key=lambda x: datetime.strptime(x['created_at'], '%d %B %Y %H:%M'), reverse=True)
        return results