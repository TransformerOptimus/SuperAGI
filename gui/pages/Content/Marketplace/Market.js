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
    const [activeTab, setActiveTab] = useState('market_agents');
    const [searchTerm, setSearchTerm] = useState('');
    const [itemClicked, setItemClicked] = useState(false);
    const [agentTemplateData, setAgentTemplateData] = useState([]);

    const handleSearch = (term) => {
      setSearchTerm(term);
    };

    const handleToolClick = (clicked) => {
      setItemClicked(clicked);
    };

    useEffect(() => {
        const handleOpenTemplateDetails = (item) => {
            setAgentTemplateData(item);
            setItemClicked(true);
        };

        const handleBackClick = ()=>{
            setItemClicked(false);
        }

        EventBus.on('openTemplateDetails', handleOpenTemplateDetails);
        EventBus.on('goToMarketplace', handleBackClick);

        return () => {
            EventBus.off('openTemplateDetails', handleOpenTemplateDetails);
            EventBus.off('goToMarketplace', handleBackClick);
        };
    }, []);

  return (
    <div>
        {!itemClicked ? <div className={styles.empty_state}>
          <div style={{width:'100%',display:'flex',flexDirection:'column'}}>
              <div className={styles.detail_top}>

              <div style={{display:'flex',overflowX:'scroll',marginLeft:'8px'}}>
                  {/*<div>*/}
                  {/*    <button onClick={() => setActiveTab('market_tools')} className={styles.tab_button} style={activeTab === 'market_tools' ? {background:'#454254',paddingRight:'15px'} : {background:'transparent',paddingRight:'15px'}}>*/}
                  {/*        <Image style={{marginTop:'-1px'}} width={14} height={14} src="/images/tools_light.svg" alt="tools-icon"/>&nbsp;Tools*/}
                  {/*    </button>*/}
                  {/*</div>*/}
                  {/*<div>*/}
                  {/*    <button onClick={() => setActiveTab('market_embeddings')} className={styles.tab_button} style={activeTab === 'market_embeddings' ? {background:'#454254',paddingRight:'15px'} : {background:'transparent',paddingRight:'15px'}}>*/}
                  {/*        <Image style={{marginTop:'-1px'}} width={14} height={14} src="/images/embedding_light.svg" alt="embeddings-icon"/>&nbsp;Embeddings*/}
                  {/*    </button>*/}
                  {/*</div>*/}
                  <div>
                      <button onClick={() => setActiveTab('market_agents')} className={styles.tab_button} style={activeTab === 'market_agents' ? {background:'#454254',paddingRight:'15px'} : {background:'transparent',paddingRight:'15px'}}>
                          <Image style={{marginTop:'-1px'}} width={14} height={14} src="/images/agents_light.svg" alt="agent-template-icon"/>&nbsp;Agent Templates
                      </button>
                  </div>
              </div>

                {/*<div>*/}
                {/*<SearchBox onSearch={handleSearch} />*/}
                {/*</div>*/}
            </div>
            <div>
              {activeTab === 'market_tools' && <MarketTools onToolClick={handleToolClick} />}
              {activeTab === 'market_embeddings' && <Embeddings />}
              {activeTab === 'market_agents' && <MarketAgent />}
            </div>
        </div>
        </div> : <div style={{padding:'0 3px'}}>
            <AgentTemplate template={agentTemplateData} />
        </div>}
    </div>
  );
};


