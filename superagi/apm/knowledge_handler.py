from sqlalchemy.orm import Session
from superagi.models.events import Event
from superagi.models.knowledges import Knowledges
from sqlalchemy import Integer, or_, label, case, and_
from fastapi import HTTPException
from typing import List, Dict, Union, Any
from sqlalchemy.sql import func
from sqlalchemy.orm import aliased


class KnowledgeHandler:
    def __init__(self, session: Session, organisation_id: int):
        self.session = session
        self.organisation_id = organisation_id


    def get_knowledge_wise_usage(self) -> Dict[str, Dict[str, int]]:

        EventAlias = aliased(Event)

        query_data = self.session.query(
            Event.event_property['knowledge_name'].label('knowledge_name'),
            func.count(Event.agent_id.distinct()).label('knowledge_unique_agents')
        ).filter(
            Event.event_name == 'knowledge_picked',
            Event.org_id == self.organisation_id
        ).group_by(
            Event.event_property['knowledge_name']
        ).all()

        return {
            record.knowledge_name: {
                'knowledge_unique_agents': record.knowledge_unique_agents,
                'knowledge_calls': self.session.query(
                    EventAlias
                ).filter(
                    EventAlias.event_property['tool_name'].astext == 'knowledgesearch',
                    EventAlias.event_name == 'tool_used',
                    EventAlias.org_id == self.organisation_id,
                    EventAlias.agent_id.in_(self.session.query(Event.agent_id).filter(
                        Event.event_name == 'knowledge_picked',
                        Event.org_id == self.organisation_id,
                        Event.event_property['knowledge_name'].astext == record.knowledge_name
                    ))
                ).count()
            } for record in query_data
        }
    

    def get_knowledge_events_by_name(self, knowledge_name: str) -> List[Dict[str, Union[str, int]]]:
        
        is_knowledge_valid = self.session.query(Knowledges.id).filter_by(name=knowledge_name).filter(Knowledges.organisation_id == self.organisation_id).first()
        if not is_knowledge_valid:
            raise HTTPException(status_code=404, detail="Knowledge not found")

        event_knowledge_picked = self.session.query(
            Event.agent_id,
            label('created_at', func.max(Event.created_at)),
            label('event_name', func.max(Event.event_name))
        ).filter(
            Event.org_id == self.organisation_id,
            Event.event_name == 'knowledge_picked',
            Event.event_property['knowledge_name'].astext == knowledge_name
        ).group_by(Event.agent_id).subquery()

        event_run = self.session.query(
            Event.agent_id,
            label('tokens_consumed', func.sum(Event.event_property['tokens_consumed'].astext.cast(Integer))),
            label('calls', func.sum(Event.event_property['calls'].astext.cast(Integer)))
        ).filter(
            Event.org_id == self.organisation_id,
            or_(Event.event_name == 'run_completed', Event.event_name == 'run_iteration_limit_crossed')
        ).group_by(Event.agent_id).subquery()

        event_run_created = self.session.query(
            Event.agent_id,
            label('agent_execution_name', func.max(Event.event_property['agent_execution_name'].astext))
        ).filter(
            Event.org_id == self.organisation_id,
            Event.event_name == 'run_created'
        ).group_by(Event.agent_id).subquery()

        event_agent_created = self.session.query(
            Event.agent_id,
            label('agent_name', func.max(Event.event_property['agent_name'].astext)),
            label('model', func.max(Event.event_property['model'].astext))
        ).filter(
            Event.org_id == self.organisation_id,
            Event.event_name == 'agent_created'
        ).group_by(Event.agent_id).subquery()

        result = self.session.query(
            event_knowledge_picked.c.agent_id,
            event_knowledge_picked.c.created_at,
            event_knowledge_picked.c.event_name,
            event_run.c.tokens_consumed,
            event_run.c.calls,
            event_run_created.c.agent_execution_name,
            event_agent_created.c.agent_name,
            event_agent_created.c.model
        ).join(
            event_run, event_knowledge_picked.c.agent_id == event_run.c.agent_id
        ).join(
            event_run_created, event_knowledge_picked.c.agent_id == event_run_created.c.agent_id
        ).join(
            event_agent_created, event_knowledge_picked.c.agent_id == event_agent_created.c.agent_id
        ).all()

        return [{
            'agent_id': row.agent_id,
            'created_at': row.created_at,
            'event_name': row.event_name,
            'tokens_consumed': row.tokens_consumed,
            'calls': row.calls,
            'agent_execution_name': row.agent_execution_name,
            'agent_name': row.agent_name,
            'model': row.model
        } for row in result]