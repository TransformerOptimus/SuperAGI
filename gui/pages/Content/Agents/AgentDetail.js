import React, {useState} from 'react';
import Image from 'next/image';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles from './Agents.module.css';

export default function AgentDetail({agent}) {
  const [leftPanel, setLeftPanel] = useState('activity_feed')
  const [history, setHistory] = useState(false)

  return (<>
    <div>
      <div style={{width:'50%',height:'100%'}}>
        <div className={styles.detail_top}>
          <div style={{display:'flex'}}>
            <div style={{display:'flex',alignItems:'center'}} onClick={() => setHistory(!history)}>
              <Image width={16} height={16} src="/images/history.png" alt="history-icon"/>
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
                <Image width={14} height={14} src="/images/run_icon.png" alt="run-icon"/>New Run
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <ToastContainer/>
  </>);
}
