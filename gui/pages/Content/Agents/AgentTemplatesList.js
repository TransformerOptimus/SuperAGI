import React, {useEffect, useState} from "react";
import Image from "next/image";
import styles from '../Marketplace/Market.module.css';
import {fetchAgentTemplateList, fetchAgentTemplateListLocal, getAgentDetails, getAgents} from "@/pages/api/DashboardService";
import AgentCreate from "@/pages/Content/Agents/AgentCreate";

export default function AgentTemplatesList({sendAgentData, selectedProjectId, fetchAgents, tools, organisationId}){
    const [agentTemplates, setAgentTemplates] = useState([])
    const [createAgentClicked, setCreateAgentClicked] = useState(false)
    const [sendTemplate, setSendTemplate] = useState(null)

    useEffect(() => {
        fetchAgentTemplateListLocal()
            .then((response) => {
                const data = response.data || [];
                setAgentTemplates(data)
            })
            .catch((error) => {
                console.error('Error fetching agent templates:', error);
            });
    }, [])

    function redirectToCreateAgent() {
        setCreateAgentClicked(true);
    }

    function handleTemplateClick(item) {
        setSendTemplate(item);
        setCreateAgentClicked(true);
    }

    return (
        <div>
            {!createAgentClicked &&
                <div>
                <div className='row' style={{marginTop: '1%'}}>
                    <div className='col-12'>
                        <span className={styles.description_heading}
                              style={{fontWeight:'400',verticalAlign:'text-top',marginLeft:'10px',fontSize:'16px'}}>Choose a template</span>
                        <button className="primary_button" onClick={redirectToCreateAgent}
                                style={{float: 'right',marginRight: '3px'}}>&nbsp;Build From Scratch
                        </button>
                    </div>
                </div>
                <div className={styles.rowContainer} style={{maxHeight: '78vh',overflowY: 'auto',marginTop:'10px',marginLeft:'3px'}}>
                    <div className={styles.resources}>
                        {agentTemplates.map((item, index) => (
                            <div className={styles.market_tool} key={item.id} style={{cursor: 'pointer',height:'100px'}}
                                 onClick={() => handleTemplateClick(item)}>
                                <div style={{display: 'inline',overflow:'auto'}}>
                                    <div>{item.name}</div>
                                    <div className={styles.tool_description} style={{marginTop:'10px'}}>{item.description}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>}
            {createAgentClicked && <AgentCreate organisationId={organisationId} sendAgentData={sendAgentData} selectedProjectId={selectedProjectId} fetchAgents={fetchAgents} tools={tools} template={sendTemplate} />}
        </div>
    )
};
