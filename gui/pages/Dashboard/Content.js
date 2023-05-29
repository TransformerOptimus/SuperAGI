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
import {getAgents, getTools} from "@/app/DashboardService";

export default function Content({selectedView, selectedProjectId, userName}) {
  const [tabs, setTabs] = useState([])
  const [selectedTab, setSelectedTab] = useState(null)
  const [agents, setAgents] = useState(null);
  const [tools, setTools] = useState(null);

  function fetchAgents() {
    getAgents(selectedProjectId)
      .then((response) => {
        const data = response.data || [];
        const updatedData = data.map(item => {
          return { ...item, contentType: "Agents" };
        });
        setAgents(updatedData);
      })
      .catch((error) => {
        console.error('Error fetching agents:', error);
      });
  }

  function fetchTools() {
    getTools()
      .then((response) => {
        const data = response.data || [];
        const updatedData = data.map(item => {
          return { ...item, contentType: "Tools" };
        });
        setTools(updatedData);
      })
      .catch((error) => {
        console.error('Error fetching agents:', error);
      });
  }

  useEffect(() => {
    fetchAgents();
    fetchTools();
  }, [selectedProjectId])

  const closeTab = (e, tabId) => {
    e.stopPropagation();
    const updatedTabs = tabs.filter((tab) => tab.id !== tabId);
    setTabs(updatedTabs);

    if (selectedTab !== tabId) {
      return;
    }

    let nextSelectedTabId = null;
    const indexToRemove = tabs.findIndex((tab) => tab.id === tabId);

    if (indexToRemove === 0) {
      nextSelectedTabId = tabs[1]?.id || null;
    } else if (indexToRemove === tabs.length - 1) {
      nextSelectedTabId = tabs[indexToRemove - 1]?.id || null;
    } else {
      nextSelectedTabId = tabs[indexToRemove + 1]?.id || null;
    }

    setSelectedTab(nextSelectedTabId);
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
    EventBus.on('reFetchAgents', fetchAgents);

    return () => {
      EventBus.off('settingsTab', settingsTab);
      EventBus.off('reFetchAgents', fetchAgents);
    };
  });

  return (<>
    <div style={{display:'flex',height:'100%'}}>
      <div className={styles.item_list} style={selectedView === '' ? {width:'0vw'} : {width:'13vw'}}>
        {selectedView === 'agents' && <Agents sendAgentData={addTab} agents={agents}/>}
        {selectedView === 'tools' && <Tools sendToolData={addTab} tools={tools} userName={userName}/>}
      </div>
      {tabs.length <= 0 ? <div className={styles.main_workspace} style={selectedView === '' ? {width:'93.5vw',paddingLeft:'10px'} : {width:'80.5vw'}}>
        <div className={styles.empty_state}>
          <div>
            <div><Image width={264} height={144} src="/images/watermark.png" alt="empty-state"/></div>
            <div style={{width:'100%',display:'flex',justifyContent:'center',marginTop:'30px'}}>
              <button onClick={() => addTab({ id: -1, name: "new agent", contentType: "Create_Agent" })} className={styles.empty_state_button}>Create new agent</button>
            </div>
            <div style={{width:'100%',display:'flex',justifyContent:'center',marginTop:'20px'}}>
              <button className={styles.empty_state_button}>View last active agent</button>
            </div>
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
                <div onClick={(e) => closeTab(e, tab.id)} className={styles.tab_active} style={{order:'1'}}><Image width={13} height={13} src="/images/close_light.png" alt="close-icon"/></div>
              </div>
            ))}
          </div>
        </div>
        <div className={styles.tab_detail} style={tabs.length > 0 ? {backgroundColor:'#2F2C40'} : {}}>
          <div style={{padding:'0 5px 5px 5px'}}>
            {tabs.map((tab) => (
              <div key={tab.id}>
                {selectedTab === tab.id && <div>
                  {tab.contentType === 'Agents' && <AgentWorkspace agentId={tab.id}/>}
                  {tab.contentType === 'Settings' && <Settings/>}
                  {tab.contentType === 'Create_Agent' && <div className={styles.create_agent}>
                    <div className="row">
                      <div className="col-3"></div>
                      <div className="col-6" style={{overflowY:'scroll'}}>
                        <AgentCreate sendAgentData={addTab} selectedProjectId={selectedProjectId} fetchAgents={fetchAgents} tools={tools}/>
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
