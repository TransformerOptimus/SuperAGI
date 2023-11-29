import React, {useState, useEffect, useRef} from "react";
import Image from "next/image";
import {excludedToolkits, loadingTextEffect, warningContainer} from "@/utils/utils";
import WorkflowDiagram from "@/pages/Content/AgentWorkflow/WorkflowDiagram";
import CodeEditor from "@/pages/Content/AgentWorkflow/CodeEditor";
import {EventBus} from "@/utils/eventBus";
import styles from "@/pages/Content/AgentWorkflow/AgentWorkflow.module.css";
import {fetchAgentWorkflowDetails, updateAgentWorkflow} from "@/pages/api/DashboardService";


export default function AgentWorkflowWorkspace({tools, workflowId, internalId}){
    const [isLoading, setIsLoading] = useState(true)
    const [loadingText, setLoadingText] = useState("Loading Workflows");
    const [yamlContent, setYamlContent] = useState(``);
    const [workflowDetails, setWorkflowDetails] = useState(null);
    const [buttonDisabled, setButtonDisabled] = useState(true);


    const [toolkitList, setToolkitList] = useState(tools)

    const parseYamlContent  = () => {
        EventBus.emit('sendCodeContent',{})
    }

    const getCode = (code) =>{
        setYamlContent(code)
    }

    useEffect(() => {
        loadingTextEffect('Loading Workflows', setLoadingText, 500);
        getWorkflowDetails()
    },[]);

    useEffect(() => {
        EventBus.on('setCode', getWorkflowDetails);
        return () => {
            EventBus.off('setCode', getWorkflowDetails);
        };
    }, []);

    useEffect(() => {
        console.log(workflowDetails)
    },[workflowDetails]);

    function getWorkflowDetails() {
        fetchAgentWorkflowDetails(workflowId)
            .then((response) => {
                setWorkflowDetails(response.data)
                setIsLoading(false)
                setYamlContent(response.data.agent_workflow_code)
            })
            .catch((error) => {
                console.error('Error fetching workflow details:', error);
            });
    }

    return(
        <div className="col-12 padding_5 overflowY_auto h_calc92">
            {!isLoading && workflowDetails ? <div>
          <div className="vertical_containers padding_16_8 display_flex_container justify_space_between flex_dir_row">
              <div>
                <span className="text_16">{workflowDetails?.agent_workflow_name}</span><br />
                <span className="text_12 color_gray mt_8 lh_18">{workflowDetails?.agent_workflow_description}</span>
              </div>
              <button className="primary_button" onClick={parseYamlContent} disabled={buttonDisabled}>&nbsp;Update Changes
              </button>
            </div>
          <div className="display_flex_container gap_8">
              <div className="w_50">
                  <div className={`${styles.code_block_topbar} ${"display_flex_container justify_space_between"}`}><span>Code</span>
                  </div>
                  <div className={styles.code_section}>
                      <CodeEditor internalId={internalId} getCode={getCode} code={workflowDetails?.agent_workflow_code} workflowId={workflowId} getWorkflowDetails={getWorkflowDetails} setButtonDisabled={setButtonDisabled} />
                  </div>
              </div>
              <div className={styles.diagram_content}>
                  <div className={styles.code_block_topbar}>Preview</div>
                  <div className={styles.daigram_section}>
                      {yamlContent ? <WorkflowDiagram yamlContent={yamlContent} /> : <div>{warningContainer("No preview available to display. Please type the .yaml to view the respective workflow preview here")}</div>}
                  </div>
              </div>
          </div>
            </div> :
                <div className="horizontal_container_center h_75vh">
                    <div className="signInInfo text_16 ff_sourceCode">{loadingText}</div>
                </div>}
        </div>
    )
}