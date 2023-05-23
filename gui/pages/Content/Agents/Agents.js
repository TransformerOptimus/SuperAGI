import React, {useState} from 'react';
import Image from "next/image";
import styles from './Agents.module.css';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function Agents({sendAgentData}) {
  const agentArray = [{
    id: 0,
    name: "agent name 1",
    description: "shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings",
    tools: ['gmailer', 'jira-v2', 'openai'],
    last_active: 180,
    isEditing: false,
    ongoing_runs: 4,
    goals: 8,
    task_queue: 'Main',
    model: 'Open AI - 3.5',
    mode: 'God Mode',
    state: "RUNNING",
  }, {
    id: 1,
    name: "agent name 2",
    description: "shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings",
    tools: ['gmailer', 'jira-v2', 'openai', 'superagi'],
    last_active: 120,
    isEditing: false,
    ongoing_runs: 4,
    goals: 8,
    task_queue: 'Main',
    model: 'Open AI - 3.5',
    mode: 'God Mode',
    state: "PENDING",
  }, {
    id: 2,
    name: "agent name 3",
    description: "shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings",
    tools: ['gmailer', 'jira-v2', 'superagi'],
    last_active: 150,
    isEditing: false,
    ongoing_runs: 4,
    goals: 8,
    task_queue: 'Main',
    model: 'Open AI - 3.5',
    mode: 'God Mode',
    state: "PENDING",
  }];

  const [agents, setAgents] = useState(agentArray);

  const handleNewAgent = () => {
    const newAgent = {
      id: agentArray.length,
      name: "new agent",
      description: "",
      tools: [],
      last_active: 0,
      isEditing: false,
      ongoing_runs: 0,
      goals: 0,
      task_queue: "",
      model: "",
      mode: "",
      state: "DRAFT",
    };

    setAgents([...agents, newAgent]);
    sendAgentData(newAgent);
  }

  return (
    <>
      <div className={styles.container}>
        <div className={styles.title_box}>
          <p className={styles.title_text}>Agents</p>
        </div>
        <div className={styles.wrapper} style={{marginBottom:'10px',marginTop:'3px'}}>
          <button style={{width:'100%'}} className={styles.agent_button} onClick={handleNewAgent}>
            + Create Agent
          </button>
        </div>
        <div className={styles.wrapper}>
          {agents.map((agent, index) => (
            <div key={index}>
              {agent.state !== 'DRAFT' && <div className={styles.agent_box} onClick={() => sendAgentData(agent)}>
                {agent.state === 'RUNNING' && <div className={styles.agent_active}><Image width={8} height={8} src="/images/active_icon.png" alt="active-icon"/></div>}
                <div><span className={styles.agent_text}>{agent.name}</span></div>
              </div>}
            </div>
          ))}
        </div>
      </div>
    <ToastContainer/>
  </>
  );
}
