import React, {useState, useEffect} from 'react';
import Image from 'next/image';
import styles from './Dashboard.module.css';
import { EventBus } from "@/utils/eventBus";
import { useRouter } from 'next/router';
import agentStyles from '../Content/Agents/Agents.module.css';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {refreshUrl} from "@/utils/utils";
import {getOrganisationConfig, updateOrganisationConfig} from "@/pages/api/DashboardService";

export default function TopBar({selectedProject, organisationId, userName, env}) {
  const [dropdown, setDropdown] = useState(false);
  const [settingsModal, setSettingsModal] = useState(false);
  const router = useRouter();
  const [openAIKey, setKey] = useState('');
  const [temperature, setTemperature] = useState(0.5);

  const handleMarketplaceClick = () => {
    EventBus.emit('openNewTab', { id: -4, name: "Marketplace", contentType: "Marketplace" });
  };
  const settingsTab = () => {
    // EventBus.emit('settingsTab', { id: -3, name: "Settings", contentType: "Settings" });
    setSettingsModal(true)
  }

  function getKey(key) {
    getOrganisationConfig(organisationId, key)
      .then((response) => {
        setKey(response.data.value);
      })
      .catch((error) => {
        console.error('Error fetching project:', error);
      });
  }

  useEffect(() => {
    getKey("model_api_key");
  }, [organisationId]);

  function updateKey(key, value) {
    const configData = {"key": key, "value": value};
    updateOrganisationConfig(organisationId, configData)
      .then((response) => {
        getKey("model_api_key");
        EventBus.emit("keySet", {});
        toast.success("Settings updated", {autoClose: 1800});
      })
      .catch((error) => {
        console.error('Error fetching project:', error);
      });
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
    if (openAIKey === null || openAIKey.replace(/\s/g, '') === '') {
      toast.error("API key is empty", {autoClose: 1800});
      return
    }

    updateKey("model_api_key", openAIKey);
    setSettingsModal(false);
  };

  const handleTemperatureChange = (event) => {
    setTemperature(event.target.value);
  };

  useEffect(() => {
    const openSettings = (eventData) => {
      setSettingsModal(true);
    };

    EventBus.on('openSettings', openSettings);

    return () => {
      EventBus.off('openSettings', openSettings);
    };
  });

  return (
    <div className={styles.top_bar}>
      <div className={styles.top_left}>
        <div className={styles.top_bar_section} style={{border: '1px solid rgba(255, 255, 255, 0.14)',width:'150px'}}>
          <div style={{display:'flex',alignItems:'center',justifyContent:'flex-start'}}>
            <div style={{marginTop:'-2px'}}><Image width={14} height={14} src="/images/project.svg" alt="project-icon"/></div>
            <div className={styles.top_bar_font}><p>{selectedProject?.name || ''}</p></div>
          </div>
          {/*<div style={{order:'1'}}><Image width={16} height={16} src="/images/dropdown_down.svg" alt="dropdown-icon"/></div>*/}
        </div>
        <div className={styles.top_bar_section} style={{ marginLeft: '7px', cursor: 'pointer' }}>
        <div style={{ marginTop: '-3px' }}><Image width={14} height={14} src="/images/widgets.svg" alt="widgets-icon" /></div>
        <div className={styles.top_bar_font} style={{marginLeft:'-1px'}} onClick={handleMarketplaceClick}><p>Marketplace</p></div>
        </div>
      </div>
      <div className={styles.top_right}>
         <div onClick={() => setSettingsModal(true)} className={styles.top_right_icon}><Image width={16} height={16} src="/images/settings.svg" alt="dropdown-icon"/></div>
        {/* <div className={styles.top_right_icon}><Image width={16} height={16} src="/images/notifications.svg" alt="dropdown-icon"/></div> */}
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
      <ToastContainer/>
    </div>
  )
}
