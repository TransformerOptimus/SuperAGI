import React, {useState} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import Head from 'next/head';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function TaskQueue() {
  const [task_title, setTaskTitle] = useState("")
  const [taskList, setTask] = useState([])

  const handleTaskTitleChange = (event) => {
    setTaskTitle(event.target.value);
  };

  const handleTaskCreate = (task_title) => {
    if(task_title.replace(/\s/g, '') === '') {
      toast.error("Task is empty", {autoClose: 1800});
      return
    }

    const newTask = {title: task_title};
    setTask((prevArray) => [...prevArray, newTask]);
    toast.success("New task created", {autoClose: 1800});
    setTaskTitle("");
  };

  return (<>
    <Head>
      {/* eslint-disable-next-line @next/next/no-page-custom-font */}
      <link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro&display=swap" rel="stylesheet"/>
    </Head>
    <div>
      <div className={styles.custom_task_box} style={{background:'#272335'}}>
        <div>Add Custom Task</div>
        <div style={{margin:'10px 0',display:'flex',alignItems:'center',justifyContent:'space-between'}}>
          <div style={{flex:'1'}}><input className="input_medium" type="text" value={task_title} onChange={handleTaskTitleChange}/></div>
          <div>
            <button onClick={() => handleTaskCreate(task_title)} className={styles.agent_button} style={{marginLeft:'10px',padding:'5px 7px'}}>
              <Image width={16} height={16} src="/images/add.svg" alt="add-icon"/>
            </button>
          </div>
        </div>
      </div>
      {taskList.map((task, index) => (<div key={index} className={styles.history_box} style={{background:'#272335',padding:'20px',cursor:'default'}}>
        <div style={{display:'flex'}}>
          <div className={styles.feed_icon}>🌟</div>
          <div className={styles.feed_title}>{task.title}</div>
        </div>
      </div>))}
    </div>
    <ToastContainer/>
  </>)
}