import React, {useEffect, useRef, useState} from 'react';
import Agents from '../Content/Agents/Agents';
import Knowledge from '../Content/Knowledge/Knowledge';
import AddKnowledge from '../Content/Knowledge/AddKnowledge';
import KnowledgeDetails from '../Content/Knowledge/KnowledgeDetails';
import AgentWorkspace from '../Content/Agents/AgentWorkspace';
import AgentCreate from '../Content/Agents/AgentCreate';
import ToolkitWorkspace from '../Content/./Toolkits/ToolkitWorkspace';
import Toolkits from '../Content/./Toolkits/Toolkits';
import Settings from "./Settings/Settings";
import styles from './Dashboard.module.css';
import ApmDashboard from "../Content/APM/ApmDashboard";
import Image from "next/image";
import {EventBus} from "@/utils/eventBus";
import {
  getAgents,
  getToolKit,
  getKnowledge,
  getLastActiveAgent,
  sendGoogleCreds,
  sendTwitterCreds
} from "@/pages/api/DashboardService";
import Market from "../Content/Marketplace/Market";
import AgentTemplatesList from '../Content/Agents/AgentTemplatesList';
import {useRouter} from 'next/router';
import querystring from 'querystring';
import styles1 from '../Content/Agents/Agents.module.css';
import AddTool from "@/pages/Content/Toolkits/AddTool";
import {createInternalId, resetLocalStorage, preventDefault} from "@/utils/utils";
import AddDatabase from "@/pages/Dashboard/Settings/AddDatabase";
import DatabaseDetails from "@/pages/Dashboard/Settings/DatabaseDetails";

