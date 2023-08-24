from sqlalchemy.orm import Session
from collections import defaultdict
from superagi.models.events import Event
from superagi.models.knowledges import Knowledges
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from sqlalchemy import Integer
from fastapi import HTTPException
from typing import List, Dict


class KnowledgeHandler:
    def __init__(self, session: Session, organisation_id: int):
        self.session = session
        self.organisation_id = organisation_id

    def get_knowledge_usage(self) -> Dict[str, Dict[str, int]]:

        knowledge_dict = {}

        knowledge_data = self.session.query(Knowledges.id, Knowledges.name, Event.org_id == self.organisation_id).all()
        for data in knowledge_data:
            knowledge_dict[str(data.id)] = data.name

        knowledge_calls = defaultdict(int)
        knowledge_agents = defaultdict(set)
        agent_tool_map = defaultdict(list)

        tool_used_events = self.session.query(
            Event.agent_id,
            Event.event_property['tool_name'].label('tool_name')
        ).filter(Event.event_name == 'tool_used', Event.org_id == self.organisation_id)

        for event in tool_used_events:
            agent_tool_map[event.agent_id].append(event.tool_name)

        agent_knowledge_map = {}

        knowledge_configurations = self.session.query(
            AgentExecutionConfiguration.agent_execution_id,
            AgentExecutionConfiguration.value.label('knowledge_id')
        ).filter(AgentExecutionConfiguration.key == 'knowledge',
                AgentExecutionConfiguration.value.isnot(None))
        
        for config in knowledge_configurations:
            agent_knowledge_map[config.agent_execution_id] = config.knowledge_id

        run_completed_events = self.session.query(
            Event.agent_id,
            Event.event_property['calls'].cast(Integer).label('calls'),
            Event.event_property['agent_execution_id'].cast(Integer).label('execution_id')
        ).filter(Event.event_name.in_(['run_completed', 'run_iteration_limit_crossed']), Event.org_id == self.organisation_id)

        for event in run_completed_events:
            if event.execution_id in agent_knowledge_map:
                knowledge_id = agent_knowledge_map[event.execution_id]
                knowledge_name = knowledge_dict.get(knowledge_id, knowledge_id)
                if knowledge_name != 'None':
                    knowledge_calls[knowledge_name] += 1
                    knowledge_agents[knowledge_name].add(event.agent_id)

        knowledge_agents_count = {k: len(v) for k, v in knowledge_agents.items()}

        return {
            'knowledge_calls': dict(knowledge_calls),
            'knowledge_unique_agents': knowledge_agents_count
        }
    

    def get_knowledge_logs_by_name(self, knowledge_name: str):
        knowledge_ids = self.session.query(Knowledges.id).filter_by(name=knowledge_name).filter(Knowledges.organisation_id==self.organisation_id).all()

        if not knowledge_ids:
            raise HTTPException(status_code=404, detail="Knowledge not found")
        
        knowledge_ids = [id_[0] for id_ in knowledge_ids]
        agent_execution_configuration = self.session.query(AgentExecutionConfiguration).filter(AgentExecutionConfiguration.key=='knowledge', AgentExecutionConfiguration.value.in_(map(str, knowledge_ids))).all()
        agent_execution_ids = {config.agent_execution_id for config in agent_execution_configuration}
        
        all_events = self.session.query(Event).filter(Event.org_id == self.organisation_id).all()
        unique_agent_ids = {event.agent_id for event in all_events if event.event_property.get('agent_execution_id', None) in agent_execution_ids}
        
        result_list = []
        for agent_id in unique_agent_ids:
            agent_specific_events = [event for event in all_events if event.agent_id == agent_id]
            agent_dict = {}
            for event in agent_specific_events:
                event_property = event.event_property
                if event.event_name in ('run_completed', 'run_iteration_limit_crossed') and event_property.get('agent_execution_id', None) in agent_execution_ids:
                    agent_dict['tokens_consumed'] = agent_dict.get('tokens_consumed', 0) + event_property.get('tokens_consumed', 0)
                    agent_dict['calls'] = agent_dict.get('calls', 0) + event_property.get('calls', 0)
                    agent_dict['created_at'] = event.created_at
                    agent_dict['event_name'] = event.event_name

                elif event.event_name == 'run_created':
                    agent_dict['agent_execution_name'] = event_property.get('agent_execution_name', '')

                elif event.event_name == 'agent_created':
                    agent_dict['agent_name'] = event_property.get('agent_name', '')
                    agent_dict['model'] = event_property.get('model', '')
            
            if 'created_at' in agent_dict:
                result_list.append(agent_dict)

        return result_list