import React, { useEffect, useState } from 'react';
import styles from './Agents.module.css';
import 'react-toastify/dist/ReactToastify.css';
import { getExecutionTasks } from '@/pages/api/DashboardService';

export default function TaskQueue({ selectedRunId }) {
  const [tasks, setTasks] = useState({ pending: [], completed: [] });

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
    <div>
      {tasks.pending.length > 0 && <div className={styles.task_header}>Pending Tasks</div>}
      {tasks.pending.map((task, index) => (
        <div key={index} className={styles.history_box} style={{ background: '#272335', padding: '20px', cursor: 'default' }}>
          <div style={{ display: 'flex' }}>
            <div className={styles.feed_title} style={{ marginLeft: '0' }}>
              {task.name}
            </div>
          </div>
        </div>
      ))}
      {tasks.completed.length > 0 && <div className={styles.task_header}>Completed Tasks</div>}
      {tasks.completed.map((task, index) => (
        <div key={index} className={styles.history_box} style={{ background: '#272335', padding: '20px', cursor: 'default' }}>
          <div style={{ display: 'flex' }}>
            <div className={styles.feed_title} style={{ marginLeft: '0' }}>
              {task.name}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
