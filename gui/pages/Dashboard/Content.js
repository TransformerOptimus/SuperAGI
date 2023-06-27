import React, {useEffect, useState, useRef} from 'react';
import Agents from '../Content/Agents/Agents';
import AgentWorkspace from '../Content/Agents/AgentWorkspace';
import ToolkitWorkspace from '../Content/./Toolkits/ToolkitWorkspace';
import Toolkits from '../Content/./Toolkits/Toolkits';
import Settings from "./Settings/Settings";
import styles from './Dashboard.module.css';
import Image from "next/image";
import { EventBus } from "@/utils/eventBus";
import {getAgents, getToolKit, getLastActiveAgent} from "@/pages/api/DashboardService";
import Market from "../Content/Marketplace/Market";
import AgentTemplatesList from '../Content/Agents/AgentTemplatesList';

export default function Content({env, selectedView, selectedProjectId, organisationId}) {
  const [tabs, setTabs] = useState([]);
  const [source, setSource] = useState(null);
  const [selectedTab, setSelectedTab] = useState(null);
  const [agents, setAgents] = useState(null);
  const [toolkits, setToolkits] = useState(null);
  const tabContainerRef = useRef(null);
  const [toolkitDetails, setToolkitDetails] = useState({})

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

  function fetchToolkits() {
    getToolKit()
      .then((response) => {
        const data = response.data || [];
        const updatedData = data.map(item => {
          return { ...item, contentType: "Toolkits", isOpen: false };
        });
        setToolkits(updatedData);
      })
      .catch((error) => {
        console.error('Error fetching toolkits:', error);
      });
  }

  useEffect(() => {
    fetchAgents();
    fetchToolkits();
  }, [selectedProjectId])

  const closeTab = (e, index) => {
    e.stopPropagation();
    cancelTab(index);
  };

  const cancelTab = (index) => {
    let updatedTabs = [...tabs];

    if (selectedTab === index) {
      updatedTabs.splice(index, 1);
      
      if (index === 0 && tabs.length === 1) {
        setSelectedTab(null);
      } else {
        const newIndex = index === tabs.length - 1 ? index - 1 : index;
        setSelectedTab(newIndex);
      }
    } else {
      if (selectedTab > index) {
        setSelectedTab(selectedTab - 1);
      }

      updatedTabs.splice(index, 1);
    }

    setTabs(updatedTabs);
  };

  const addTab = (element) => {
    let addedTabIndex = null;
    if(element.contentType === "Toolkits") {
      setToolkitDetails(element);
    }

    const isExistingTab = tabs.some(
      (tab) => tab.id === element.id && tab.name === element.name && tab.contentType === element.contentType && element.contentType !== 'Create_Agent'
    );

    if (!isExistingTab) {
      const updatedTabs= [...tabs, element];
      setTabs(updatedTabs);
      addedTabIndex = updatedTabs.length - 1;
      setSelectedTab(addedTabIndex);
    } else {
      const existingTabIndex = tabs.findIndex(
        (tab) => tab.id === element.id && tab.name === element.name && tab.contentType === element.contentType
      );
      setSelectedTab(existingTabIndex);
    }
  };

  const selectTab = (element, index) => {
    setSelectedTab(index);
    if(element.contentType === "Toolkits") {
      setToolkitDetails(element);
    }
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
    const openNewTab = (eventData) => {
      addTab(eventData.element);
      setSource(eventData.source || null);
    };

    const removeTab = (eventData) => {
      const newAgentTabIndex = tabs.findIndex(
        (tab) => tab.id === eventData.id && tab.name === eventData.name && tab.contentType === eventData.contentType
      );
      cancelTab(newAgentTabIndex);
    };

    EventBus.on('openNewTab', openNewTab);
    EventBus.on('reFetchAgents', fetchAgents);
    EventBus.on('removeTab', removeTab);

    return () => {
      EventBus.off('openNewTab', openNewTab);
      EventBus.off('reFetchAgents', fetchAgents);
      EventBus.off('removeTab', removeTab);
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
        {selectedView === 'toolkits' && <div><Toolkits sendToolkitData={addTab} toolkits={toolkits}/></div>}
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
            {tabs.map((tab, index) => (
              <div data-tab-id={index} key={index} className={`${styles.tab_box} ${selectedTab === index ? styles.tab_box_selected : ''}`} onClick={() => {selectTab(tab, index)}}>
                <div style={{display:'flex', order:'0'}}>
                  {(tab.contentType === 'Agents' || tab.contentType === 'Create_Agent') && <div className={styles.tab_active}><Image width={13} height={13} src="/images/agents_light.svg" alt="agent-icon"/></div>}
                  {(tab.contentType === 'ToolKits' || tab.contentType === 'Create_Tool') && <div className={styles.tab_active}><Image width={13} height={13} src="/images/tools_light.svg" alt="tools-icon"/></div>}
                  {tab.contentType === 'Settings' && <div className={styles.tab_active}><Image width={13} height={13} src="/images/settings.svg" alt="settings-icon"/></div>}
                  {tab.contentType === 'Marketplace' && <div className={styles.tab_active}><Image width={13} height={13} src="/images/marketplace.svg" alt="marketplace-icon"/></div>}
                  <div style={{marginLeft:'8px'}}><span className={styles.tab_text}>{tab.name}</span></div>
                </div>
                <div onClick={(e) => closeTab(e, index)} className={styles.tab_active} style={{order:'1'}}><Image width={13} height={13} src="/images/close_light.svg" alt="close-icon"/></div>
              </div>
            ))}
          </div>
        </div>
        <div className={styles.tab_detail} style={tabs.length > 0 ? {backgroundColor:'#2F2C40',overflowX:'hidden'} : {}}>
          <div style={{padding:'0 5px 5px 5px'}}>
            {tabs.map((tab, index) => (
              <div key={index}>
                {selectedTab === index && <div>
                  {tab.contentType === 'Agents' && <AgentWorkspace agentId={tab.id} selectedView={selectedView}/>}
                  {tab.contentType === 'Toolkits' && <ToolkitWorkspace toolkitDetails={toolkitDetails}/>}
                  {tab.contentType === 'Settings' && <Settings organisationId={organisationId} />}
                  {tab.contentType === 'Marketplace' && <Market env={env} source={source} selectedView={selectedView}/>}
                  {tab.contentType === 'Create_Agent' && <AgentTemplatesList organisationId={organisationId} sendAgentData={addTab} selectedProjectId={selectedProjectId} fetchAgents={fetchAgents} toolkits={toolkits}/>}
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