import React, {useState, useEffect, useRef} from "react";
import Image from "next/image";
import {excludedToolkits, loadingTextEffect} from "@/utils/utils";
import WorkflowDiagram from "@/pages/Content/AgentWorkflow/WorkflowDiagram";
import CodeEditor from "@/pages/Content/AgentWorkflow/CodeEditor";
import {EventBus} from "@/utils/eventBus";
import styles from "@/pages/Content/AgentWorkflow/AgentWorkflow.module.css";
import {fetchAgentWorkflowDetails, updateAgentWorkflow} from "@/pages/api/DashboardService";


export default function AgentWorkflowWorkspace({tools, workflowId}){
    const [isLoading, setIsLoading] = useState(true)
    const [loadingText, setLoadingText] = useState("Loading Workflows");
    const [yamlContent, setYamlContent] = useState(``);
    const toolkitRef = useRef(null);
    const [toolDropdown, setToolDropdown] = useState(false);
    const codeEditorRef = useRef(null);
    const [selectedTools, setSelectedTools] = useState([]);
    const [workflowDetails, setWorkflowDetails] = useState(null);


    const [toolkitList, setToolkitList] = useState(tools)

    const parseYamlContent  = () => {
        console.log(yamlContent)
        EventBus.emit('sendCodeContent',{})
        // updateAgentWorkflow(workflowId,  {name:"", description: "", code_yaml: yamlContent})
        //     .then((response) => {
        //         EventBus.emit('sendCodeContent',{});
        //     })
        //     .catch((error) => {
        //         console.error('Error fetching workflow details:', error);
        //     });
    }

    const getCode = (code) =>{
        console.log(code)
        setYamlContent(code)
    }
    const toggleToolkit = (e, id) => {
        e.stopPropagation();
        const toolkitToUpdate = toolkitList.find(toolkit => toolkit.id === id);
        if (toolkitToUpdate) {
            const newOpenValue = !toolkitToUpdate.isOpen;
            setToolkitOpen(id, newOpenValue);
        }
    };

    const setToolkitOpen = (id, isOpen) => {
        const updatedToolkits = toolkitList.map(toolkit =>
            toolkit.id === id ? {...toolkit, isOpen: isOpen} : {...toolkit, isOpen: false}
        );
        setToolkitList(updatedToolkits);
    };

    const handleToolClick = (toolName) => {

    };

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
                setYamlContent(response.data.code_yaml)
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
              <button className="primary_button" onClick={parseYamlContent}>&nbsp;Update Changes
              </button>
            </div>
          <div className="display_flex_container gap_8">
              <div className="w_50">
                  <div className={`${styles.code_block_topbar} ${"display_flex_container justify_space_between"}`}><span>Code</span>
                      <div className={styles.dropdown_placement}>
                          <div className="dropdown_container_search w_100">
                              <div className={`${"custom_select_container"} ${'w_100'}`} onClick={() => {setToolDropdown(!toolDropdown)}}>
                                  Select Tool<Image width={20} height={21}
                                                        src={!toolDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'}
                                                        alt="expand-icon"/>
                              </div>
                              {toolDropdown && <div className="custom_select_options" ref={toolkitRef} style={{marginLeft: '-135px'}}>
                                  {toolkitList && toolkitList.map((toolkit, index) => (
                                      <div key={index}>
                                          {toolkit.name !== null && !excludedToolkits().includes(toolkit.name) && <div>
                                              <div className={`${'custom_select_option mxw_100 display_flex_container justify_space_between align_center '}`} style={{padding: '10px 14px',}}>
                                                  <div className="display_flex_container align_center justify_start">
                                                      <div className="ml_8 mr_8" onClick={(e) => toggleToolkit(e, toolkit.id)}>
                                                          <Image src={toolkit.isOpen ? "/images/arrow_down.svg" : "/images/arrow_forward.svg"}
                                                                 width={11} height={11} alt="expand-arrow"/>
                                                      </div>
                                                      <div className="w_100">{toolkit.name}</div>
                                                  </div>
                                              </div>
                                              {toolkit.isOpen && toolkit.tools.map((tool, index) => (
                                                  <div key={index} className="custom_select_option mxw_100 display_flex_container align_center justify_space_between" onClick={handleToolClick(tool.name)} style={{padding: '10px 14px 10px 40px'}}>
                                                      <div>{tool.name}</div>
                                                  </div>))}
                                          </div>}
                                      </div>))}
                              </div>}
                          </div>
                      </div>
                  </div>
                  <div style={{backgroundImage :"url('/images/workflow_background.svg')",height:'71.5vh'}}>
                      <CodeEditor getCode={getCode} code={workflowDetails?.agent_workflow_code} workflowId={workflowId} />
                  </div>
              </div>
              <div className={styles.diagram_content}>
                  <div className={styles.code_block_topbar}>Preview</div>
                  <div style={{backgroundImage :"url('/images/workflow_background.svg')",height:'71.5vh', borderBottomLeftRadius: '8px', borderBottomRightRadius: '8px',overflowX:'scroll', padding:'16px'}}>
                      {yamlContent &&<WorkflowDiagram yamlContent={yamlContent} />}
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