import React, {useEffect, useState, useRef} from 'react';
import Agents from '../Content/Agents/Agents';
import AgentWorkspace from '../Content/Agents/AgentWorkspace';
import AgentCreate from '../Content/Agents/AgentCreate';
import Tools from '../Content/Tools/Tools';
import ToolCreate from '../Content/Tools/ToolCreate';
import Settings from "./Settings/Settings";
import styles from './Dashboard.module.css';
import Image from "next/image";
import { EventBus } from "@/utils/eventBus";
import {getAgents, getTools, getLastActiveAgent} from "@/pages/api/DashboardService";

export default function Content({selectedView, selectedProjectId, organisationId}) {
  const [tabs, setTabs] = useState([])
  const [selectedTab, setSelectedTab] = useState(null)
  const [agents, setAgents] = useState(null);
  const [tools, setTools] = useState(null);
  const tabContainerRef = useRef(null);

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
        console.error('Error fetching tools:', error);
      });
  }

  useEffect(() => {
    fetchAgents();
    fetchTools();
  }, [selectedProjectId])

  const closeTab = (e, tabId) => {
    e.stopPropagation();
    cancelTab(tabId);
  };

  const cancelTab = (tabId) => {
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
    if (tabContainerRef.current) {
      const tabElement = tabContainerRef.current.querySelector(`[data-tab-id="${selectedTab}"]`);
      if (tabElement) {
        const containerScrollLeft = tabContainerRef.current.scrollLeft;
        const tabOffsetLeft = tabElement.offsetLeft;
        const containerWidth = tabContainerRef.current.offsetWidth;

        if (tabOffsetLeft < containerScrollLeft || tabOffsetLeft >= containerScrollLeft + containerWidth) {
          tabContainerRef.current.scrollLeft = tabOffsetLeft;
        }
      }
    }
  }, [selectedTab]);

  useEffect(() => {
    const settingsTab = (eventData) => {
      addTab(eventData);
    };

    const cancelAgentCreate = (eventData) => {
      cancelTab(-1);
    };

    EventBus.on('settingsTab', settingsTab);
    EventBus.on('reFetchAgents', fetchAgents);
    EventBus.on('cancelAgentCreate', cancelAgentCreate);

    return () => {
      EventBus.off('settingsTab', settingsTab);
      EventBus.off('reFetchAgents', fetchAgents);
      EventBus.off('cancelAgentCreate', cancelAgentCreate);
    };
  });

  function getLastActive() {
    getLastActiveAgent(selectedProjectId)
      .then((response) => {
        addTab(response.data);
      })
      .catch((error) => {
        console.error('Error fetching last active agent:', error);
      });
  }

  return (<>
    <div style={{display:'flex',height:'100%'}}>
      <div className={styles.item_list} style={selectedView === '' ? {width:'0vw'} : {width:'13vw'}}>
        {selectedView === 'agents' && <div><Agents sendAgentData={addTab} agents={agents}/></div>}
        {selectedView === 'tools' && <div><Tools sendToolData={addTab} tools={tools}/></div>}
      </div>
      {tabs.length <= 0 ? <div className={styles.main_workspace} style={selectedView === '' ? {width:'93.5vw',paddingLeft:'10px'} : {width:'80.5vw'}}>
        <div className={styles.empty_state}>
          <div>
            <div><Image width={264} height={144} src="/images/watermark.png" alt="empty-state"/></div>
            <div style={{width:'100%',display:'flex',justifyContent:'center',marginTop:'30px'}}>
              <button onClick={() => addTab({ id: -1, name: "new agent", contentType: "Create_Agent" })} className={styles.empty_state_button}>Create new agent</button>
            </div>
            {agents && agents.length > 0 && <div style={{width:'100%',display:'flex',justifyContent:'center',marginTop:'12px'}}>
              <button onClick={getLastActive} className={styles.empty_state_button}>View last active agent</button>
            </div>}
          </div>
        </div>
      </div> : <div className={styles.main_workspace} style={selectedView === '' ? {width:'93.5vw',paddingLeft:'10px'} : {width:'80.5vw'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'center'}}>
          <div className={styles.tabs} ref={tabContainerRef}>
            {tabs.map((tab) => (
              <div data-tab-id={tab.id} key={tab.id} className={`${styles.tab_box} ${selectedTab === tab.id ? styles.tab_box_selected : ''}`} onClick={() => setSelectedTab(tab.id)}>
                <div style={{display:'flex', order:'0'}}>
                  {(tab.contentType === 'Agents' || tab.contentType === 'Create_Agent') && <div className={styles.tab_active}><Image width={13} height={13} src="/images/agents_light.svg" alt="agent-icon"/></div>}
                  {(tab.contentType === 'Tools' || tab.contentType === 'Create_Tool') && <div className={styles.tab_active}><Image width={13} height={13} src="/images/tools_light.svg" alt="tools-icon"/></div>}
                  {tab.contentType === 'Settings' && <div className={styles.tab_active}><Image width={13} height={13} src="/images/settings.svg" alt="settings-icon"/></div>}
                  <div style={{marginLeft:'8px'}}><span className={styles.tab_text}>{tab.name}</span></div>
                </div>
                <div onClick={(e) => closeTab(e, tab.id)} className={styles.tab_active} style={{order:'1'}}><Image width={13} height={13} src="/images/close_light.svg" alt="close-icon"/></div>
              </div>
            ))}
          </div>
        </div>
        <div className={styles.tab_detail} style={tabs.length > 0 ? {backgroundColor:'#2F2C40'} : {}}>
          <div style={{padding:'0 5px 5px 5px'}}>
            {tabs.map((tab) => (
              <div key={tab.id}>
                {selectedTab === tab.id && <div>
                  {tab.contentType === 'Agents' && <AgentWorkspace agentId={tab.id} selectedView={selectedView}/>}
                  {tab.contentType === 'Settings' && <Settings/>}
                  {tab.contentType === 'Create_Agent' && <div className={styles.create_agent}>
                    <AgentCreate organisationId={organisationId} sendAgentData={addTab} selectedProjectId={selectedProjectId} fetchAgents={fetchAgents} tools={tools}/>
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
