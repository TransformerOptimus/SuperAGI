import React, {useEffect, useState} from "react";
import Image from "next/image";
import styles from './Market.module.css';
import {fetchAgentTemplateDetails, fetchAgentTemplateList, getAgents} from "@/pages/api/DashboardService";

export default function MarketAgent(){
    const [agentTemplates, setAgentTemplates] = useState([])
    useEffect(() => {
        fetchAgentTemplateList()
            .then((response) => {
                const data = response.data || [];
                console.log(data)
                setAgentTemplates(data)
            })
            .catch((error) => {
                console.error('Error fetching agents:', error);
            });
    }, [])
    return (
        <div>
    <div className={styles.history_box}>
        Agents
    </div>
        <div className={styles.rowContainer}>
            {agentTemplates.map((item, index) => (
                <div className={styles.market_tool} key={item.id}>
                    <div style={{ display: 'inline' }}>
                        <div style={{ paddingTop: '12px', paddingLeft: '6px', paddingRight: '8px' }}>{item.name}</div>
                        <div style={{ paddingLeft: '6px', fontSize: 'x-small', color: 'rgb(96, 96, 96)' }}>by SuperAgi&nbsp;<Image width={14} height={14} src="/images/is_verified.svg" alt="is_verified"/></div>
                        <div style={{ paddingLeft: '6px', fontSize: 'x-small', color: 'rgb(96, 96, 96)' }}>{item.description}</div>
                    </div>
                </div>
            ))}
        </div>

    </div>
    )  
};
