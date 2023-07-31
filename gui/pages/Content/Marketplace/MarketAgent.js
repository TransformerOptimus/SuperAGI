import React, {useEffect, useState} from "react";
import Image from "next/image";
import styles from './Market.module.css';
import {fetchAgentTemplateList} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import {loadingTextEffect} from "@/utils/utils";
import axios from 'axios';

export default function MarketAgent() {
  const [agentTemplates, setAgentTemplates] = useState([])
  const [showMarketplace, setShowMarketplace] = useState(false);
  const [isLoading, setIsLoading] = useState(true)
  const [loadingText, setLoadingText] = useState("Loading Agent Templates");

  useEffect(() => {
    loadingTextEffect('Loading Agent Templates', setLoadingText, 500);

    if (window.location.href.toLowerCase().includes('marketplace')) {
      setShowMarketplace(true);
      axios.get('https://app.superagi.com/api/agent_templates/marketplace/list')
        .then((response) => {
          const data = response.data || [];
          setAgentTemplates(data);
          setIsLoading(false);
        })
        .catch((error) => {
          console.error('Error fetching agent templates:', error);
        });
    } else {
      fetchAgentTemplateList()
        .then((response) => {
          const data = response.data || [];
          setAgentTemplates(data);
          setIsLoading(false);
        })
        .catch((error) => {
          console.error('Error fetching agent templates:', error);
        });
    }
  }, []);

  function handleTemplateClick(item) {
    const contentType = 'agent_template';
    EventBus.emit('openTemplateDetails', {item, contentType});
  }

  return (
    <div className={showMarketplace ? 'ml_8' : 'ml_3'}>
      <div className="w_100 overflowY_auto mxh_78vh">
        {!isLoading ? <div>
          {agentTemplates.length > 0 ? <div className={styles.resources}>{agentTemplates.map((item, index) => (
            <div className="market_tool cursor_pointer" key={item.id} onClick={() => handleTemplateClick(item)}>
              <div className="vertical_containers overflow_auto">
                <div>{item.name}</div>
                <div className="color_gray lh_16">by SuperAgi&nbsp;<Image width={14} height={14}
                                                                                            src="/images/is_verified.svg"
                                                                                            alt="is_verified"/></div>
                <div className="text_ellipsis mt_8 color_gray">{item.description}</div>
              </div>
            </div>
          ))}</div> : <div className="center_container mt_40">
            <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions"/>
            <span className="feed_title mt_8">No Agent Templates found!</span>
          </div>}
        </div> : <div className="horizontal_container_center h_75vh">
          <div className="signInInfo text_16 ff_sourceCode">{loadingText}</div>
        </div>}
      </div>
    </div>
  )
};
