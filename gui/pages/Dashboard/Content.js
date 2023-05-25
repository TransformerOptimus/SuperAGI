import React, {useState} from 'react';
import Agents from '../Content/Agents/Agents';
import AgentWorkspace from '../Content/Agents/AgentWorkspace';
import AgentCreate from '../Content/Agents/AgentCreate';
import Tools from '../Content/Tools/Tools';
import styles from './Dashboard.module.css';
import Image from "next/image";

export default function Content({selectedView}) {
  const tabsArray = []
  const [tabs, setTabs] = useState(tabsArray)
  const [selectedTab, setSelectedTab] = useState(null)

  const closeTab = (indexToDelete) => {
    setTabs((prevArray) => {
      const newArray = [...prevArray];
      newArray.splice(indexToDelete, 1);
      if(tabs.length > 0) {
        handleTabSelection(tabs[indexToDelete - 1] ? tabs[indexToDelete - 1] : tabs[indexToDelete + 1])
      } else {
        handleTabSelection(null)
      }
      return newArray;
    });
  };

  const addTab = (element) => {
    if (!tabs.includes(element)) {
      const updatedTabs = [...tabs, element];
      setTabs(updatedTabs);
    }
    handleTabSelection(element);
  };

  const handleTabSelection = (tab) => {
    setSelectedTab(tab);
  };

  return (<>
    <div style={{display:'flex',height:'100%'}}>
      <div className={styles.item_list} style={selectedView === '' ? {width:'0vw'} : {width:'13vw'}}>
        {selectedView === 'agents' && <Agents sendAgentData={addTab}/>}
        {selectedView === 'tools' && <Tools sendToolData={addTab}/>}
      </div>
      <div className={styles.main_workspace} style={selectedView === '' ? {width:'93.5vw',paddingLeft:'10px'} : {width:'80.5vw'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'center'}}>
          <div className={styles.tabs}>
            {tabs.map((tab, index) => (
              <div key={tab.id}>
                <div className={`${styles.tab_box} ${selectedTab.id === tab.id ? styles.tab_box_selected : ''}`} onClick={() => handleTabSelection(tab)}>
                  <div style={{display:'flex', order:'0'}}>
                    {(tab.contentType === 'Agents' || tab.contentType === 'Create_Agent') && <div className={styles.tab_active}><Image width={13} height={13} src="/images/agents_light.png" alt="agent-icon"/></div>}
                    {tab.contentType === 'Tools' && <div className={styles.tab_active}><Image width={13} height={13} src="/images/tools_light.png" alt="tools-icon"/></div>}
                    <div style={{marginLeft:'8px'}}><span className={styles.tab_text}>{tab.name}</span></div>
                  </div>
                  <div onClick={() => closeTab(index)} className={styles.tab_active} style={{order:'1'}}><Image width={13} height={13} src="/images/close_light.png" alt="close-icon"/></div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className={styles.tab_detail} style={tabs.length > 0 ? {backgroundColor:'#2F2C40'} : {}}>
          <div style={{padding:'0 5px 5px 5px'}}>
            {tabs.map((tab) => (
              <div key={tab.id}>
                {tab.id === selectedTab.id && <div>
                  {tab.contentType === 'Agents' && <AgentWorkspace agent={tab}/>}
                  {tab.contentType === 'Create_Agent' && <div className={styles.create_agent}>
                    <div className="row">
                      <div className="col-3"></div>
                      <div className="col-6" style={{overflowY:'scroll'}}>
                        <AgentCreate agent={tab}/>
                      </div>
                      <div className="col-3"></div>
                    </div>
                  </div>}
                </div>}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  </>
  );
}
