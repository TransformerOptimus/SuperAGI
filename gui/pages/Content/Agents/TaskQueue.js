import React, {useState} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import Head from 'next/head';

export default function TaskQueue({tasks}) {
  const [task_title, setTaskTitle] = useState("")

  return (<>
    <Head>
      <link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro&display=swap" rel="stylesheet"/>
    </Head>
    <div>
      <div className={styles.custom_task_box} style={{background:'#272335'}}>
        <div>Add Custom Task</div>
        <div style={{margin:'10px 0',display:'flex',alignItems:'center',justifyContent:'space-between'}}>
          <div style={{flex:'1'}}><input className="input_medium" type="text" value={task_title} onChange={() => setTaskTitle(task_title)}/></div>
          <div>
            <button className={styles.agent_button} style={{marginLeft:'10px',padding:'5px 7px'}}>
              <Image width={16} height={16} src="/images/add.png" alt="add-icon"/>
            </button>
          </div>
        </div>
      </div>
      {tasks.map((task, index) => (<div key={index} className={styles.history_box} style={{background:'#272335',padding:'20px',cursor:'default'}}>
        <div style={{display:'flex'}}>
          <div className={styles.feed_icon}>🌟</div>
          <div className={styles.feed_title}>{task.title}</div>
        </div>
      </div>))}
    </div>
  </>)
}