import React, {useState} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import Head from 'next/head';

export default function ActivityFeed({feeds, history}) {
  function checkEmptyText(text) {
    return text.replace(/\s/g, '') !== ''
  }

  return (<>
    <Head>
      <link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro&display=swap" rel="stylesheet"/>
    </Head>
    <div style={history ? {paddingLeft:'7px'} : {}}>
      {feeds.map((feed, index) => (<div key={index} className={styles.history_box} style={{background:'#272335',padding:'20px',cursor:'default'}}>
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
    </div>
  </>)
}