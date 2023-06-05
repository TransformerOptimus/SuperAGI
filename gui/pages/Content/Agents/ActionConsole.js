import React from 'react';
import styles from './Agents.module.css';
import Image from "next/image";

export default function ActionConsole() {
  const actions = [
    {
      title: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
      type: "text",
      timeStamp: "2min ago"
    },
    {
      title: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam.",
      type: "boolean",
      timeStamp: "2min ago"
    },
    {
      title: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
      type: "text",
      timeStamp: "2min ago"
    },
    {
      title: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam.",
      type: "boolean",
      timeStamp: "2min ago"
    },
    {
      title: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
      type: "text",
      timeStamp: "2min ago"
    },
    {
      title: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam.",
      type: "boolean",
      timeStamp: "2min ago"
    }
  ]

  return (<>
    <div className={styles.detail_body} style={{height:'auto'}}>
      {actions.map((action, index) => (<div key={index} className={styles.history_box} style={{background:'#272335',padding:'15px',cursor:'default'}}>
        {action.type === "notification" && <div>
          <div>{action.title}</div>
        </div>}
        {action.type === "boolean" && <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
          <div style={{flex:'1'}}>{action.title}</div>
          <div>
            <button className={styles.agent_button} style={{marginLeft:'4px',padding:'5px',background:'transparent',border:'none'}}>
              <Image width={20} height={21} src="/images/close.svg" alt="close-icon"/>
            </button>
          </div>
          <div>
            <button className={styles.agent_button} style={{marginLeft:'4px',padding:'5px'}}>
              <Image width={20} height={21} src="/images/check.svg" alt="check-icon"/>
            </button>
          </div>
        </div>}
        {action.type === "text" && <div>
          <div>{action.title}</div>
          <div style={{marginTop:'10px',display:'flex',alignItems:'center',justifyContent:'space-between'}}>
            <div style={{flex:'1'}}><input className="input_medium" type="text"/></div>
            <div>
              <button className={styles.agent_button} style={{marginLeft:'4px',padding:'5px',background:'transparent',border:'none'}}>
                <Image width={20} height={21} src="/images/close.svg" alt="close-icon"/>
              </button>
            </div>
            <div>
              <button className={styles.agent_button} style={{marginLeft:'4px',padding:'5px'}}>
                <Image width={20} height={21} src="/images/send.svg" alt="send-icon"/>
              </button>
            </div>
          </div>
        </div>}
        <div style={{display:'flex',alignItems:'center',paddingLeft:'0',paddingBottom:'0'}} className={styles.tab_text}>
          <div>
            <Image width={12} height={12} src="/images/schedule.svg" alt="schedule-icon"/>
          </div>
          <div className={styles.history_info}>{action.timeStamp}</div>
        </div>
      </div>))}
    </div>
  </>)
}