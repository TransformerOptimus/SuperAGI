import React, { useState, useEffect, useRef } from 'react';
import styles from './Agents.module.css';
import Head from 'next/head';
import {getExecutionFeeds} from "@/app/DashboardService";

export default function ActivityFeed({selectedRunId, selectedRunStatus}) {
  const [loadingText, setLoadingText] = useState("Thinking");
  const [feeds, setFeeds] = useState([]);
  const feedContainerRef = useRef(null);

  useEffect(() => {
    const text = 'Thinking';
    let dots = '';

    const interval = setInterval(() => {
      dots = dots.length < 3 ? dots + '.' : '';
      setLoadingText(`${text}${dots}`);
    }, 250);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const selectedRunId1 = selectedRunId;
    const interval = window.setInterval(function(){
      fetchFeeds(selectedRunId1);
    }, 10000);

    return () => clearInterval(interval);
  }, [selectedRunId]);

  function checkEmptyText(text) {
    return text.replace(/\s/g, '') !== ''
  }

  useEffect(() => {
    getExecutionFeeds(selectedRunId)
      .then((response) => {
        setFeeds(response.data);
      })
      .catch((error) => {
        console.error('Error fetching execution feeds:', error);
      });
  }, [selectedRunId])

  function fetchFeeds(selectedRunId) {
    getExecutionFeeds(selectedRunId)
      .then((response) => {
        setFeeds(response.data);
        scrollToBottom();
      })
      .catch((error) => {
        console.error('Error fetching execution feeds:', error);
      });
  }

  const scrollToBottom = () => {
    if (feedContainerRef.current) {
      feedContainerRef.current.scrollTop = feedContainerRef.current.scrollHeight;
    }
  };

  return (<>
    <Head>
      {/* eslint-disable-next-line @next/next/no-page-custom-font */}
      <link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro&display=swap" rel="stylesheet"/>
    </Head>
    <div style={{marginBottom:'140px'}} ref={feedContainerRef}>
      {feeds && feeds.map((f, index) => (<div key={index} className={styles.history_box} style={{background:'#272335',padding:'20px',cursor:'default'}}>
        <div style={{display:'flex'}}>
          {f.role === 'user' && <div className={styles.feed_icon}>💁</div>}
          {f.role === 'system' && <div className={styles.feed_icon}>🛠️ </div>}
          {f.role === 'assistant' && <div className={styles.feed_icon}>💡</div>}
          <div className={styles.feed_title} style={{whiteSpace: 'pre-line'}}>{f?.feed || ''}</div>
        </div>
        {/*{checkEmptyText(feed.description) && <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>*/}
        {/*  <div className={styles.feed_description}>{feed.description}</div>*/}
        {/*</div>}*/}
      </div>))}
      {selectedRunStatus && selectedRunStatus === 'RUNNING' && <div className={styles.history_box} style={{background: '#272335', padding: '20px', cursor: 'default'}}>
        <div style={{display: 'flex'}}>
          <div style={{fontSize: '20px'}}>🧠</div>
          <div className={styles.feed_title}><i>{loadingText}</i></div>
        </div>
      </div>}
    </div>
  </>)
}