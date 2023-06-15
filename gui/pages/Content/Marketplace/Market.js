import React, { useState, useEffect, useRef } from 'react';
import Image from "next/image";
import styles from './Market.module.css';
import Embeddings from './Embeddings';
import MarketAgent from './MarketAgent';
import MarketTools from './MarketTools';
import SearchBox from './SearchBox';
import EachTool from './EachTool';
import {fetchAgentTemplateConfig} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import AgentTemplate from "@/pages/Content/Marketplace/AgentTemplate";
import {arEG} from "date-fns/locale";

export default function Market() {
    const [activeTab, setActiveTab] = useState('market_agents'); // State to track the active tab
    const [searchTerm, setSearchTerm] = useState('');
    const [Itemclicked, setItemclicked] = useState(false);
    const [agentTemplateData, setAagentTemplateData] = useState([]);
    const handleSearch = (term) => {
      setSearchTerm(term);
      //opt
    };
    const handleToolClick = (clicked) => {
      setItemclicked(clicked);
    };

    useEffect(() => {
        const handleOpenTemplateDetails = (item) => {
            setAagentTemplateData(item)
            setItemclicked(true)
        };
        const handleBackClick = ()=>{
            setItemclicked(false)
        }
        EventBus.on('openTemplateDetails', handleOpenTemplateDetails);
        EventBus.on('goToMarketplace', handleBackClick);
        return () => {
            EventBus.off('openTemplateDetails', handleOpenTemplateDetails);
            EventBus.off('goToMarketplace', handleBackClick);
        };
    }, [])

  return (
    <div>
    {!Itemclicked && <div className={styles.empty_state}>
      <div style={{width:'100%',display:'flex',marginTop:'10px',flexDirection:'column'}}>
      <div className={styles.detail_top}>
      
      <div>
        {/*<div className={styles.agent_box} onClick={() => setActiveTab('market_tools')} style={activeTab === 'market_tools' ? {background:'#454254',paddingRight:'15px'} : {background:'transparent',paddingRight:'15px'}}>*/}
        {/*<div ><Image width={17} height={17} src="/images/tools_light.svg" alt="tools-icon"/></div>*/}
        {/*<div className={styles.tab_text}>Tools</div> */}
        {/*</div>*/}
        
        {/*<div className={styles.agent_box} onClick={() => setActiveTab('market_embeddings')} style={activeTab === 'market_embeddings' ? {background:'#454254',paddingRight:'15px'} : {background:'transparent',paddingRight:'15px'}}>*/}
        {/*<div><Image width={17} height={17} src="/images/tools_light.svg" alt="tools-icon"/></div>*/}
        {/*<div className={styles.tab_text}>Embeddings</div>*/}
        {/*</div>*/}
        
        <div className={styles.agent_box} onClick={() => setActiveTab('market_agents')} style={activeTab === 'market_agents' ? {background:'#454254',paddingRight:'15px'} : {background:'transparent',paddingRight:'15px'}}>
        <div ><Image width={17} height={17} src="/images/agents_light.svg" alt="tools-icon"/></div>
        <div  className={styles.tab_text}>Agents</div>
        </div>
      </div>

        {/*<div>*/}
        {/*<SearchBox onSearch={handleSearch} />*/}
        {/*</div>*/}
    </div>
    <div>
      {activeTab === 'market_tools' && <div><MarketTools onToolClick={handleToolClick} /></div>}
      {activeTab === 'market_embeddings' && <div><Embeddings /></div>}
      {activeTab === 'market_agents' && <div><MarketAgent /></div>}
    </div>             
    </div>
    </div>}
        {Itemclicked && <AgentTemplate template={agentTemplateData} />}
    </div>
  );
};


