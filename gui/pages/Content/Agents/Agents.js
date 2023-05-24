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
    goals: ['goal 1', 'goal 2'],
    task_queue: 'Main',
    model: 'Open AI - 3.5',
    mode: 'God Mode',
    state: "RUNNING",
    contentType: 'Agents',
    tasks: [
      { title: "Added task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
      { title: "Added task 2: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
      { title: "Added task 3: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
      { title: "Added task 4: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
      { title: "Added task 5: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
    ],
    feeds: [
      {
        status: "new",
        title: "Added task 3: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
        description : ""
      },
      {
        status: "working",
        title: "Working on task 3: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
        description : "As an AI language model, I am not capable of creating a platformer game or designing a level and enemy behavior. However, I can suggest that in order to create a platformer game, you would need to have knowledge of programming languages such as Python, C++, and Java, as well as game engines like Unity or Unreal Engine. Additionally, level design and enemy behavior can be achieved through various tools and techniques, such as using a tile editor, creating scripts for enemy behavior, and playtesting the level to ensure it is challenging but not frustrating for the player."
      },
      {
        status: "completed",
        title: "Completed task 3: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
        description : "I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression. I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression."
      }
    ],
    runs: [
      { id: 0, name: 'run name', is_running: true, calls: 783, last_active: 120, notification_count: 4 },
      { id: 1, name: 'run name', is_running: false, calls: 783, last_active: 180, notification_count: 0 },
      { id: 2, name: 'run name', is_running: true, calls: 783, last_active: 150, notification_count: 2 },
      { id: 3, name: 'run name', is_running: false, calls: 783, last_active: 300, notification_count: 0 },
      { id: 4, name: 'run name', is_running: false, calls: 783, last_active: 270, notification_count: 0 },
      { id: 5, name: 'run name', is_running: false, calls: 783, last_active: 360, notification_count: 0 },
      { id: 6, name: 'run name', is_running: true, calls: 783, last_active: 450, notification_count: 1 },
      { id: 7, name: 'run name', is_running: false, calls: 783, last_active: 150, notification_count: 0 },
      { id: 8, name: 'run name', is_running: false, calls: 783, last_active: 270, notification_count: 0 },
    ]
  }, {
    id: 1,
    name: "agent name 2",
    description: "shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings",
    tools: ['gmailer', 'jira-v2', 'openai', 'superagi'],
    last_active: 120,
    isEditing: false,
    ongoing_runs: 4,
    goals: ['goal 1', 'goal 2'],
    task_queue: 'Main',
    model: 'Open AI - 3.5',
    mode: 'God Mode',
    state: "PENDING",
    contentType: 'Agents',
    tasks: [
      { title: "Added task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
      { title: "Added task 2: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
      { title: "Added task 3: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
      { title: "Added task 4: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
      { title: "Added task 5: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
    ],
    feeds: [
      {
        status: "new",
        title: "Added task 3: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
        description : ""
      },
      {
        status: "working",
        title: "Working on task 3: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
        description : "As an AI language model, I am not capable of creating a platformer game or designing a level and enemy behavior. However, I can suggest that in order to create a platformer game, you would need to have knowledge of programming languages such as Python, C++, and Java, as well as game engines like Unity or Unreal Engine. Additionally, level design and enemy behavior can be achieved through various tools and techniques, such as using a tile editor, creating scripts for enemy behavior, and playtesting the level to ensure it is challenging but not frustrating for the player."
      },
      {
        status: "completed",
        title: "Completed task 3: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
        description : "I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression. I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression."
      }
    ],
    runs: [
      { id: 0, name: 'run name', is_running: true, calls: 783, last_active: 120, notification_count: 4 },
      { id: 1, name: 'run name', is_running: false, calls: 783, last_active: 180, notification_count: 0 },
      { id: 2, name: 'run name', is_running: true, calls: 783, last_active: 150, notification_count: 2 },
      { id: 3, name: 'run name', is_running: false, calls: 783, last_active: 300, notification_count: 0 },
      { id: 4, name: 'run name', is_running: false, calls: 783, last_active: 270, notification_count: 0 },
      { id: 5, name: 'run name', is_running: false, calls: 783, last_active: 360, notification_count: 0 },
      { id: 6, name: 'run name', is_running: true, calls: 783, last_active: 450, notification_count: 1 },
      { id: 7, name: 'run name', is_running: false, calls: 783, last_active: 150, notification_count: 0 },
      { id: 8, name: 'run name', is_running: false, calls: 783, last_active: 270, notification_count: 0 },
    ]
  }, {
    id: 2,
    name: "agent name 3",
    description: "shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings",
    tools: ['gmailer', 'jira-v2', 'superagi'],
    last_active: 150,
    isEditing: false,
    ongoing_runs: 4,
    goals: ['goal 1', 'goal 2'],
    task_queue: 'Main',
    model: 'Open AI - 3.5',
    mode: 'God Mode',
    state: "PENDING",
    contentType: 'Agents',
    tasks: [
      { title: "Added task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
      { title: "Added task 2: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
      { title: "Added task 3: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
      { title: "Added task 4: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
      { title: "Added task 5: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
    ],
    feeds: [
      {
        status: "new",
        title: "Added task 3: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
        description : ""
      },
      {
        status: "working",
        title: "Working on task 3: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
        description : "As an AI language model, I am not capable of creating a platformer game or designing a level and enemy behavior. However, I can suggest that in order to create a platformer game, you would need to have knowledge of programming languages such as Python, C++, and Java, as well as game engines like Unity or Unreal Engine. Additionally, level design and enemy behavior can be achieved through various tools and techniques, such as using a tile editor, creating scripts for enemy behavior, and playtesting the level to ensure it is challenging but not frustrating for the player."
      },
      {
        status: "completed",
        title: "Completed task 3: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
        description : "I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression. I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression."
      }
    ],
    runs: [
      { id: 0, name: 'run name', is_running: true, calls: 783, last_active: 120, notification_count: 4 },
      { id: 1, name: 'run name', is_running: false, calls: 783, last_active: 180, notification_count: 0 },
      { id: 2, name: 'run name', is_running: true, calls: 783, last_active: 150, notification_count: 2 },
      { id: 3, name: 'run name', is_running: false, calls: 783, last_active: 300, notification_count: 0 },
      { id: 4, name: 'run name', is_running: false, calls: 783, last_active: 270, notification_count: 0 },
      { id: 5, name: 'run name', is_running: false, calls: 783, last_active: 360, notification_count: 0 },
      { id: 6, name: 'run name', is_running: true, calls: 783, last_active: 450, notification_count: 1 },
      { id: 7, name: 'run name', is_running: false, calls: 783, last_active: 150, notification_count: 0 },
      { id: 8, name: 'run name', is_running: false, calls: 783, last_active: 270, notification_count: 0 },
    ]
  }];

  const [agents, setAgents] = useState(agentArray);

  const handleNewAgent = () => {
    const newAgent = {
      id: agentArray.length,
      name: "new agent",
      description: "shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings",
      tools: ['gmailer'],
      last_active: 0,
      isEditing: false,
      ongoing_runs: 0,
      goals: ['goal 1', 'goal 2'],
      task_queue: "",
      model: "Open AI - 3.5",
      mode: "",
      state: "DRAFT",
      contentType: 'Agents'
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
        <div className={styles.wrapper} style={{marginBottom:'10px',marginTop:'4px'}}>
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
