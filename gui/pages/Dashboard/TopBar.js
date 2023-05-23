import React, {useState} from 'react';
import Image from 'next/image';
import styles from './Dashboard.module.css';

export default function TopBar() {
  return (
    <div className={styles.top_bar}>
      <div className={styles.top_bar_section} style={{border: '1px solid rgba(255, 255, 255, 0.14)'}}>
        <div style={{marginTop:'-1px'}}><Image width={14} height={14} src="/images/project.png" alt="project-icon"/></div>
        <div className={styles.top_bar_font}><p>Default Project 1</p></div>
        <div style={{flexGrow:'1'}}><Image width={16} height={16} src="/images/dropdown_down.png" alt="dropdown-icon"/></div>
      </div>

      <div className={styles.top_bar_section} style={{marginLeft:'10px'}}>
        <div style={{marginTop:'-2px'}}><Image width={14} height={14} src="/images/widgets.png" alt="widgets-icon"/></div>
        <div className={styles.top_bar_font}><p>Marketplace</p></div>
        <div style={{flexGrow:'1'}}><Image width={16} height={16} src="/images/dropdown_down.png" alt="dropdown-icon"/></div>
      </div>
    </div>
  )
}
