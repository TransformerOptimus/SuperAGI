import React, {useState, useEffect} from 'react';
import Image from "next/image";
import styles from './Agents.module.css';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { EventBus } from "@/utils/eventBus";

export default function Agents({sendAgentData}) {
  const agentArray = [{
    id: 0,
    project_id: 1,
    name: "agent name 1",
    description: "shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings",
    tools: ['gmail', 'powerpoint', 'jira', 'confluence', 'openai', 'canva'],
    goal: ['goal 1', 'goal 2', 'goal 3', 'goal 4', 'goal 5', 'goal 6'],
    constraints: ['constraint 1', 'constraint 2'],
    agent_type: "Maintain Task Queue",
    model: 'Open AI - 3.5',
    permission_type: 'No autonomous (Ask permission_type for every action)',
    state: "RUNNING",
    contentType: 'Agents',
    window: 10,
    window_unit: 'seconds',
    exit: 'No exit criterion',
    LTM_DB: "Pinecone",
    runs: [
      { id: 0, name: 'Third Run', is_running: true, calls: 150, last_active: 100, notification_count: 4,
        tasks: [
          { title: "Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
          { title: "Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
        ],
        feeds: [
          {
            status: "new",
            title: "Added task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : ""
          },
          {
            status: "working",
            title: "Working on task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "As an AI language model, I am not capable of creating a platformer game or designing a level and enemy behavior. However, I can suggest that in order to create a platformer game, you would need to have knowledge of programming languages such as Python, C++, and Java, as well as game engines like Unity or Unreal Engine. Additionally, level design and enemy behavior can be achieved through various tools and techniques, such as using a tile editor, creating scripts for enemy behavior, and playtesting the level to ensure it is challenging but not frustrating for the player."
          },
          {
            status: "completed",
            title: "Completed task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression. I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression."
          },
          {
            status: "new",
            title: "Added task 2: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : ""
          },
          {
            status: "working",
            title: "Working on task 2: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "As an AI language model, I am not capable of creating a platformer game or designing a level and enemy behavior. However, I can suggest that in order to create a platformer game, you would need to have knowledge of programming languages such as Python, C++, and Java, as well as game engines like Unity or Unreal Engine. Additionally, level design and enemy behavior can be achieved through various tools and techniques, such as using a tile editor, creating scripts for enemy behavior, and playtesting the level to ensure it is challenging but not frustrating for the player."
          },
        ],
      },
      { id: 1, name: 'Second Run', is_running: false, calls: 200, last_active: 200, notification_count: 0,
        tasks: [
          { title: "Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
        ],
        feeds: [
          {
            status: "new",
            title: "Added task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : ""
          },
          {
            status: "working",
            title: "Working on task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "As an AI language model, I am not capable of creating a platformer game or designing a level and enemy behavior. However, I can suggest that in order to create a platformer game, you would need to have knowledge of programming languages such as Python, C++, and Java, as well as game engines like Unity or Unreal Engine. Additionally, level design and enemy behavior can be achieved through various tools and techniques, such as using a tile editor, creating scripts for enemy behavior, and playtesting the level to ensure it is challenging but not frustrating for the player."
          },
          {
            status: "completed",
            title: "Completed task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression. I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression."
          }
        ],
      },
      { id: 2, name: 'First Run', is_running: false, calls: 250, last_active: 300, notification_count: 0,
        tasks: [
          { title: "Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
        ],
        feeds: [
          {
            status: "new",
            title: "Added task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : ""
          },
          {
            status: "working",
            title: "Working on task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "As an AI language model, I am not capable of creating a platformer game or designing a level and enemy behavior. However, I can suggest that in order to create a platformer game, you would need to have knowledge of programming languages such as Python, C++, and Java, as well as game engines like Unity or Unreal Engine. Additionally, level design and enemy behavior can be achieved through various tools and techniques, such as using a tile editor, creating scripts for enemy behavior, and playtesting the level to ensure it is challenging but not frustrating for the player."
          },
          {
            status: "completed",
            title: "Completed task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression. I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression."
          }
        ],
      },
    ]
  }, {
    id: 1,
    project_id: 1,
    name: "agent name 2",
    description: "shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings",
    tools: ['gmail', 'powerpoint', 'photoshop', 'maya', 'rhino', 'blender', 'autocad', 'jira', 'vs-code', 'confluence', 'openai', 'canva'],
    goal: ['goal 1', 'goal 2', 'goal 3', 'goal 4'],
    constraints: ['constraint 1', 'constraint 2', 'constraint 3', 'constraint 4', 'constraint 5', 'constraint 6'],
    agent_type: "Don't Maintain Task Queue",
    model: 'Open AI - 4.0',
    permission_type: 'God Mode (fully autonomous)',
    state: "RUNNING",
    contentType: 'Agents',
    window: 2,
    window_unit: 'minutes',
    exit: 'System defined',
    LTM_DB: "Pinecone",
    runs: [
      { id: 0, name: 'First Run', is_running: true, calls: 150, last_active: 100, notification_count: 3,
        tasks: [],
        feeds: [
          {
            status: "new",
            title: "Added task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : ""
          },
          {
            status: "working",
            title: "Working on task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "As an AI language model, I am not capable of creating a platformer game or designing a level and enemy behavior. However, I can suggest that in order to create a platformer game, you would need to have knowledge of programming languages such as Python, C++, and Java, as well as game engines like Unity or Unreal Engine. Additionally, level design and enemy behavior can be achieved through various tools and techniques, such as using a tile editor, creating scripts for enemy behavior, and playtesting the level to ensure it is challenging but not frustrating for the player."
          },
          {
            status: "completed",
            title: "Completed task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression. I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression."
          },
          {
            status: "new",
            title: "Added task 2: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : ""
          },
          {
            status: "working",
            title: "Working on task 2: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "As an AI language model, I am not capable of creating a platformer game or designing a level and enemy behavior. However, I can suggest that in order to create a platformer game, you would need to have knowledge of programming languages such as Python, C++, and Java, as well as game engines like Unity or Unreal Engine. Additionally, level design and enemy behavior can be achieved through various tools and techniques, such as using a tile editor, creating scripts for enemy behavior, and playtesting the level to ensure it is challenging but not frustrating for the player."
          },
          {
            status: "completed",
            title: "Completed task 2: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression. I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression."
          },
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
        ],
      },
    ]
  }, {
    id: 2,
    project_id: 1,
    name: "agent name 3",
    description: "shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings",
    tools: ['photoshop', 'maya', 'rhino', 'blender', 'autocad', 'jira'],
    goal: ['goal 1', 'goal 2', 'goal 3'],
    constraints: ['constraint 1', 'constraint 2', 'constraint 3', 'constraint 4'],
    agent_type: "Don't Maintain Task Queue",
    model: 'Open AI - 3.0',
    permission_type: 'God Mode (fully autonomous)',
    state: "PENDING",
    contentType: 'Agents',
    window: 50,
    window_unit: 'seconds',
    exit: 'Number of steps/tasks',
    LTM_DB: "Pinecone",
    runs: [
      { id: 0, name: 'Second Run', is_running: false, calls: 150, last_active: 100, notification_count: 0,
        tasks: [
          { title: "Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
          { title: "Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
        ],
        feeds: [
          {
            status: "new",
            title: "Added task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : ""
          },
          {
            status: "working",
            title: "Working on task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "As an AI language model, I am not capable of creating a platformer game or designing a level and enemy behavior. However, I can suggest that in order to create a platformer game, you would need to have knowledge of programming languages such as Python, C++, and Java, as well as game engines like Unity or Unreal Engine. Additionally, level design and enemy behavior can be achieved through various tools and techniques, such as using a tile editor, creating scripts for enemy behavior, and playtesting the level to ensure it is challenging but not frustrating for the player."
          },
          {
            status: "completed",
            title: "Completed task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression. I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression."
          },
          {
            status: "new",
            title: "Added task 2: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : ""
          },
          {
            status: "working",
            title: "Working on task 2: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "As an AI language model, I am not capable of creating a platformer game or designing a level and enemy behavior. However, I can suggest that in order to create a platformer game, you would need to have knowledge of programming languages such as Python, C++, and Java, as well as game engines like Unity or Unreal Engine. Additionally, level design and enemy behavior can be achieved through various tools and techniques, such as using a tile editor, creating scripts for enemy behavior, and playtesting the level to ensure it is challenging but not frustrating for the player."
          },
          {
            status: "completed",
            title: "Completed task 2: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression. I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression."
          }
        ],
      },
      { id: 1, name: 'First Run', is_running: false, calls: 200, last_active: 200, notification_count: 0,
        tasks: [
          { title: "Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game." },
        ],
        feeds: [
          {
            status: "new",
            title: "Added task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : ""
          },
          {
            status: "working",
            title: "Working on task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "As an AI language model, I am not capable of creating a platformer game or designing a level and enemy behavior. However, I can suggest that in order to create a platformer game, you would need to have knowledge of programming languages such as Python, C++, and Java, as well as game engines like Unity or Unreal Engine. Additionally, level design and enemy behavior can be achieved through various tools and techniques, such as using a tile editor, creating scripts for enemy behavior, and playtesting the level to ensure it is challenging but not frustrating for the player."
          },
          {
            status: "completed",
            title: "Completed task 1: Design and implement graphics for obstacles and enemies to match the overall aesthetic of the game.",
            description : "I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression. I will write code to create a platformer game. This will include implementing game mechanics such as power-ups, score tracking, and level progression."
          },
        ],
      },
    ]
  }];

  const [agents, setAgents] = useState(agentArray);

  useEffect(() => {
    const createRun = (eventData) => {
      const updatedAgentId = eventData.agentId;
      const newRun = eventData.newRun;
      const updatedGoals = eventData.updatedGoals;

      const updatedAgents = agents.map((agent) => {
        if (agent.id === updatedAgentId) {
          const updatedAgent = {
            ...agent,
            goal: updatedGoals,
            runs: [...agent.runs, newRun],
          };
          sendAgentData(updatedAgent);
          return updatedAgent;
        }
        return agent;
      });

      setAgents(updatedAgents);
    };

    EventBus.on('runCreate', createRun);

    return () => {
      EventBus.off('runCreate', createRun);
    };
  }, [agents]);

  return (
    <>
      <div className={styles.container}>
        <div className={styles.title_box}>
          <p className={styles.title_text}>Agents</p>
        </div>
        <div className={styles.wrapper} style={{marginBottom:'10px',marginTop:'4px'}}>
          <button style={{width:'100%'}} className={styles.agent_button} onClick={() => sendAgentData({ id: -1, name: "new agent", contentType: "Create_Agent" })}>
            + Create Agent
          </button>
        </div>
        <div className={styles.wrapper}>
          {agents.map((agent, index) => (
            <div key={index}>
              <div className={styles.agent_box} onClick={() => sendAgentData(agent)}>
                {agent.state === 'RUNNING' && <div className={styles.agent_active}><Image width={8} height={8} src="/images/active_icon.png" alt="active-icon"/></div>}
                <div><span className={styles.agent_text}>{agent.name}</span></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    <ToastContainer/>
  </>
  );
}
