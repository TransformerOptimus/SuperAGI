import React, { useState, useEffect, useRef } from 'react';
import Image from "next/image";
import styles from './Market.module.css';
import Embeddings from './Embeddings';
import MarketAgent from './MarketAgent';
import MarketTools from './MarketTools';
import SearchBox from './SearchBox';

export default function Market() {
    const [activeTab, setActiveTab] = useState('market_tools'); // State to track the active tab
    const [searchTerm, setSearchTerm] = useState('');
    const handleSearch = (term) => {
      setSearchTerm(term);
      //opt
    };

  return (
    <div className={styles.empty_state}>
      <div style={{width:'100%',display:'flex',marginTop:'10px',flexDirection:'column'}}>
      <div className={styles.detail_top}>
      <div >
        <div className={styles.agent_box} onClick={() => setActiveTab('market_tools')}> 
        <div ><Image width={17} height={17} src="/images/tools_light.svg" alt="tools-icon"/></div>
        <div className={styles.tab_text}>Tools</div> 
        </div>
        
        <div className={styles.agent_box} onClick={() => setActiveTab('market_embeddings')}> 
        <div><Image width={17} height={17} src="/images/tools_light.svg" alt="tools-icon"/></div>
        <div className={styles.tab_text}>Embeddings</div>
        </div>
        
        <div className={styles.agent_box} onClick={() => setActiveTab('market_agents')}>
        <div ><Image width={17} height={17} src="/images/agents_light.svg" alt="tools-icon"/></div>
        <div  className={styles.tab_text}>Agents</div>
        </div> 
      </div>
        <div>
        <SearchBox onSearch={handleSearch} />
        </div>
    </div>
    <div>
      {activeTab === 'market_tools' && <div><MarketTools /></div>}
      {activeTab === 'market_embeddings' && <div><Embeddings /></div>}
      {activeTab === 'market_agents' && <div><MarketAgent /></div>}
    </div>             
    </div>
    </div>
  );
};


