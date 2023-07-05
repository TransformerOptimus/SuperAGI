import React, { useState, useEffect, useRef } from 'react';
import Image from "next/image";
import styles from './Market.module.css';
import Embeddings from './Embeddings';
import MarketAgent from './MarketAgent';
import MarketTools from './MarketTools';
import SearchBox from './SearchBox';
import EachTool from './EachTool';
import {EventBus} from "@/utils/eventBus";
import AgentTemplate from "@/pages/Content/Marketplace/AgentTemplate";
import {setLocalStorageValue, setLocalStorageArray} from "@/utils/utils";

export default function Market({env}) {
    const [activeTab, setActiveTab] = useState('market_tools');
    const [searchTerm, setSearchTerm] = useState('');
    const [itemClicked, setItemClicked] = useState(false);
    const [templateData, setTemplateData] = useState([]);
    const [detailType, setDetailType] = useState('');

    const handleSearch = (term) => {
      setSearchTerm(term);
    };

    const handleToolClick = (clicked) => {
        setLocalStorageValue('market_item_clicked', clicked, setItemClicked);
    };

    useEffect(() => {
        const marketplace_tab = localStorage.getItem('marketplace_tab');
        if(marketplace_tab) {
            setActiveTab(marketplace_tab);
        }

        const item_clicked = localStorage.getItem('market_item_clicked');
        const detail_type = localStorage.getItem('market_detail_type');
        const market_item = localStorage.getItem('market_item');

        if(item_clicked) {
            setItemClicked(JSON.parse(item_clicked));
            if(detail_type) {
                setDetailType(item_clicked === 'true' ? detail_type : '');
                setTemplateData(item_clicked === 'true' ? JSON.parse(market_item) : []);
            }
        }

        const handleOpenTemplateDetails = ({ item, contentType }) => {
            setLocalStorageValue('market_detail_type', contentType, setDetailType);
            setLocalStorageArray('market_item', item, setTemplateData);
            setLocalStorageValue('market_item_clicked', true, setItemClicked);
        };

        const handleBackClick = ()=>{
            setLocalStorageValue('market_item_clicked', false, setItemClicked);
        }

        EventBus.on('openTemplateDetails', handleOpenTemplateDetails);
        EventBus.on('goToMarketplace', handleBackClick);

        return () => {
            EventBus.off('openTemplateDetails', handleOpenTemplateDetails);
            EventBus.off('goToMarketplace', handleBackClick);
        };
    }, []);

    const switchTab = (tab) => {
        setActiveTab(tab);
        localStorage.setItem('marketplace_tab', tab);
    };

  return (
    <div>
        {!itemClicked ? <div className={styles.empty_state}>
          <div style={{width:'100%',display:'flex',flexDirection:'column'}}>
              <div className={styles.detail_top}>

              <div style={{display:'flex',overflowX:'scroll',marginLeft:'8px'}}>
                  <div>
                      <button onClick={() => switchTab('market_tools')} className={styles.tab_button} style={activeTab === 'market_tools' ? {background:'#454254',paddingRight:'15px'} : {background:'transparent',paddingRight:'15px'}}>
                          <Image style={{marginTop:'-1px'}} width={14} height={14} src="/images/tools_light.svg" alt="tools-icon"/>&nbsp;Tools
                      </button>
                  </div>
                  {/*<div>*/}
                  {/*    <button onClick={() => switchTab('market_embeddings')} className={styles.tab_button} style={activeTab === 'market_embeddings' ? {background:'#454254',paddingRight:'15px'} : {background:'transparent',paddingRight:'15px'}}>*/}
                  {/*        <Image style={{marginTop:'-1px'}} width={14} height={14} src="/images/embedding_light.svg" alt="embeddings-icon"/>&nbsp;Embeddings*/}
                  {/*    </button>*/}
                  {/*</div>*/}
                  <div>
                      <button onClick={() => switchTab('market_agents')} className={styles.tab_button} style={activeTab === 'market_agents' ? {background:'#454254',paddingRight:'15px'} : {background:'transparent',paddingRight:'15px'}}>
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
            {detailType === 'agent_template' && <AgentTemplate env={env} template={templateData}/>}
            {detailType === 'tool_template' && <EachTool env={env} template={templateData} />}
        </div>}
    </div>
  );
};


