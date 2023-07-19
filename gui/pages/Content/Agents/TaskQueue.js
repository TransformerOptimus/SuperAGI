import React, {useEffect, useState} from 'react';
import styles from './Agents.module.css';
import 'react-toastify/dist/ReactToastify.css';
import {getExecutionTasks} from '@/pages/api/DashboardService';
import Image from "next/image";

export default function TaskQueue({selectedRunId}) {
  const [tasks, setTasks] = useState({pending: [], completed: []});

  useEffect(() => {
    fetchTasks();
  }, [selectedRunId]);

  function fetchTasks() {
    getExecutionTasks(selectedRunId)
      .then((response) => {
        setTasks({
          pending: response.data.tasks,
          completed: response.data.completed_tasks,
        });
      })
      .catch((error) => {
        console.error('Error fetching execution feeds:', error);
      });
  }

  return (
    <>
      {tasks.pending.length <= 0 && tasks.completed.length <= 0 ? <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: '40px',
        width: '100%'
      }}>
        <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions"/>
        <span className={styles.feed_title} style={{marginTop: '8px'}}>No Tasks found!</span>
      </div> : <div>
        {tasks.pending.length > 0 && <div className={styles.task_header}>Pending Tasks</div>}
        {tasks.pending.map((task, index) => (
          <div key={index} className={styles.history_box}
               style={{background: '#272335', padding: '20px', cursor: 'default'}}>
            <div style={{display: 'flex'}}>
              <div>
                <Image width={14} height={14} style={{mixBlendMode: 'exclusion'}} src="/images/loading.gif"
                       alt="loading-icon"/>
              </div>
              <div className={styles.feed_title}>
                {task.name}
              </div>
            </div>
          </div>
        ))}
        {tasks.completed.length > 0 && <div className={styles.task_header}>Completed Tasks</div>}
        {tasks.completed.map((task, index) => (
          <div key={index} className={styles.history_box}
               style={{background: '#272335', padding: '20px', cursor: 'default'}}>
            <div style={{display: 'flex'}}>
              <div className={styles.feed_title} style={{marginLeft: '0'}}>
                {task.name}
              </div>
            </div>
          </div>
        ))}
      </div>}
    </>
  );
}
