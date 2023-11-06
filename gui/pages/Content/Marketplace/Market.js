import React, {useState, useEffect} from 'react';
import Image from "next/image";
import styles from './Market.module.css';
import MarketKnowledge from './MarketKnowledge';
import MarketAgent from './MarketAgent';
import MarketTools from './MarketTools';
import MarketModels from '../Models/MarketModels';
import ToolkitTemplate from './ToolkitTemplate';
import ModelTemplate from "../Models/ModelTemplate";
import {EventBus} from "@/utils/eventBus";
import AgentTemplate from "./AgentTemplate";
import KnowledgeTemplate from "./KnowledgeTemplate";
import {setLocalStorageValue, setLocalStorageArray} from "@/utils/utils";

export default function Market({env, getModels, sendModelData}) {
  const [activeTab, setActiveTab] = useState('market_tools');
  const [itemClicked, setItemClicked] = useState(false);
  const [templateData, setTemplateData] = useState([]);
  const [detailType, setDetailType] = useState('');

  useEffect(() => {
    const marketplace_tab = localStorage.getItem('marketplace_tab');
    if (marketplace_tab) {
      setActiveTab(marketplace_tab);
    }

    const item_clicked = localStorage.getItem('market_item_clicked');
    const detail_type = localStorage.getItem('market_detail_type');
    const market_item = localStorage.getItem('market_item');

    if (item_clicked) {
      setItemClicked(JSON.parse(item_clicked));
      if (detail_type) {
        setDetailType(item_clicked === 'true' ? detail_type : '');
        setTemplateData(item_clicked === 'true' ? JSON.parse(market_item) : []);
      }
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

  const tabData = [
    { id: 'market_tools', label: 'Tools', image: '/images/tools_light.svg' },
    { id: 'market_knowledge', label: 'Knowledge', image: '/images/knowledge.svg' },
    { id: 'market_agents', label: 'Agent Templates', image: '/images/agents_light.svg' },
    { id: 'market_models', label: 'Models', image: '/images/models.svg' },
  ];

  const renderTab = (tab) => {
    if(tab.id === 'market_models' && !(window.location.href.toLowerCase().includes('marketplace')))
      return

    return (
        <button
            key={tab.id}
            onClick={() => switchTab(tab.id)}
            className={activeTab === tab.id ? 'tab_button_selected' : 'tab_button'}
        >
          <Image width={14} height={14} src={tab.image} alt={`${tab.label}-icon`} />
          <span>{tab.label}</span>
        </button>
    );
  };

  const handleOpenTemplateDetails = ({ item, contentType }) => {
    localStorage.setItem('market_detail_type', contentType);
    setDetailType(contentType);
    localStorage.setItem('market_item', JSON.stringify(item));
    setTemplateData(item);
    localStorage.setItem('market_item_clicked', true);
    setItemClicked(true);
  };

  const handleBackClick = () => {
    localStorage.setItem('market_item_clicked', false);
    setItemClicked(false);
  };

  return (
      <div>
        {!itemClicked ? (
            <div className={styles.empty_state}>
              <div style={{ width: '100%', display: 'flex', flexDirection: 'column' }}>
                <div className={styles.detail_top}>
                  <div style={{ display: 'flex', overflowX: 'scroll', marginLeft: '8px' }}>
                    {tabData.map(renderTab)}
                  </div>
                </div>
                <div>
                  {activeTab === 'market_tools' && <MarketTools />}
                  {activeTab === 'market_knowledge' && <MarketKnowledge />}
                  {activeTab === 'market_agents' && <MarketAgent />}
                  {activeTab === 'market_models' && <MarketModels />}
                </div>
              </div>
            </div>
        ) : (
            <div style={{padding: '0 3px'}}>
              {detailType === 'agent_template' && <AgentTemplate env={env} template={templateData}/>}
              {detailType === 'knowledge_template' && <KnowledgeTemplate env={env} template={templateData}/>}
              {detailType === 'tool_template' && <ToolkitTemplate env={env} template={templateData}/>}
              {detailType === 'model_template' && <ModelTemplate env={env} template={templateData} getModels={getModels} sendModelData={sendModelData} />}
            </div>
        )}
      </div>
  );
}

