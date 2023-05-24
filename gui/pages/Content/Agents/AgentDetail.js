import React, {useState} from 'react';
import Image from 'next/image';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles from './Agents.module.css';
import ActivityFeed from './ActivityFeed';
import TaskQueue from './TaskQueue';
import RunHistory from "./RunHistory";

export default function AgentDetail({agent}) {
  const [leftPanel, setLeftPanel] = useState('activity_feed')
  const [rightPanel, setRightPanel] = useState('action_console')
  const [history, setHistory] = useState(false)

  return (<>
    <div style={{display:'flex',height:'100%'}}>
      {history && <RunHistory runs={agent.runs} setHistory={setHistory}/>}
      <div style={{width: history ? '40%' : '60%',height:'100%'}}>
        <div className={styles.detail_top}>
          <div style={{display:'flex'}}>
            {!history && <div style={{display:'flex',alignItems:'center',cursor:'pointer'}} onClick={() => setHistory(true)}>
              <Image width={16} height={16} src="/images/history.png" alt="history-icon"/>
            </div>}
            <div style={{display:'flex',alignItems:'center',marginLeft:'2px'}} className={styles.tab_text}>
              <div style={{marginLeft:'7px'}}>run name</div>
            </div>
            <div style={{marginLeft:'7px'}}>
              <button onClick={() => setLeftPanel('activity_feed')} className={styles.tab_button} style={leftPanel === 'activity_feed' ? {background:'#454254'} : {background:'transparent'}}>Activity Feed</button>
            </div>
            <div style={{marginLeft:'7px'}}>
              <button onClick={() => setLeftPanel('task_queue')} className={styles.tab_button} style={leftPanel === 'task_queue' ? {background:'#454254'} : {background:'transparent'}}>Task Queue</button>
            </div>
          </div>
          <div style={{display:'flex'}}>
            <div>
              <button className={styles.run_button}>
                <Image width={14} height={14} src="/images/run_icon.png" alt="run-icon"/>&nbsp;New Run
              </button>
            </div>
          </div>
        </div>
        <div className={styles.detail_body}>
          {leftPanel === 'activity_feed' && <ActivityFeed feeds={agent.feeds} history={history}/>}
          {leftPanel === 'task_queue' && <TaskQueue tasks={agent.tasks} history={history}/>}
        </div>
      </div>
      <div style={{width:'40%',height:'100%'}}>

      </div>
    </div>
    <ToastContainer/>
  </>);
}
