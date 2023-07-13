import React, {useState} from 'react';
import Image from 'next/image';
import styles from './Dashboard.module.css';
import { useRouter } from 'next/router';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {refreshUrl, openNewTab} from "@/utils/utils";

export default function TopBar({selectedProject, userName, env}) {
  const [dropdown, setDropdown] = useState(false);
  const router = useRouter();

  const logoutUser = () => {
    setDropdown(false);

    if (typeof window === 'undefined') {
      return;
    }

    localStorage.removeItem('accessToken');
    refreshUrl();
    router.reload();
  };

  return (
    <div className={styles.top_bar}>
      <div className={styles.top_left}>
        <div className={styles.top_bar_section} style={{border: '1px solid rgba(255, 255, 255, 0.14)',width:'150px',cursor:'default'}}>
          <div style={{display:'flex',alignItems:'center',justifyContent:'flex-start'}}>
            <div style={{marginTop:'-2px'}}><Image width={14} height={14} src="/images/project.svg" alt="project-icon"/></div>
            <div className={styles.top_bar_font}><p>{selectedProject?.name || ''}</p></div>
          </div>
          {/*<div style={{order:'1'}}><Image width={16} height={16} src="/images/dropdown_down.svg" alt="dropdown-icon"/></div>*/}
        </div>
        <div className={styles.top_bar_section} style={{ marginLeft: '7px', cursor: 'pointer' }}>
        <div style={{ marginTop: '-3px' }}><Image width={14} height={14} src="/images/widgets.svg" alt="widgets-icon" /></div>
        <div className={styles.top_bar_font} style={{marginLeft:'-1px'}} onClick={() => openNewTab(-4, "Marketplace", "Marketplace", false)}><p>Marketplace</p></div>
        </div>
      </div>
      <div className={styles.top_right}>
        <div onClick={() => openNewTab(-3, "Settings", "Settings", false)} className={styles.top_right_icon}><Image width={16} height={16} src="/images/settings.svg" alt="dropdown-icon"/></div>
        <div className={styles.top_right_icon} onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
          <Image width={20} height={20} src="/images/profile_pic.png" alt="dropdown-icon"/>
        </div>
        {dropdown && env === 'PROD' && <div style={{marginTop:'3vh',marginRight:'74px'}} onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
          <ul className="dropdown_container" style={{width:'120px'}}>
            <li className="dropdown_item" onClick={() => setDropdown(false)}>{userName}</li>
            <li className="dropdown_item" onClick={logoutUser}>Logout</li>
          </ul>
        </div>}
      </div>
      <ToastContainer/>
    </div>  
  )
}
