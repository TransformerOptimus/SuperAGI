import React, {useEffect, useState} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {getExecutionTasks} from "@/pages/api/DashboardService";

export default function TaskQueue({selectedRunId}) {
  const [task_title, setTaskTitle] = useState("")
  const [taskList, setTasks] = useState([])
  const [completedTaskList, setCompletedTasks] = useState([])

  const handleTaskTitleChange = (event) => {
    setTaskTitle(event.target.value);
  };

  const handleTaskCreate = (task_title) => {
    if(task_title.replace(/\s/g, '') === '') {
      toast.error("Task is empty", {autoClose: 1800});
      return
    }

    const newTask = {title: task_title};
    setTasks((prevArray) => [...prevArray, newTask]);
    toast.success("New task created", {autoClose: 1800});
    setTaskTitle("");
  };

  useEffect(() => {
    fetchTasks();
  }, [selectedRunId])

  function fetchTasks() {
    getExecutionTasks(selectedRunId)
      .then((response) => {
        setTasks(response.data.tasks);
        setCompletedTasks(response.data.completed_tasks);
      })
      .catch((error) => {
        console.error('Error fetching execution feeds:', error);
      });
  }
  return (<>
    <div>
      {/*<div className={styles.custom_task_box} style={{background:'#272335'}}>*/}
      {/*  <div>Add Custom Task</div>*/}
      {/*  <div style={{margin:'10px 0',display:'flex',alignItems:'center',justifyContent:'space-between'}}>*/}
      {/*    <div style={{flex:'1'}}><input className="input_medium" type="text" value={task_title} onChange={handleTaskTitleChange}/></div>*/}
      {/*    <div>*/}
      {/*      <button onClick={() => handleTaskCreate(task_title)} className="secondary_button" style={{marginLeft:'10px',padding:'5px 7px'}}>*/}
      {/*        <Image width={16} height={16} src="/images/add.svg" alt="add-icon"/>*/}
      {/*      </button>*/}
      {/*    </div>*/}
      {/*  </div>*/}
      {/*</div>*/}
      {taskList.length > 0 ? <div style={{color: '#FFFFFF', padding: '5px 7px'}}>Pending Tasks</div> : <div></div>}
      {taskList.map((task, index) => (<div key={index} className={styles.history_box}
                                           style={{background: '#272335', padding: '20px', cursor: 'default'}}>
        <div style={{display: 'flex'}}>
          {/*<div className={styles.feed_icon}>🌟</div>*/}
          <div className={styles.feed_title}>{task.name}</div>
        </div>
      </div>))}
      {completedTaskList.length > 0 ? <div style={{color: '#FFFFFF', padding: '5px 7px'}}>Completed Tasks</div> : <div></div>}
       {completedTaskList.map((task, index) => (<div key={index} className={styles.history_box} style={{background:'#272335',padding:'20px',cursor:'default'}}>
        <div style={{display:'flex'}}>
          {/*<div className={styles.feed_icon}>🌟</div>*/}
          <div className={styles.feed_title}>{task.name}</div>
        </div>
       </div>))}
    </div>
    <ToastContainer/>
  </>)
}