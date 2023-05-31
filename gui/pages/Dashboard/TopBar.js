import React, {useEffect} from 'react';
import Image from 'next/image';
import styles from './Dashboard.module.css';
import { EventBus } from "@/utils/eventBus";

export default function TopBar({userName, selectedProject}) {
  const settingsTab = () => {
    EventBus.emit('settingsTab', { id: -3, name: "Settings", contentType: "Settings" });
  }

  return (
    <div className={styles.top_bar}>
      <div className={styles.top_left}>
        <div className={styles.top_bar_section} style={{border: '1px solid rgba(255, 255, 255, 0.14)',width:'140px'}}>
          <div style={{display:'flex',alignItems:'center',justifyContent:'flex-start'}}>
            <div style={{marginTop:'-1px'}}><Image width={14} height={14} src="/images/project.svg" alt="project-icon"/></div>
            <div className={styles.top_bar_font}><p>{selectedProject?.name || ''}</p></div>
          </div>
          {/*<div style={{order:'1'}}><Image width={16} height={16} src="/images/dropdown_down.svg" alt="dropdown-icon"/></div>*/}
        </div>

        <div className={styles.top_bar_section} style={{marginLeft:'10px',cursor:'default'}}>
          <div style={{marginTop:'-2px'}}><Image width={14} height={14} src="/images/widgets.svg" alt="widgets-icon"/></div>
          <div className={styles.top_bar_font}><p>Marketplace (coming soon)</p></div>
          {/*<div style={{flexGrow:'1'}}><Image width={16} height={16} src="/images/dropdown_down.svg" alt="dropdown-icon"/></div>*/}
        </div>
      </div>


      <div className={styles.top_right}>
        {/*<div onClick={settingsTab} className={styles.top_right_icon}><Image width={16} height={16} src="/images/settings.svg" alt="dropdown-icon"/></div>*/}
        {/*<div className={styles.top_right_icon}><Image width={16} height={16} src="/images/notifications.svg" alt="dropdown-icon"/></div>*/}
        <div className={styles.top_bar_font} style={{marginRight:'5px'}}><p>{userName}</p></div>
        <div className={styles.top_right_icon}><Image width={20} height={20} src="/images/profile_pic.png" alt="dropdown-icon"/></div>
      </div>
    </div>
  )
}
