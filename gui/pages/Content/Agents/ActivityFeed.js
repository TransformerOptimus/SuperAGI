import React, { useState, useEffect } from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import Head from 'next/head';

export default function ActivityFeed() {
  const [loadingText, setLoadingText] = useState("Thinking");
  const [feeds, setFeeds] = useState([]);

  useEffect(() => {
    const text = 'Thinking';
    let dots = '';

    const interval = setInterval(() => {
      dots = dots.length < 3 ? dots + '.' : '';
      setLoadingText(`${text}${dots}`);
    }, 250);

    return () => clearInterval(interval);
  }, []);

  function checkEmptyText(text) {
    return text.replace(/\s/g, '') !== ''
  }

  return (<>
    <Head>
      {/* eslint-disable-next-line @next/next/no-page-custom-font */}
      <link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro&display=swap" rel="stylesheet"/>
    </Head>
    <div>
      {[].map((feed, index) => (<div key={index} className={styles.history_box} style={{background:'#272335',padding:'20px',cursor:'default'}}>
        <div style={{display:'flex',marginBottom: checkEmptyText(feed.description) ? '10px' : ''}}>
          {feed.status === 'new' && <div className={styles.feed_icon}>🌟</div>}
          {feed.status === 'working' && <div className={styles.feed_icon}>⚒️</div>}
          {feed.status === 'completed' && <div className={styles.feed_icon}>✅</div>}
          <div className={styles.feed_title}>{feed.title}</div>
        </div>
        {checkEmptyText(feed.description) && <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
          <div className={styles.feed_description}>{feed.description}</div>
        </div>}
      </div>))}
      <div className={styles.history_box} style={{background:'#272335',padding:'20px',cursor:'default'}}>
        <div style={{display:'flex'}}>
          <div style={{fontSize:'20px'}}>🧠</div>
          <div className={styles.feed_title}><i>{loadingText}</i></div>
        </div>
      </div>
    </div>
  </>)
}