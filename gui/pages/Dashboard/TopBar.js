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
        <div className={styles.top_bar_font} style={{marginLeft:'-1px'}} onClick={() => openNewTab(-4, "Marketplace", "Marketplace")}><p>Marketplace</p></div>
        </div>
      </div>
      <div className={styles.top_right}>
        <div onClick={() => openNewTab(-3, "Settings", "Settings")} className={styles.top_right_icon}><Image width={16} height={16} src="/images/settings.svg" alt="dropdown-icon"/></div>
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
<<<<<<< HEAD
      {settingsModal && (<div className="modal" onClick={() => setSettingsModal(false)}>
        <div className="modal-content" style={{width: '35%'}} onClick={preventDefault}>
          <div className={agentStyles.detail_name}>Settings</div>
          <div>
            <label className={agentStyles.form_label}>Open-AI API Key</label>
            <input placeholder="Enter your Open-AI API key" className="input_medium" type="password" value={openAIKey} onChange={handleOpenAIKey}/>
          </div>
          {/*<div style={{marginTop:'15px'}}>*/}
          {/*  <label className={agentStyles.form_label}>Temperature</label>*/}
          {/*  <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>*/}
          {/*    <input style={{width:'89%'}} type="range" step={0.1} min={0} max={1} value={temperature} onChange={handleTemperatureChange}/>*/}
          {/*    <input style={{width:'9%',order:'1',textAlign:'center',paddingLeft:'0',paddingRight:'0'}} disabled={true} className="input_medium" type="text" value={temperature}/>*/}
          {/*  </div>*/}
          {/*</div>*/}
          <div style={{display: 'flex', justifyContent: 'flex-end',marginTop:'15px'}}>
            <button className="secondary_button" style={{marginRight: '10px'}} onClick={() => setSettingsModal(false)}>
              Cancel
            </button>
            <button className="primary_button" onClick={saveSettings}>
              Update Changes
            </button>
          </div>
        </div>
      </div>)}
      
=======
>>>>>>> 2dddd7050116b216fcbdf6118435691327e2eb90
      <ToastContainer/>
    </div>  
  )
}
