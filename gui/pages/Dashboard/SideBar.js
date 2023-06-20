import React, {useState} from 'react';
import Image from 'next/image';
import styles from './Dashboard.module.css';
// import qs from "qs";
// import {googleClientId} from "@/pages/api/apiConfig";

export default function SideBar({onSelectEvent}) {
  const [sectionSelected, setSelection] = useState('');
  const [env, setEnv] = useState('DEV');

  function getToken(){
    const client_id = '854220347677-61mrt85gqss7egbmhm79dfumqj1dlrto.apps.googleusercontent.com';
    const scope = 'https://www.googleapis.com/auth/calendar';
    const redirect_uri = 'http://localhost:8001/oauth-calendar';
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${client_id}&redirect_uri=${redirect_uri}&access_type=offline&response_type=code&scope=${scope}`;
    window.location.href = authUrl;
  }
  const handleClick = (value) => {
    setSelection(value);
    onSelectEvent(value);
  };
    return (
    <div className={styles.side_bar}>
      <div><Image width={64} height={48} className={styles.logo} src="/images/app-logo-light.png" alt="super-agi-logo"/>
      </div>
      <div className={styles.selection_section}>
        <div onClick={() => handleClick(sectionSelected !== 'agents' ? 'agents' : '')} className={`${styles.section} ${sectionSelected === 'agents' ? styles.selected : ''}`}>
          <div className={styles.button_icon}><Image width={17} height={17} src="/images/agents_light.svg" alt="agent-icon"/></div>
          <div>Agents</div>
        </div>
      </div>
      <div className={styles.selection_section}>
        <div onClick={() => handleClick(sectionSelected !== 'tools' ? 'tools' : '')} className={`${styles.section} ${sectionSelected === 'tools' ? styles.selected : ''}`}>
          <div className={styles.button_icon}><Image width={17} height={17} src="/images/tools_light.svg" alt="tools-icon"/></div>
          <div>Tools</div>
        </div>
      </div>
      {/*<div className={styles.selection_section}>*/}
      {/*  <div onClick={getToken} className={`${styles.section} ${sectionSelected === 'agent_cluster' ? styles.selected : ''}`}>*/}
      {/*    <div className={styles.button_icon}><Image width={17} height={17} src="/images/agent_cluster_light.svg" alt="agent-cluster-icon"/></div>*/}
      {/*    <div>Google Calendar</div>*/}
      {/*  </div>*/}
      {/*</div>*/}
      {/*<div className={styles.selection_section}>*/}
      {/*  <div onClick={() => handleClick(sectionSelected !== 'apm' ? 'apm' : '')} className={`${styles.section} ${sectionSelected === 'apm' ? styles.selected : ''}`}>*/}
      {/*    <div className={styles.button_icon}><Image width={17} height={17} src="/images/apm_light.svg" alt="apm-icon"/></div>*/}
      {/*    <div>APM</div>*/}
      {/*  </div>*/}
      {/*</div>*/}
      {/*<div className={styles.selection_section}>*/}
      {/*  <div onClick={() => handleClick(sectionSelected !== 'embeddings' ? 'embeddings' : '')} className={`${styles.section} ${sectionSelected === 'embeddings' ? styles.selected : ''}`}>*/}
      {/*    <div className={styles.button_icon}><Image width={17} height={17} src="/images/embedding_light.svg" alt="embedding-icon"/></div>*/}
      {/*    <div>Embeddings</div>*/}
      {/*  </div>*/}
      {/*</div>*/}
    </div>
  );
}
