import React, {useState, useEffect} from 'react';
import 'react-toastify/dist/ReactToastify.css';
import styles from "@/pages/Content/Marketplace/Market.module.css";
import Image from "next/image";
import Model from "@/pages/Dashboard/Settings/Model";
import Database from "@/pages/Dashboard/Settings/Database";
import ApiKeys from "@/pages/Dashboard/Settings/ApiKeys";

export default function Settings({organisationId, sendDatabaseData}) {
  const [activeTab, setActiveTab] = useState('model');

  useEffect(() => {
    const settings_tab = localStorage.getItem('settings_tab');
    if (settings_tab) {
      setActiveTab(settings_tab);
    }
  }, []);

  const switchTab = (tab) => {
    setActiveTab(tab);
    localStorage.setItem('settings_tab', tab);
  };

  return (<>
    <div className={styles.empty_state}>
      <div style={{width: '100%', display: 'flex', flexDirection: 'column'}}>
        <div className={styles.detail_top}>
          <div style={{display: 'flex', overflowX: 'scroll', marginLeft: '8px'}}>
            <div>
              <button onClick={() => switchTab('model')} className={styles.tab_button} style={activeTab === 'model' ? {
                background: '#454254',
                paddingRight: '15px'
              } : {background: 'transparent', paddingRight: '15px'}}>
                <Image style={{marginTop: '-1px'}} width={14} height={14} src="/images/model_light.svg"
                       alt="model-icon"/>&nbsp;Model
              </button>
            </div>
            <div>
              <button onClick={() => switchTab('database')} className={styles.tab_button}
                      style={activeTab === 'database' ? {
                        background: '#454254',
                        paddingRight: '15px'
                      } : {background: 'transparent', paddingRight: '15px'}}>
                <Image style={{marginTop: '-1px'}} width={14} height={14} src="/images/database.svg"
                       alt="database-icon"/>&nbsp;Database
              </button>
            </div>
            <div>
              <button onClick={() => switchTab('apikeys')} className={`${styles.tab_button} ${activeTab === 'apikeys' ? styles.settings_tab_button_clicked : styles.settings_tab_button}`}>
                <Image className={styles.settings_tab_img} width={14} height={14} src="/images/key_white.svg"
                       alt="database-icon"/>&nbsp;API Keys
              </button>
            </div>
          </div>
        </div>
        <div>
          {activeTab === 'model' && <Model organisationId={organisationId}/>}
          {activeTab === 'database' && <Database sendDatabaseData={sendDatabaseData} organisationId={organisationId}/>}
          {activeTab === 'apikeys' && <ApiKeys />}
        </div>
      </div>
    </div>
  </>)
}