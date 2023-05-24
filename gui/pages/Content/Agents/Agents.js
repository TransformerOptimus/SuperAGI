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
    tools: ['gmail', 'powerpoint', 'jira', 'confluence', 'openai', 'canva'],
    goals: ['goal 1', 'goal 2', 'goal 3', 'goal 4', 'goal 5', 'goal 6'],
    constraints: ['constraint 1', 'constraint 2'],
    task_queue: 'Maintain Task Queue',
    ai_model: 'Open AI - 3.5',
    mode: 'No autonomous (Ask permission for every action)',
    state: "RUNNING",
    contentType: 'Agents',
    window: 10,
    window_unit: 'seconds',
    exit_criterion: 'No exit criterion',
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
    tools: ['gmail', 'powerpoint', 'photoshop', 'maya', 'rhino', 'blender', 'autocad', 'jira', 'vs-code', 'confluence', 'openai', 'canva'],
    goals: ['goal 1', 'goal 2', 'goal 3', 'goal 4'],
    constraints: ['constraint 1', 'constraint 2', 'constraint 3', 'constraint 4', 'constraint 5', 'constraint 6'],
    task_queue: "Don't Maintain Task Queue",
    ai_model: 'Open AI - 4.0',
    mode: 'Semi-autonomous',
    state: "PENDING",
    contentType: 'Agents',
    window: 2,
    window_unit: 'minutes',
    exit_criterion: 'System defined',
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
    tools: ['photoshop', 'maya', 'rhino', 'blender', 'autocad', 'jira'],
    goals: ['goal 1', 'goal 2', 'goal 3'],
    constraints: ['constraint 1', 'constraint 2', 'constraint 3', 'constraint 4'],
    task_queue: 'Maintain Task Queue',
    ai_model: 'Open AI - 3.0',
    mode: 'God Mode (fully autonomous)',
    state: "PENDING",
    contentType: 'Agents',
    window: 50,
    window_unit: 'seconds',
    exit_criterion: 'Number of steps/tasks',
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
