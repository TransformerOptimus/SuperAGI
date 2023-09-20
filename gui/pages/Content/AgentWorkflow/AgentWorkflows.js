import React, {useState} from 'react';
import Image from "next/image";
import 'react-toastify/dist/ReactToastify.css';
import {createInternalId, getUserClick, preventDefault} from "@/utils/utils";
import styles from "@/pages/Content/Agents/Agents.module.css";

export default function AgentWorkflows({sendWorkflowData}) {
    const [createWorkflow, setCreateWorflow] = useState(false);
    const [workflowDescription, setWorkflowDescription] = useState('');
    const [workflowName, setWorkflowName] = useState('');
    const agents = [{name: 'Naman'}, {name: 'Naman2'}]
    const handleAddAgentWorkflow = () => {
        sendWorkflowData({
            id: -10,
            name: workflowName,
            contentType: "Agent_Workflow",
            internalId: createInternalId()
        });
    }
    const handleWorkflowNameChange = (event) => {
        setWorkflowName(event.target.value);
    }

    const handleWorkflowDescriptionChange = (event) => {
        setWorkflowDescription(event.target.value);
    }

    return (<>
            <div className="container">
                <p className="text_14 mt_8 mb_12 ml_8">Agent Workflows</p>
                <div className="w_100 mb_10">
                    <button className="secondary_button w_100" style={{fontSize: '13px'}} onClick={() => {
                       setCreateWorflow(true); getUserClick('Agent Workflow Create Clicked', {})
                    }}>
                        + Create Workflow
                    </button>
                </div>

                {agents && agents.length > 0 ? <div className="vertical_selection_scroll w_100">
                    {agents.map((agent, index) => (
                        <div key={index}>
                            <div className="agent_box w_100" onClick={() =>  sendWorkflowData({
                                id: -14342424,
                                name: workflowName,
                                contentType: "Agent_Workflow",
                                internalId: createInternalId()
                            })}>
                                <div className="text_ellipsis"><span className="agent_text text_ellipsis">{agent.name}</span></div>
                            </div>
                        </div>
                    ))}
                </div> : <div className="form_label mt_20 horizontal_container justify_center">No Agents found</div>}
            </div>

            {createWorkflow && (<div className="modal" onClick={() => setCreateWorflow(false)}>
                <div className="modal-content" style={{width: '502px', padding: '16px', gap: '24px'}} onClick={preventDefault}>
                    <div className={styles.detail_name}>Create Agent Workflow</div>
                    <div>
                        <label className={styles.form_label}>Name</label>
                        <input className="input_medium" type="text" value={workflowName} onChange={handleWorkflowNameChange}/>
                    </div>
                    <div>
                        <label className={styles.form_label}>Description</label>
                        <input className="input_medium" type="text" value={workflowDescription} onChange={handleWorkflowDescriptionChange}/>
                    </div>
                    <div style={{display: 'flex', justifyContent: 'flex-end'}}>
                        <button className="secondary_button" style={{marginRight: '10px'}} onClick={() => setCreateWorflow(false)}>
                            Cancel
                        </button>
                        <button className="primary_button" onClick={() => handleAddAgentWorkflow()}>
                            Create Agent Workflow
                        </button>
                    </div>
                </div>
            </div>)}
        </>
    );
}
