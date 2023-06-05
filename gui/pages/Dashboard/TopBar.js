import React, {useState} from 'react';
import Image from 'next/image';
import styles from './Dashboard.module.css';
import { EventBus } from "@/utils/eventBus";
import { useRouter } from 'next/router';

export default function TopBar({selectedProject, userName}) {
  const [dropdown, setDropdown] = useState(false);
  const router = useRouter();

  const settingsTab = () => {
    EventBus.emit('settingsTab', { id: -3, name: "Settings", contentType: "Settings" });
  }

  const logoutUser = () => {
    if (typeof window === 'undefined') {
      return;
    }

    localStorage.setItem('accessToken', '');
    router.reload();
    setDropdown(false);
  };

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
        <div className={styles.top_right_icon} onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
          <Image width={20} height={20} src="/images/profile_pic.png" alt="dropdown-icon"/>
        </div>
        {dropdown && <div style={{marginTop:'13vh',marginRight:'-20px'}} onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
          <ul className="dropdown_container" style={{width:'120px'}}>
            <li className="dropdown_item" onClick={() => setDropdown(false)}>{userName}</li>
            <li className="dropdown_item" onClick={logoutUser}>Logout</li>
          </ul>
        </div>}
      </div>
    </div>
  )
}
