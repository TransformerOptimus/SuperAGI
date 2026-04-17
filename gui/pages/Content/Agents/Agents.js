import React, {useMemo, useState} from 'react';
import Image from "next/image";
import 'react-toastify/dist/ReactToastify.css';
import {createInternalId, getUserClick} from "@/utils/utils";
import styles from './Agents.module.css';

const STATUS_FILTERS = {
  ALL: 'all',
  RUNNING: 'running',
  SCHEDULED: 'scheduled',
  IDLE: 'idle',
};

const normalizeName = (name) => (name || '').toString().trim().toLowerCase();

const byPriorityThenName = (firstAgent, secondAgent) => {
  const getPriority = (agent) => {
    if (agent?.is_running) return 0;
    if (agent?.is_scheduled) return 1;
    return 2;
  };

  const priorityDiff = getPriority(firstAgent) - getPriority(secondAgent);
  if (priorityDiff !== 0) return priorityDiff;

  return normalizeName(firstAgent?.name).localeCompare(normalizeName(secondAgent?.name));
};

export default function Agents({sendAgentData, agents}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState(STATUS_FILTERS.ALL);

  const agentCounts = useMemo(() => {
    const sourceAgents = agents || [];
    const running = sourceAgents.filter((agent) => agent?.is_running).length;
    const scheduled = sourceAgents.filter((agent) => !agent?.is_running && agent?.is_scheduled).length;
    const idle = sourceAgents.length - running - scheduled;

    return {
      all: sourceAgents.length,
      running,
      scheduled,
      idle,
    };
  }, [agents]);

  const visibleAgents = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    const sourceAgents = [...(agents || [])].sort(byPriorityThenName);

    return sourceAgents.filter((agent) => {
      const matchesSearch = query === '' || normalizeName(agent?.name).includes(query);
      if (!matchesSearch) return false;

      if (statusFilter === STATUS_FILTERS.RUNNING) return Boolean(agent?.is_running);
      if (statusFilter === STATUS_FILTERS.SCHEDULED) return Boolean(!agent?.is_running && agent?.is_scheduled);
      if (statusFilter === STATUS_FILTERS.IDLE) return Boolean(!agent?.is_running && !agent?.is_scheduled);
      return true;
    });
  }, [agents, searchQuery, statusFilter]);

  const hasAgents = (agents || []).length > 0;

  return (<>
      <div className="container">
        <p className="text_14 mt_8 mb_12 ml_8">Agents</p>
        <div className="w_100 mb_10">
          <button className="secondary_button w_100" onClick={() => {
            sendAgentData({
              id: -1,
              name: "new agent",
              contentType: "Create_Agent",
              internalId: createInternalId()
            }); getUserClick('Agent Create Clicked', {'Click Position': 'Sidebar'})
          }}>
            + Create Agent
          </button>
        </div>

        {hasAgents && (
          <>
            <div className={styles.agent_search_wrap}>
              <input
                type="text"
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                className={styles.agent_search_input}
                placeholder="Search agents"
                aria-label="Search agents"
              />
            </div>
            <div className={styles.agent_filter_row}>
              <button
                type="button"
                className={`${styles.agent_filter_button} ${statusFilter === STATUS_FILTERS.ALL ? styles.agent_filter_button_active : ''}`}
                onClick={() => setStatusFilter(STATUS_FILTERS.ALL)}>
                All ({agentCounts.all})
              </button>
              <button
                type="button"
                className={`${styles.agent_filter_button} ${statusFilter === STATUS_FILTERS.RUNNING ? styles.agent_filter_button_active : ''}`}
                onClick={() => setStatusFilter(STATUS_FILTERS.RUNNING)}>
                Running ({agentCounts.running})
              </button>
              <button
                type="button"
                className={`${styles.agent_filter_button} ${statusFilter === STATUS_FILTERS.SCHEDULED ? styles.agent_filter_button_active : ''}`}
                onClick={() => setStatusFilter(STATUS_FILTERS.SCHEDULED)}>
                Scheduled ({agentCounts.scheduled})
              </button>
              <button
                type="button"
                className={`${styles.agent_filter_button} ${statusFilter === STATUS_FILTERS.IDLE ? styles.agent_filter_button_active : ''}`}
                onClick={() => setStatusFilter(STATUS_FILTERS.IDLE)}>
                Idle ({agentCounts.idle})
              </button>
            </div>
          </>
        )}

        {hasAgents ? <div className="vertical_selection_scroll w_100">
          {visibleAgents.length > 0 ? visibleAgents.map((agent) => (
            <div key={agent.id}>
              <button type="button" className={`agent_box w_100 ${styles.agent_row_button}`} onClick={() => sendAgentData(agent)} aria-label={`Open agent ${agent.name}`}>
                {agent?.is_running && <Image width={14} height={14} className="mix_blend_mode" src="/images/loading.gif" alt="active-icon"/>}
                <div className="text_ellipsis"><span className="agent_text text_ellipsis">{agent.name}</span></div>
                {agent?.is_scheduled && <Image className="ml_4" width={17} height={17} src="/images/event_repeat.svg" alt="check-icon"/>}
              </button>
            </div>
          )) : (
            <div className="form_label mt_20 horizontal_container justify_center">
              No agents match the current filters
            </div>
          )}
        </div> : <div className="form_label mt_20 horizontal_container justify_center">No Agents found</div>}

      </div>
    </>
  );
}