export default function Content({env, selectedView, selectedProjectId, organisationId}) {
  const [tabs, setTabs] = useState([]);
  const [selectedTab, setSelectedTab] = useState(null);
  const [agents, setAgents] = useState(null);
  const [toolkits, setToolkits] = useState(null);
  const [knowledge, setKnowledge] = useState(null);
  const tabContainerRef = useRef(null);
  const [toolkitDetails, setToolkitDetails] = useState({});
  const [starModal, setStarModal] = useState(false);
  const router = useRouter();
  const multipleTabContentTypes = ['Create_Agent', 'Add_Toolkit', 'Add_Knowledge', 'Add_Database','Edit_Agent'];
  const [isApmOpened, setIsApmOpened] = useState(false);
  const [prevView, setPrevView] = useState(null);

  useEffect(() => {
    if (prevView !== selectedView) {
      const apmTab = tabs.find(tab => tab.contentType === 'APM');
      setIsApmOpened(!!apmTab);
      setPrevView(selectedView);
    }
  }, [selectedView, tabs, prevView]);

  async function fetchAgents() {
    try {
      const response = await getAgents(selectedProjectId);
      const data = response.data || [];
      const updatedData = data.map(item => {
        return {...item, contentType: "Agents"};
      });
      setAgents(updatedData);
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  }

  function getAgentList() {
    fetchAgents()
      .then(() => {
        console.log('Agents fetched successfully!');
      })
      .catch((error) => {
        console.error('Error fetching agents:', error);
      });
  }

  async function fetchToolkits() {
    try {
      const response = await getToolKit();
      const data = response.data || [];
      const updatedData = data.map(item => {
        let updatedName = item.name === "Web Scrapper Toolkit" ? "Web Scraper Toolkit" : item.name;
        return {...item,name: updatedName,  contentType: "Toolkits", isOpen: false, internalId: createInternalId()};
      });
      setToolkits(updatedData);
    } catch (error) {
      console.error('Error fetching toolkits:', error);
    }
  }

  function getToolkitList() {
    fetchToolkits()
      .then(() => {
        console.log('Toolkits fetched successfully!');
      })
      .catch((error) => {
        console.error('Error fetching toolkits:', error);
      });
  }

  async function fetchKnowledge() {
    try {
      const response = await getKnowledge();
      const data = response.data || [];
      const updatedData = data.map(item => {
        return {...item, contentType: "Knowledge", internalId: createInternalId()};
      });
      setKnowledge(updatedData);
    } catch (error) {
      console.error('Error fetching knowledge:', error);
    }
  }

  function getKnowledgeList() {
    fetchKnowledge()
      .then(() => {
        console.log('Knowledge fetched successfully!');
      })
      .catch((error) => {
        console.error('Error fetching knowledge:', error);
      });
  }

  useEffect(() => {
    getAgentList();
    getToolkitList();
  }, [selectedProjectId])

  useEffect(() => {
    getKnowledgeList();
  }, [organisationId])

  const cancelTab = (index, contentType, internalId) => {
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

    resetLocalStorage(contentType, internalId);
    setTabs(updatedTabs);
  };

  const addTab = (element) => {
    let addedTabIndex = null;
    if (element.contentType === "Toolkits") {
      setToolkitDetails(element);
    }

    const isExistingTab = tabs.some(
      (tab) => tab.id === element.id && tab.name === element.name && tab.contentType === element.contentType && !multipleTabContentTypes.includes(element.contentType)
    );

    if (!isExistingTab) {
      const updatedTabs = [...tabs, element];
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
    if (element.contentType === "Toolkits") {
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

    const queryParams = router.asPath.split('?')[1];
    const parsedParams = querystring.parse(queryParams);
    parsedParams["toolkit_id"] = toolkitDetails.toolkit_id;

    if (window.location.href.indexOf("twitter_creds") > -1) {
      parsedParams["toolkit_id"] = localStorage.getItem("twitter_toolkit_id") || null;
      const params = JSON.stringify(parsedParams)

      sendTwitterCreds(params)
        .then((response) => {
          console.log("Authentication completed successfully");
        })
        .catch((error) => {
          console.error("Error fetching data: ", error);
        })
    }

    if (window.location.href.indexOf("google_calendar_creds") > -1) {
      const toolkit_id = localStorage.getItem("google_calendar_toolkit_id") || null;
      let data = Object.keys(parsedParams)[0];
      let params = JSON.parse(data);

      sendGoogleCreds(params, toolkit_id)
        .then((response) => {
          console.log("Authentication completed successfully");
        })
        .catch((error) => {
          console.error("Error fetching data: ", error);
        })
    }
  }, [selectedTab]);

  useEffect(() => {
    const openNewTab = (eventData) => {
      addTab(eventData.element);
    };

    const openToolkitTab = (eventData) => {
      const toolkit = toolkits?.find((toolkit) => toolkit.tools.some((tool) => tool.id === eventData.toolId));
      if (toolkit) {
        localStorage.setItem('toolkit_tab_' + String(toolkit.internalId), 'tools_included');
        addTab(toolkit);
      }
    }

    const removeTab = (eventData) => {
      const element = eventData.element;
      const tabIndex = tabs.findIndex(
        (tab) => tab.id === element.id &&
          tab.name === element.name &&
          tab.contentType === element.contentType &&
          tab.internalId === element.internalId
      );
      cancelTab(tabIndex, element.contentType, element.internalId);
    };

    EventBus.on('openNewTab', openNewTab);
    EventBus.on('reFetchAgents', getAgentList);
    EventBus.on('reFetchKnowledge', getKnowledgeList);
    EventBus.on('removeTab', removeTab);
    EventBus.on('openToolkitTab', openToolkitTab);

    return () => {
      EventBus.off('openNewTab', openNewTab);
      EventBus.off('reFetchAgents', getAgentList);
      EventBus.off('reFetchKnowledge', getKnowledgeList);
      EventBus.off('removeTab', removeTab);
    };
  });

  async function fetchLastActive() {
    try {
      const response = await getLastActiveAgent(selectedProjectId);
      addTab(response.data);
    } catch (error) {
      console.error('Error fetching last active agent:', error);
    }
  }

  function getLastActive() {
    fetchLastActive()
      .then(() => {
        console.log('Last active agent fetched successfully!');
      })
      .catch((error) => {
        console.error('Error fetching last active agent:', error);
      });
  }

  const openGithubRepo = () => {
    window.open('https://github.com/TransformerOptimus/SuperAGI', '_blank');
    localStorage.setItem('repo_starred', 'starred');
    setStarModal(false);
  };

  const closeStarModal = () => {
    const closedTime = Date.now();
    localStorage.setItem('popup_closed_time', JSON.stringify(closedTime));
    setStarModal(false);
  };

  useEffect(() => {
    const last_closed_time = localStorage.getItem('popup_closed_time');
    const minTime = 4 * 24 * 60 * 60 * 1000;
    const repo_starred = localStorage.getItem('repo_starred');

    if (!repo_starred && Date.now() - JSON.parse(last_closed_time) > minTime) {
      setStarModal(true);
    }
  }, []);

  return (<>
      <div style={{display: 'flex', height: '100%'}}>
        {(selectedView === 'agents' || selectedView === 'toolkits' || selectedView === 'knowledge') &&
          <div className={styles.item_list} style={{width: '13vw'}}>
            {selectedView === 'agents' && <div><Agents sendAgentData={addTab} agents={agents}/></div>}
            {selectedView === 'toolkits' && <div><Toolkits env={env} sendToolkitData={addTab} toolkits={toolkits}/></div>}
            {selectedView === 'knowledge' && <div><Knowledge sendKnowledgeData={addTab} knowledge={knowledge}/></div>}
          </div>}

        {tabs.length <= 0 ? <div className={styles.main_workspace} style={selectedView === '' ? {
          width: '93.5vw',
          paddingLeft: '10px'
        } : {width: '80.5vw'}}>
          <div className={styles.empty_state}>
            <div>
              <div><Image width={264} height={144} src="/images/watermark.png" alt="empty-state"/></div>
              <div style={{width: '100%', display: 'flex', justifyContent: 'center', marginTop: '30px'}}>
                <button onClick={() => addTab({
                  id: -1,
                  name: "new agent",
                  contentType: "Create_Agent",
                  internalId: createInternalId()
                })} className={styles.empty_state_button}>
                  Create new agent&nbsp;<Image width={17} height={17} src="/images/arrow_forward_secondary.svg"
                                               alt="forward-arrow"/>
                </button>
              </div>
              {agents && agents.length > 0 &&
                <div style={{width: '100%', display: 'flex', justifyContent: 'center', marginTop: '12px'}}>
                  <button onClick={getLastActive} className={styles.empty_state_button}>
                    View last active agent&nbsp;<Image width={17} height={17} src="/images/arrow_forward_secondary.svg"
                                                       alt="forward-arrow"/>
                  </button>
                </div>}
              {env !== 'PROD' &&
                <div style={{width: '100%', display: 'flex', justifyContent: 'center', marginTop: '12px'}}>
                  <button onClick={() => addTab({
                    id: -2,
                    name: "new tool",
                    contentType: "Add_Toolkit",
                    internalId: createInternalId()
                  })} className={styles.empty_state_button}>
                    Add custom tool&nbsp;<Image width={17} height={17} src="/images/arrow_forward_secondary.svg"
                                                alt="forward-arrow"/>
                  </button>
                </div>}
              <div style={{width: '100%', display: 'flex', justifyContent: 'center', marginTop: '12px'}}>
                <button onClick={() => addTab({id: -3, name: "Settings", contentType: "Settings"})}
                        className={styles.empty_state_button}>
                  Go to settings&nbsp;<Image width={17} height={17} src="/images/arrow_forward_secondary.svg"
                                             alt="forward-arrow"/>
                </button>
              </div>
            </div>
          </div>
        </div> : <div className={styles.main_workspace}
                      style={(selectedView === 'agents' || selectedView === 'toolkits' || selectedView === 'knowledge') ? {width: '80.5vw'} : {width: '100%'}}>
          <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%'}}>
            <div className={styles.tabs} ref={tabContainerRef}>
              {tabs.map((tab, index) => (
                <div data-tab-id={index} key={index}
                     className={`${styles.tab_box} ${selectedTab === index ? styles.tab_box_selected : ''}`}
                     onClick={() => {
                       selectTab(tab, index)
                     }}>
                  <div style={{display: 'flex', order: '0', overflowX: 'hidden'}}>
                    {(tab.contentType === 'Agents' || tab.contentType === 'Create_Agent' || tab.contentType === 'Edit_Agent') &&
                      <div className={styles.tab_active}><Image width={13} height={13} src="/images/agents_light.svg"
                                                                alt="agent-icon"/></div>}
                    {(tab.contentType === 'Toolkits' || tab.contentType === 'Add_Toolkit') &&
                      <div className={styles.tab_active}><Image width={13} height={13} src="/images/tools_light.svg"
                                                                alt="tools-icon"/></div>}
                    {(tab.contentType === 'Knowledge' || tab.contentType === 'Add_Knowledge') &&
                      <div className={styles.tab_active}><Image width={13} height={13} src="/images/knowledge.svg"
                                                                alt="knowledge-icon"/></div>}
                    {(tab.contentType === 'Database' || tab.contentType === 'Add_Database') &&
                      <div className={styles.tab_active}><Image width={13} height={13} src="/images/database.svg"
                                                                alt="database-icon"/></div>}
                    {tab.contentType === 'Settings' &&
                      <div className={styles.tab_active}><Image width={13} height={13} src="/images/settings.svg"
                                                                alt="settings-icon"/></div>}
                    {tab.contentType === 'Marketplace' &&
                      <div className={styles.tab_active}><Image width={13} height={13} src="/images/marketplace.svg"
                                                                alt="marketplace-icon"/></div>}
                    {tab.contentType === 'APM' &&
                      <div className={styles.tab_active}><Image width={13} height={13} src="/images/apm.svg"
                                                                alt="apm-icon"/></div>}
                    <div style={{marginLeft: '8px'}}><span className={styles.tab_text}>{tab.name}</span></div>
                  </div>
                  <div onClick={(e) => {
                    e.stopPropagation();
                    cancelTab(index, tab.contentType, tab.internalId || 0)
                  }} className={styles.tab_active} style={{order: '1'}}><Image width={13} height={13}
                                                                               src="/images/close.svg"
                                                                               alt="close-icon"/></div>
                </div>
              ))}
            </div>
          </div>
          <div className={styles.tab_detail}
               style={tabs.length > 0 ? {backgroundColor: '#2F2C40', overflowX: 'hidden'} : {}}>
            <div style={{padding: '0 5px 5px 5px'}}>
              {tabs.map((tab, index) => (
                <div key={index}>
                  {selectedTab === index && <div>
                    {tab.contentType === 'Agents' &&
                      <AgentWorkspace env={env} internalId={tab.internalId || index} agentId={tab.id} agentName={tab.name}
                                      selectedView={selectedView}
                                      agents={agents} fetchAgents={getAgentList} sendAgentData={addTab} />}
                    {tab.contentType === 'Toolkits' &&
                      <ToolkitWorkspace env={env} internalId={tab.internalId || index}
                                        toolkitDetails={toolkitDetails}/>}
                    {tab.contentType === 'Knowledge' &&
                      <KnowledgeDetails internalId={tab.internalId || index} knowledgeId={tab.id}/>}
                    {tab.contentType === 'Database' &&
                      <DatabaseDetails internalId={tab.internalId || index} databaseId={tab.id}/>}
                    {tab.contentType === 'Knowledge' &&
                      <KnowledgeDetails internalId={tab.internalId || index} knowledgeId={tab.id}/>}
                    {tab.contentType === 'Database' &&
                      <DatabaseDetails internalId={tab.internalId || index} databaseId={tab.id}/>}
                    {tab.contentType === 'Settings' &&
                      <Settings organisationId={organisationId} sendDatabaseData={addTab}/>}
                    {tab.contentType === 'Marketplace' && <Market env={env} selectedView={selectedView}/>}
                    {tab.contentType === 'Add_Toolkit' && <AddTool internalId={tab.internalId || index}/>}
                    {tab.contentType === 'Add_Knowledge' &&
                      <AddKnowledge internalId={tab.internalId || index} sendKnowledgeData={addTab}/>}
                    {tab.contentType === 'Add_Database' &&
                      <AddDatabase internalId={tab.internalId || index} sendDatabaseDetailsData={addTab}/>}
                    {tab.contentType === 'Create_Agent' &&
                      <AgentTemplatesList knowledge={knowledge} internalId={tab.internalId || index}
                                          organisationId={organisationId} sendKnowledgeData={addTab}
                                          sendAgentData={addTab} selectedProjectId={selectedProjectId}
                                          fetchAgents={getAgentList} toolkits={toolkits} env={env} />}
                    {tab.contentType === 'APM' && <ApmDashboard />}
                    {tab.contentType === 'Edit_Agent' &&
                        <AgentCreate knowledge={knowledge} internalId={tab.internalId || index}
                                     organisationId={organisationId} sendKnowledgeData={addTab}
                                     sendAgentData={addTab} selectedProjectId={selectedProjectId} editAgentId={tab.id}
                                     fetchAgents={getAgentList} toolkits={toolkits} template={null} edit={true} agents={agents}/>}
                  </div>}
                </div>
              ))}
            </div>
          </div>
        </div>}

        {starModal && (<div className="modal" onClick={closeStarModal}>
          <div className="modal-content" style={{width: '35%'}} onClick={preventDefault}>
            <div className={styles1.detail_name} style={{width: '100%', textAlign: 'center'}}>Support the project by
              leaving a star on GitHub repository
            </div>
            <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
              <button className="secondary_button" style={{marginTop: '10px', width: 'fit-content'}}
                      onClick={openGithubRepo}>
                Leave a ⭐ star on GitHub
              </button>
            </div>
            <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
              <div className="cancel_action" onClick={closeStarModal}>
                I’ll do it later
              </div>
            </div>
          </div>
        </div>)}
      </div>
    </>
  );
}