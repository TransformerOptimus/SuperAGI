import React, {useEffect, useState} from "react";
import Image from "next/image";
import styles from './Market.module.css';
import {fetchAgentTemplateList} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import {loadingTextEffect} from "@/utils/utils";

export default function MarketAgent(){
    const [agentTemplates, setAgentTemplates] = useState([])
    const [showMarketplace, setShowMarketplace] = useState(false);
    const [isLoading, setIsLoading] = useState(true)
    const [loadingText, setLoadingText] = useState("Loading Templates");

    useEffect(() => {
      loadingTextEffect('Loading Templates', setLoadingText, 500);

      if(window.location.href.toLowerCase().includes('marketplace')) {
          setShowMarketplace(true)
      }

      fetchAgentTemplateList()
        .then((response) => {
            const data = response.data || [];
            setAgentTemplates(data);
            setIsLoading(false);
        })
        .catch((error) => {
            console.error('Error fetching agent templates:', error);
        });
    }, []);

    function handleTemplateClick(item) {
        EventBus.emit('openTemplateDetails', item);
    }

    return (
        <div style={showMarketplace ? { marginLeft:'8px',marginRight:'8px' } : { marginLeft:'3px' }}>
           <div className={styles.rowContainer} style={{maxHeight: '78vh',overflowY: 'auto'}}>
             {!isLoading ? <div className={styles.resources}>
                {agentTemplates.map((item, index) => (
                  <div className={styles.market_tool} key={item.id} style={{cursor: 'pointer'}}  onClick={() => handleTemplateClick(item)}>
                    <div style={{display: 'inline',overflow:'auto'}}>
                      <div>{item.name}</div>
                      <div style={{color: '#888888',lineHeight:'16px'}}>by SuperAgi&nbsp;<Image width={14} height={14} src="/images/is_verified.svg" alt="is_verified"/></div>
                      <div className={styles.tool_description}>{item.description}</div>
                    </div>
                  </div>
                ))}
             </div> : <div style={{display:'flex',justifyContent:'center',alignItems:'center',height:'75vh'}}>
             <div className="signInInfo" style={{fontSize:'16px',fontFamily:'Source Code Pro'}}>{loadingText}</div>
           </div>}
          </div>
    </div>
    )  
};
