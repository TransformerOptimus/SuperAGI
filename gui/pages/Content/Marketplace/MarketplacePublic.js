import React, { useState, useEffect, useRef } from 'react';
import Image from "next/image";
import styles from './Market.module.css';
import Embeddings from './Embeddings';
import Market from './Market';
import MarketTools from './MarketTools';
import SearchBox from './SearchBox';
import EachTool from './EachTool';
import {fetchAgentTemplateConfig} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import AgentTemplate from "@/pages/Content/Marketplace/AgentTemplate";
import {arEG} from "date-fns/locale";

export default function MarketplacePublic() {
    // const [activeTab, setActiveTab] = useState('market_agents'); // State to track the active tab
    const [searchTerm, setSearchTerm] = useState('');
    const [Itemclicked, setItemclicked] = useState(false);
    const [agentTemplateData, setAagentTemplateData] = useState([]);


    return (
        <div style={{height:'100vh',width:'100%'}}>
             <div style={{height:'6.5vh',display:'flex',width:'100%'}}>
                 <div className="superAgiLogo" style={{paddingLeft:'24px'}}><Image width={132} height={24} src="/images/sign-in-logo.svg" alt="super-agi-logo"/>
                    <div className={styles.vertical_line} />
                    <div className={styles.topbar_heading}>&nbsp;marketplace</div>
                 </div>
                 <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center',width:'100%',paddingRight:'24px' }}>
                     <button style={{ marginRight: '7px' }} className="secondary_button">
                         Sign Up
                     </button>
                     <button className="primary_button">Try for free today!</button>
                 </div>
             </div>
            <div style={{height:'92.5vh',width:'99vw',background: 'rgba(255, 255, 255, 0.08)',marginLeft:'8px',borderRadius: '8px'}}>
                <Market />
            </div>
        </div>
    );
};


