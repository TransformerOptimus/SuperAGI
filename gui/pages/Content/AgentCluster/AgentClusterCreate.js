import React, { useState, useEffect, useRef } from 'react';
import Image from "next/image";
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles from '../Agents/Agents.module.css';
import {createAgent, uploadFile} from "@/pages/api/DashboardService";
import {formatBytes} from "@/utils/utils";
import {EventBus} from "@/utils/eventBus";
import agentStyles from "@/pages/Content/Agents/Agents.module.css";

export default function AgentClusterCreate({sendAgentData, selectedProjectId, fetchAgents, tools}) {
    const [agentClusterName, setAgentClusterName] = useState("");
    const [agentClusterDescription, setAgentClusterDescription] = useState("");
    const [toolNames, setToolNames] = useState(['GoogleSearch', 'Read File', 'Write File']);
    const [toolDropdown, setToolDropdown] = useState(false);
    const toolRef = useRef(null);

    const handleNameChange = (event) => {
        setAgentClusterName(event.target.value);
    };
    const handleDescriptionChange = (event) => {
        setAgentClusterDescription(event.target.value);
    };
    const handleAddAgent = () => {

    };
    function cancelCreate() {
        EventBus.emit('cancelAgentCreate', {});
    }
    const preventDefault = (e) => {
        e.stopPropagation();
    };
    return (<>
        <div className="row">
            <div className="col-3"></div>
            <div className="col-6" style={{overflowY:'scroll',height:'calc(100vh - 92px)',padding:'25px 20px'}}>
                <div>
                    <div className={styles.page_title}>Create new cluster</div>
                </div>
                <div style={{marginTop:'10px'}}>
                    <div>
                        <label className={styles.form_label}>Name</label>
                        <input className="input_medium" type="text" value={agentClusterName} onChange={handleNameChange}/>
                    </div>
                    <div style={{marginTop: '15px'}}>
                        <label className={styles.form_label}>Description</label>
                        <textarea className="textarea_medium" rows={3} value={agentClusterDescription} onChange={handleDescriptionChange}/>
                    </div>
                    <div style={{marginTop: '15px'}}>
                        <label className={styles.form_label}>Agents</label>
                        <div className="dropdown_container_search" style={{width:'100%'}}>
                            <div className="custom_select_container" onClick={() => setToolDropdown(!toolDropdown)} style={{width:'100%'}}>
                                {toolNames && toolNames.length > 0 ? <div style={{display:'flex',overflowX:'scroll'}}>
                                    {toolNames.map((tool, index) => (<div key={index} className="tool_container" style={{marginTop:'0'}} onClick={preventDefault}>
                                        <div className={styles.tool_text}>{tool}</div>
                                        <div><Image width={12} height={12} src='/images/close_light.svg' alt="close-icon" style={{margin:'-2px -5px 0 2px'}} /></div>
                                    </div>))}
                                </div> : <div style={{color:'#666666'}}>Select Tools</div>}
                                <Image width={20} height={21} src={!toolDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'} alt="expand-icon"/>
                            </div>
                            <div>
                                {toolDropdown && <div className="custom_select_options" ref={toolRef} style={{width:'100%'}}>
                                    {tools && tools.map((tool, index) => (<div key={index}>
                                        {tool.name !== null && tool.name !== 'LlmThinkingTool' && <div className="custom_select_option"
                                                                                                       style={{padding: '12px 14px', maxWidth: '100%'}}>
                                            {tool.name}
                                        </div>}
                                    </div>))}
                                </div>}
                            </div>
                        </div>
                    </div>

                    <div style={{marginTop: '15px', display: 'flex', justifyContent: 'flex-end'}}>
                        <button style={{marginRight:'7px'}} className="secondary_button" onClick={cancelCreate}>Cancel</button>
                        <button className="primary_button" onClick={handleAddAgent}>Create and Run</button>
                    </div>
                </div>
            </div>
            <div className="col-3"></div>
        </div>
        <ToastContainer/>
    </>)
}