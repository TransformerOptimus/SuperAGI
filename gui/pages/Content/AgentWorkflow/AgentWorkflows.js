import React, {useState} from 'react';
import Image from "next/image";
import 'react-toastify/dist/ReactToastify.css';
import {createInternalId, getUserClick, preventDefault} from "@/utils/utils";
import styles from "@/pages/Content/Agents/Agents.module.css";
import {createAgentWorkflow, fetchAgentWorkflowDetails} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import {toast, ToastContainer} from "react-toastify";

export default function AgentWorkflows({sendWorkflowData, workflows}) {
    const [createWorkflow, setCreateWorflow] = useState(false);
    const [workflowDescription, setWorkflowDescription] = useState('');
    const [workflowName, setWorkflowName] = useState('');
    const handleAddAgentWorkflow = () => {
        createAgentWorkflow({name: workflowName, description: workflowDescription, code_yaml: ""})
            .then((response) => {
                EventBus.emit('reFetchAgentWorkflows', {});
                setCreateWorflow(false)
                toast.success('Agent Workflow successfully', {autoClose: 1800});
                // sendWorkflowData({
                //     id: response.data.id,
                //     name: workflowName,
                //     contentType: "Agent_Workflow",
                //     internalId: createInternalId()
                // });
            })
            .catch((error) => {
                console.error('Error fetching workflow details:', error);
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
                    <button className="secondary_button w_100" onClick={() => {
                       setCreateWorflow(true); getUserClick('Agent Workflow Create Clicked', {})
                    }}>
                        + Create Workflow
                    </button>
                </div>

                {workflows && workflows.length > 0 ? <div className="vertical_selection_scroll w_100">
                    {workflows.map((workflow, index) => (
                        <div key={index}>
                            <div className="agent_box w_100" onClick={() =>  sendWorkflowData({
                                id: workflow.id,
                                name: workflow.name,
                                contentType: "Agent_Workflow",
                                internalId: createInternalId()
                            })}>
                                <div className="text_ellipsis"><span className="agent_text text_ellipsis">{workflow.name}</span></div>
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
                        <textarea className="textarea_medium" rows={3} value={workflowDescription} onChange={handleWorkflowDescriptionChange}/>
                    </div>
                    <div className="display_flex_container justify_end">
                        <button className="secondary_button mr_10" onClick={() => setCreateWorflow(false)}>
                            Cancel
                        </button>
                        <button className="primary_button" onClick={() => handleAddAgentWorkflow()}>
                            Create Agent Workflow
                        </button>
                    </div>
                </div>
            </div>)}
            <ToastContainer/>
        </>
    );
}
