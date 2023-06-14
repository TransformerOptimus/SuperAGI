import React, {useEffect, useState} from "react";
import Image from "next/image";
import styles from '../Marketplace/Market.module.css';
import {fetchAgentTemplateDetails, fetchAgentTemplateList, fetchAgentTemplateListLocal, getAgentDetails, getAgents} from "@/pages/api/DashboardService";
import styles2 from "@/pages/Content/Marketplace/Market.module.css";
import {EventBus} from "@/utils/eventBus";
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
                console.error('Error fetching agents:', error);
            });
    }, [])
    function redirectToCreateAgent() {
        setCreateAgentClicked(true);
        // EventBus.emit('createAgent', {});
    }
    function handleTemplateClick(item) {
        // EventBus.emit('createAgent', {});
        console.log('in agent create')
        console.log(item)
        setSendTemplate(item);
        console.log(sendTemplate)
        setCreateAgentClicked(true);
    }
    useEffect(() => {
        console.log(sendTemplate); // Log the updated sendTemplate value
    }, [sendTemplate]);
    return (
        <div>
            {!createAgentClicked &&
                <div>
                <div className='row' style={{marginTop: '1%'}}>
                    <div className='col-12'>
                        <span className={styles.description_heading}
                              style={{fontWeight: '400'}}>Choose a template</span>
                        <button className="primary_button" onClick={redirectToCreateAgent}
                                style={{float: 'right'}}>&nbsp;Build From Scratch
                        </button>
                    </div>
                </div>
                <div className={styles.rowContainer} style={{marginTop: '1%'}}>
                    {agentTemplates.map((item, index) => (
                        <div className={styles.market_tool} key={item.id} style={{cursor: 'pointer'}}
                             onClick={() => handleTemplateClick(item)}>
                            <div style={{display: 'inline'}}>
                                <div style={{
                                    paddingTop: '12px',
                                    paddingLeft: '12px',
                                    paddingRight: '12px'
                                }}>{item.name}</div>
                                <div style={{paddingLeft: '12px', fontSize: 'x-small', color: 'rgb(96, 96, 96)'}}>by
                                    SuperAgi&nbsp;<Image width={14} height={14} src="/images/is_verified.svg"
                                                         alt="is_verified"/></div>
                                <div style={{
                                    paddingLeft: '12px',
                                    fontSize: 'x-small',
                                    color: 'rgb(96, 96, 96)'
                                }}>{item.description}</div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>}
            {createAgentClicked && <AgentCreate organisationId={organisationId} sendAgentData={sendAgentData} selectedProjectId={selectedProjectId} fetchAgents={fetchAgents} tools={tools} template={sendTemplate} />}
        </div>
    )
};
