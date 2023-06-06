import React, {useState} from 'react';
import Image from 'next/image';
import styles from './Dashboard.module.css';
import { EventBus } from "@/utils/eventBus";
import { useRouter } from 'next/router';
import agentStyles from '../Content/Agents/Agents.module.css';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {refreshUrl} from "@/utils/utils";

export default function TopBar({selectedProject, userName}) {
  const [dropdown, setDropdown] = useState(false);
  const [settingsModal, setSettingsModal] = useState(false);
  const router = useRouter();
  const [openAIKey, setKey] = useState('');
  const [temperature, setTemperature] = useState(0.5);

  const settingsTab = () => {
    EventBus.emit('settingsTab', { id: -3, name: "Settings", contentType: "Settings" });
  }

  const logoutUser = () => {
    setDropdown(false);

    if (typeof window === 'undefined') {
      return;
    }

    localStorage.removeItem('accessToken');
    refreshUrl();
    router.reload();
  };

  const handleOpenAIKey = (event) => {
    setKey(event.target.value);
  };

  const preventDefault = (e) => {
    e.stopPropagation();
  };

  const saveSettings = () => {
    setSettingsModal(false);
    toast.success("Settings updated", {autoClose: 1800});
  };

  const handleTemperatureChange = (event) => {
    setTemperature(event.target.value);
  };

  return (
    <>
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
          <div onClick={() => setSettingsModal(true)} className={styles.top_right_icon}><Image width={16} height={16} src="/images/settings.svg" alt="dropdown-icon"/></div>
          {/*<div className={styles.top_right_icon}><Image width={16} height={16} src="/images/notifications.svg" alt="dropdown-icon"/></div>*/}
          <div className={styles.top_right_icon} onClick={() => setDropdown(!dropdown)}>
            <Image width={20} height={20} src="/images/profile_pic.png" alt="dropdown-icon"/>
          </div>
          {dropdown && <div style={{marginTop:'13vh',marginRight:'-45px'}} onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
            <ul className="dropdown_container" style={{width:'fit-content'}}>
              <li className="dropdown_item" onClick={() => setDropdown(false)}>{userName}</li>
              <li className="dropdown_item" onClick={logoutUser}>Logout</li>
            </ul>
          </div>}
        </div>
      </div>
      {settingsModal && (<div className="modal" onClick={() => setSettingsModal(false)}>
        <div className="modal-content" style={{width: '40%'}} onClick={preventDefault}>
          <div className={agentStyles.detail_name}>Settings</div>
          <div>
            <label className={agentStyles.form_label}>Open-AI API Key</label>
            <input placeholder="Enter your Open-AI API key" className="input_medium" type="password" value={openAIKey} onChange={handleOpenAIKey}/>
          </div>
          {/*<div style={{marginTop:'15px'}}>*/}
          {/*  <label className={agentStyles.form_label}>Temperature</label>*/}
          {/*  <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>*/}
          {/*    <input style={{width:'90%'}} type="range" step={0.1} min={0} max={1} value={temperature} onChange={handleTemperatureChange}/>*/}
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
      <ToastContainer/>
    </>
  )
}
