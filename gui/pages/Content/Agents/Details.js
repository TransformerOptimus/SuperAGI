import React, {useState} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";

export default function Details({agent}) {
  const info_text = {
    marginLeft:'7px',
  }
  
  return (<>
    <div className={styles.history_box} style={{background:'#272335',padding:'20px',cursor:'default',height:'100%',overflowY:'scroll'}}>
      <div className={styles.detail_name}>{agent.name}</div>
      <div>{agent.description}</div>
      <div className={styles.separator}></div>
      <div className={styles.separator}></div>
      <div className={styles.agent_info_box}>
        <div><Image width={15} height={15} src="/images/tools_dark.png" alt="tools-icon"/></div>
        <div style={info_text}>Tools assigned</div>
      </div>
      <div className={styles.separator}></div>
      <div className={styles.agent_info_box}>
        <div><Image width={15} height={15} src="/images/flag.png" alt="goals-icon"/></div>
        <div style={info_text}>{agent.goals.length} Goals</div>
      </div>
      <div className={styles.agent_info_box}>
        <div><Image width={15} height={15} src="/images/fact_check.png" alt="queue-icon"/></div>
        <div style={info_text}>{agent.task_queue}</div>
      </div>
      <div className={styles.agent_info_box}>
        <div><Image width={15} height={15} src="/images/deployed_code.png" alt="model-icon"/></div>
        <div style={info_text}>{agent.ai_model}</div>
      </div>
      <div className={styles.agent_info_box}>
        <div><Image width={15} height={15} src="/images/cancel_presentation.png" alt="exit-icon"/></div>
        <div style={info_text}>{agent.exit_criterion}</div>
      </div>
      <div className={styles.agent_info_box}>
        <div><Image width={15} height={15} src="/images/close_fullscreen.png" alt="constraint-icon"/></div>
        <div style={info_text}>{agent.constraints.length} Constraints</div>
      </div>
      <div className={styles.agent_info_box}>
        <div><Image width={15} height={15} src="/images/overview.png" alt="window-icon"/></div>
        <div style={info_text}>{agent.window} {agent.window_unit}</div>
      </div>
      <div className={styles.agent_info_box}>
        <div><Image width={15} height={15} src="/images/key.png" alt="permission-icon"/></div>
        <div style={info_text}>{agent.mode}</div>
      </div>
    </div>
  </>)
}