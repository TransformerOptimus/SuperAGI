import React, {useState, useEffect} from 'react';
import 'react-toastify/dist/ReactToastify.css';
import styles from "@/pages/Content/Marketplace/Market.module.css";
import Image from "next/image";
import Model from "@/pages/Dashboard/Settings/Model";
import Database from "@/pages/Dashboard/Settings/Database";
import ApiKeys from "@/pages/Dashboard/Settings/ApiKeys";
import Webhooks from "@/pages/Dashboard/Settings/Webhooks";

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
      <div className="vertical_containers w_100">
        <div className={styles.detail_top}>
          <div style={{display: 'flex', overflowX: 'scroll', marginLeft: '8px', gap:'4px'}}>
            <button onClick={() => switchTab('model')} className={activeTab === 'model' ? 'tab_button_selected' : 'tab_button'}>
              <Image width={14} height={14} src="/images/model_light.svg" alt="model-icon"/>
              <span>Model Providers</span>
            </button>
            <button onClick={() => switchTab('database')} className={activeTab === 'database' ? 'tab_button_selected' : 'tab_button'}>
              <Image width={14} height={14} src="/images/database.svg" alt="database-icon"/>
              <span>Database</span>
            </button>
            <button onClick={() => switchTab('apikeys')} className={activeTab === 'apikeys' ? 'tab_button_selected' : 'tab_button'}>
              <Image width={14} height={14} src="/images/key_white.svg" alt="api-key-icon"/>
              <span>API Keys</span>
            </button>
            <button onClick={() => switchTab('webhooks')} className={activeTab === 'webhooks' ? 'tab_button_selected' : 'tab_button'}>
              <Image className={styles.settings_tab_img} width={14} height={14} src="/images/webhook_icon.svg"
                     alt="database-icon"/>&nbsp;Webhooks
            </button>
          </div>
        </div>
        <div>
          {activeTab === 'model' && <Model organisationId={organisationId}/>}
          {activeTab === 'database' && <Database sendDatabaseData={sendDatabaseData} organisationId={organisationId}/>}
          {activeTab === 'apikeys' && <ApiKeys />}
          {activeTab === 'webhooks' && <Webhooks />}
        </div>
      </div>
    </div>
  </>)
}