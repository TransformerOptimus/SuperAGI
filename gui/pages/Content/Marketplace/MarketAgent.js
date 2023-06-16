import React, {useEffect, useState} from "react";
import Image from "next/image";
import styles from './Market.module.css';
import {fetchAgentTemplateList} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";

export default function MarketAgent(){
    const [agentTemplates, setAgentTemplates] = useState([])
    const [currentPage, setCurrentPage] = useState(0);

    useEffect(() => {
        fetchAgentTemplateList(currentPage)
            .then((response) => {
                const data = response.data || [];
                console.log(data)
                setAgentTemplates((prevTemplates) => [...prevTemplates, ...data]);
            })
            .catch((error) => {
                console.error('Error fetching agents:', error);
            });
    }, [currentPage])

    function handleTemplateClick(item) {
        EventBus.emit('openTemplateDetails', item);

    }

    return (
        <div>
    {/*<div className={styles.history_box}>*/}
    {/*    Agents*/}
    {/*</div>*/}
             <div className={styles.rowContainer} style={{maxHeight: '78vh',overflowY: 'auto'}}>
                 <div className='row' style={{paddingLeft:'2.5%'}}>
                {agentTemplates.map((item, index) => (
                    <div className={styles.market_tool} key={item.id} style={{cursor: 'pointer'}}  onClick={() => handleTemplateClick(item)}>
                        <div style={{display: 'inline',overflow:'hidden'}}>
                            <div style={{fontWeight:'500'}}>{item.name}</div>
                            <div style={{fontWeight:'500',lineHeight: '14px', color: 'rgb(96, 96, 96)'}}>by SuperAgi&nbsp;<Image width={14} height={14} src="/images/is_verified.svg" alt="is_verified"/></div>
                            <div style={{marginTop: '1%',lineHeight: '14px', color: 'rgb(96, 96, 96)',wordWrap: 'break-word',overflowWrap: 'break-word'}}>{item.description}</div>
                        </div>
                    </div>
                ))}
                 </div>
            </div>
    </div>
    )  
};
