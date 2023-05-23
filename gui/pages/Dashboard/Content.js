import React, {useState} from 'react';
import Agents from '../Content/Agents/Agents';
import AgentDetail from '../Content/Agents/AgentDetail';
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
      return newArray;
    });
  };

  const addTab = (element) => {
    const updatedElement = {
      ...element,
      contentType: "Agents"
    };

    if (!tabs.includes(updatedElement)) {
      const updatedTabs = [...tabs, updatedElement];
      setTabs(updatedTabs);
    }
    handleTabSelection(updatedElement);
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
        <div>
          <div className={styles.tabs}>
            {tabs.map((tab, index) => (
              <div key={tab.id}>
                <div className={`${styles.tab_box} ${selectedTab.id === tab.id ? styles.tab_box_selected : ''}`} onClick={() => handleTabSelection(tab)}>
                  <div style={{display:'flex', order:'0'}}>
                    <div className={styles.tab_active}><Image width={13} height={13} src="/images/agents_light.png" alt="active-icon"/></div>
                    <div style={{marginLeft:'8px'}}><span className={styles.tab_text}>{tab.name}</span></div>
                  </div>
                  <div onClick={() => closeTab(index)} className={styles.tab_active} style={{order:'1'}}><Image width={13} height={13} src="/images/close_light.png" alt="close-icon"/></div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className={styles.tab_detail} style={tabs.length > 0 ? {backgroundColor:'#2F2C40'} : {}}>
          <div style={{padding:'5px'}}>
            {tabs.map((tab, index) => (
              <div key={tab.id}>
                {tab.id === selectedTab.id && tab.contentType === 'Agents' && <div>
                  {tab.state !== 'DRAFT' ? (
                    <div>
                      <AgentDetail agent={tab}/>
                    </div>
                  ) : (
                    <div className={styles.create_agent}>
                      <div className="row">
                        <div className="col-3"></div>
                        <div className="col-6">
                          <AgentCreate agent={tab}/>
                        </div>
                        <div className="col-3"></div>
                      </div>
                    </div>
                  )}
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
