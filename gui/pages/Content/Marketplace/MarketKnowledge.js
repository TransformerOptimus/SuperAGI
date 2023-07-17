import React, {useEffect, useState} from "react";
import Image from "next/image";
import styles from './Market.module.css';
import {EventBus} from "@/utils/eventBus";
import {loadingTextEffect} from "@/utils/utils";
import axios from 'axios';
import {fetchKnowledgeTemplateList} from "@/pages/api/DashboardService";

export default function MarketKnowledge() {
  const [knowledgeTemplates, setKnowledgeTemplates] = useState([])
  const [showMarketplace, setShowMarketplace] = useState(false);
  const [isLoading, setIsLoading] = useState(true)
  const [loadingText, setLoadingText] = useState("Loading Knowledge Templates");

  useEffect(() => {
    loadingTextEffect('Loading Knowledge Templates', setLoadingText, 500);

    if (window.location.href.toLowerCase().includes('marketplace')) {
      setShowMarketplace(true);
      axios.get(`https://app.superagi.com/api/knowledge/get/list?page=0`)
        .then((response) => {
          const data = response.data || [];
          setKnowledgeTemplates(data);
          setIsLoading(false);
        })
        .catch((error) => {
          console.error('Error fetching knowledge templates:', error);
        });
    } else {
      fetchKnowledgeTemplateList()
        .then((response) => {
          const data = response.data || [];
          setKnowledgeTemplates(data);
          setIsLoading(false);
        })
        .catch((error) => {
          console.error('Error fetching knowledge templates:', error);
        });
    }
  }, []);

  function handleTemplateClick(item) {
    const contentType = 'knowledge_template';
    EventBus.emit('openTemplateDetails', {item, contentType});
  }

  return (
    <div style={showMarketplace ? {marginLeft: '8px'} : {marginLeft: '3px'}}>
      <div className={styles.rowContainer} style={{maxHeight: '78vh', overflowY: 'auto'}}>
        {!isLoading ? <div>
          {knowledgeTemplates.length > 0 ? <div className={styles.resources}>{knowledgeTemplates.map((item, index) => (
            <div className={styles.market_tool} key={item.id} style={{cursor: 'pointer'}}
                 onClick={() => handleTemplateClick(item)}>
              <div style={{display: 'inline', overflow: 'auto'}}>
                {/*<Image style={{borderRadius: '25px',background:'black',position:'absolute'}} width={40} height={40} src="/images/app-logo-light.png" alt="tool-icon"/>*/}
                <div>{item.name}</div>
                <div style={{color: '#888888', lineHeight: '16px'}}>by {item.contributed_by}</div>
                <div className={styles.tool_description}>{item.description}</div>
              </div>
            </div>
          ))}</div> : <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            marginTop: '40px',
            width: '100%'
          }}>
            <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions"/>
            <span className={styles.feed_title} style={{marginTop: '8px'}}>No Knowledge found!</span>
          </div>}
        </div> : <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '75vh'}}>
          <div className="signInInfo" style={{fontSize: '16px', fontFamily: 'Source Code Pro'}}>{loadingText}</div>
        </div>}
      </div>
    </div>
  )
}