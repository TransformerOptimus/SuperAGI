import React, {useEffect, useState} from 'react';
import Agents from '../Content/Agents/Agents';
import AgentWorkspace from '../Content/Agents/AgentWorkspace';
import AgentCreate from '../Content/Agents/AgentCreate';
import Tools from '../Content/Tools/Tools';
import ToolCreate from '../Content/Tools/ToolCreate';
import Settings from "./Settings/Settings";
import styles from './Dashboard.module.css';
import Image from "next/image";
import { EventBus } from "@/utils/eventBus";

export default function Content({selectedView}) {
  const [tabs, setTabs] = useState([])
  const [selectedTab, setSelectedTab] = useState(null)

  const closeTab = (tabId) => {
    const updatedTabs = tabs.filter((tab) => tab.id !== tabId);
    const indexToRemove = tabs.findIndex((tab) => tab.id === tabId);

    let nextSelectedTabIndex;
    if (indexToRemove === 0) {
      nextSelectedTabIndex = 0;
    } else if (indexToRemove === tabs.length - 1) {
      nextSelectedTabIndex = tabs.length - 2;
    } else {
      nextSelectedTabIndex = indexToRemove;
    }

    setTabs(updatedTabs);
    setSelectedTab(tabs[nextSelectedTabIndex]?.id || null);
  };

  const addTab = (element) => {
    if (!tabs.some(item => item.id === element.id)) {
      const updatedTabs = [...tabs, element];
      setTabs(updatedTabs);
    }
    setSelectedTab(element.id);
  };

  useEffect(() => {
    const settingsTab = (eventData) => {
      addTab(eventData);
    };

    EventBus.on('settingsTab', settingsTab);

    return () => {
      EventBus.off('settingsTab', settingsTab);
    };
  });

  return (<>
    <div style={{display:'flex',height:'100%'}}>
      <div className={styles.item_list} style={selectedView === '' ? {width:'0vw'} : {width:'13vw'}}>
        {selectedView === 'agents' && <Agents sendAgentData={addTab}/>}
        {selectedView === 'tools' && <Tools sendToolData={addTab}/>}
      </div>
      {tabs.length <= 0 ? <div className={styles.main_workspace} style={selectedView === '' ? {width:'93.5vw',paddingLeft:'10px'} : {width:'80.5vw'}}>
        <div className={styles.empty_state}>
          <div>
            <Image width={264} height={144} src="/images/watermark.png" alt="empty-state"/>
          </div>
        </div>
      </div> : <div className={styles.main_workspace} style={selectedView === '' ? {width:'93.5vw',paddingLeft:'10px'} : {width:'80.5vw'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'center'}}>
          <div className={styles.tabs}>
            {tabs.map((tab) => (
              <div key={tab.id} className={`${styles.tab_box} ${selectedTab === tab.id ? styles.tab_box_selected : ''}`} onClick={() => setSelectedTab(tab.id)}>
                <div style={{display:'flex', order:'0'}}>
                  {(tab.contentType === 'Agents' || tab.contentType === 'Create_Agent') && <div className={styles.tab_active}><Image width={13} height={13} src="/images/agents_light.png" alt="agent-icon"/></div>}
                  {(tab.contentType === 'Tools' || tab.contentType === 'Create_Tool') && <div className={styles.tab_active}><Image width={13} height={13} src="/images/tools_light.png" alt="tools-icon"/></div>}
                  {tab.contentType === 'Settings' && <div className={styles.tab_active}><Image width={13} height={13} src="/images/settings.png" alt="settings-icon"/></div>}
                  <div style={{marginLeft:'8px'}}><span className={styles.tab_text}>{tab.name}</span></div>
                </div>
                <div onClick={() => closeTab(tab.id)} className={styles.tab_active} style={{order:'1'}}><Image width={13} height={13} src="/images/close_light.png" alt="close-icon"/></div>
              </div>
            ))}
          </div>
        </div>
        <div className={styles.tab_detail} style={tabs.length > 0 ? {backgroundColor:'#2F2C40'} : {}}>
          <div style={{padding:'0 5px 5px 5px'}}>
            {tabs.map((tab) => (
              <div key={tab.id}>
                {selectedTab === tab.id && <div>
                  {tab.contentType === 'Agents' && <AgentWorkspace agent={tab}/>}
                  {tab.contentType === 'Settings' && <Settings/>}
                  {tab.contentType === 'Create_Agent' && <div className={styles.create_agent}>
                    <div className="row">
                      <div className="col-3"></div>
                      <div className="col-6" style={{overflowY:'scroll'}}>
                        <AgentCreate/>
                      </div>
                      <div className="col-3"></div>
                    </div>
                  </div>}
                  {tab.contentType === 'Create_Tool' && <div className={styles.create_agent}>
                    <div className="row">
                      <div className="col-3"></div>
                      <div className="col-6" style={{overflowY:'scroll'}}>
                        <ToolCreate/>
                      </div>
                      <div className="col-3"></div>
                    </div>
                  </div>}
                </div>}
              </div>
            ))}
          </div>
        </div>
      </div>}
    </div>
  </>
  );
}
