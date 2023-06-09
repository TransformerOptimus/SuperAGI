import React, { useState, useEffect, useRef } from 'react';
import Image from "next/image";
import styles from './Market.module.css';

export default function MarketTools() {
  return (
    <div>
    <div className={styles.history_box}>
        Tools
    </div>
    <div className={styles.featured_text}>Top featured</div>

    <div className={styles.market_tool}>
      <div style={{padding:'12px'}}>
      <Image width={35} height={35} src="/images/gmail.png" alt="empty-state"/>
      </div>
      <div style={{display:'inline'}}>
      <div style={{paddingTop:'12px', paddingLeft:'6px'}}>tool name</div>
      <div style={{paddingLeft:'6px', fontSize:'x-small', color:'rgb(96, 96, 96)'}}>by Google</div>
      </div>
    </div>

    <div className={styles.market_tool}>
      <div style={{padding:'12px'}}>
      <Image width={35} height={35} src="/images/gmail.png" alt="empty-state"/>
      </div>
      <div style={{display:'inline'}}>
      <div style={{paddingTop:'12px', paddingLeft:'6px'}}>tool name</div>
      <div style={{paddingLeft:'6px', fontSize:'x-small', color:'rgb(96, 96, 96)'}}>by random</div>
      </div>
    </div>


    <div className={styles.featured_text}>New Tools</div>
    </div>
  );
};


