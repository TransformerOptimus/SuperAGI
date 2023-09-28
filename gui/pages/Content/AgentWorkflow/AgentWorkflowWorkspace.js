import React, {useState, useEffect, useRef} from "react";
import Image from "next/image";
import {excludedToolkits, loadingTextEffect} from "@/utils/utils";
import WorkflowDiagram from "@/pages/Content/AgentWorkflow/WorkflowDiagram";
import CodeEditor from "@/pages/Content/AgentWorkflow/CodeEditor";
import {EventBus} from "@/utils/eventBus";
import styles from "@/pages/Content/Agents/Agents.module.css";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";




export default function AgentWorkflowWorkspace({tools, modelName}){
    const [modelDetails, setModelDetails] = useState([])
    const [selectedOption, setSelectedOption] = useState('metrics')
    const [isLoading, setIsLoading] = useState(true)
    const [loadingText, setLoadingText] = useState("Loading Models");
    const [yamlContent, setYamlContent] = useState(``);
    const [timeDropdown, setTimeDropdown] = useState(false);
    const toolkitRef = useRef(null);
    const [toolkitDropdown, setToolkitDropdown] = useState(false);
    // const timeRef = useRef(null);
    const timeUnit =''
    const [selectedTools, setSelectedTools] = useState([]);

    const [toolkitList, setToolkitList] = useState(tools)

    const [isToggled, setIsToggled] = useState(false);

    const handleToggle = () => {
        setIsToggled(!isToggled);
    };

    const parseYamlContent  = () => {
        EventBus.emit('sendCodeContent', {});
    }

    const getCode = (code) =>{
        console.log(code)
        setYamlContent(code)
    }


    return(
        <div id="model_details" className="col-12 padding_5 overflowY_auto h_calc92">
          <div className="vertical_containers padding_16_8" style={{display: 'flex',
              flexDirection: 'row',
              justifyContent: 'space-between',}}>
              <div>
                <span className="text_16">Workflow Name</span><br />
                <span className="text_12 color_gray mt_8 lh_18">Testing Workflow</span>
              </div>
              <button className="primary_button" onClick={parseYamlContent}>&nbsp;Update Changes
              </button>
            </div>
          <div className="display_flex_container gap_8">
              <div style={{width : '50%'}}>
                  <div style={{    background: '#2E294B',
                      color: 'white',
                      fontSize: '14px',
                      padding:'8px',
                      height:'4.5vh', borderTopLeftRadius: '8px', borderTopRightRadius: '8px'
                  }}><span>Code</span>
                      <div style={{marginTop: '15px'}}>
                          <label className={styles.form_label}>Agent Workflow</label><br/>
                          <div className="dropdown_container_search" style={{width: '100%'}}>
                              <div className={`${"custom_select_container"}`} onClick={() => {setToolDropdown(!edit ? !toolDropdown : false)}}
                                   style={{width: '100%'}}>
                                  Select Tool<Image width={20} height={21}
                                                        src={!toolDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'}
                                                        alt="expand-icon"/>
                              </div>
                              {toolkitDropdown && <div className="custom_select_options" ref={toolkitRef} style={{width: '100%'}}>
                                  {toolkitList && toolkitList.map((toolkit, index) => (
                                      <div key={index}>
                                          {toolkit.name !== null && !excludedToolkits().includes(toolkit.name) && <div>
                                              <div onClick={() => addToolkit(toolkit)} className="custom_select_option" style={{
                                                  padding: '10px 14px',
                                                  maxWidth: '100%',
                                                  display: 'flex',
                                                  alignItems: 'center',
                                                  justifyContent: 'space-between'
                                              }}>
                                                  <div style={{display: 'flex', alignItems: 'center', justifyContent: 'flex-start'}}>
                                                      <div onClick={(e) => toggleToolkit(e, toolkit.id)}
                                                           style={{marginLeft: '-8px', marginRight: '8px'}}>
                                                          <Image src={toolkit.isOpen ? "/images/arrow_down.svg" : "/images/arrow_forward.svg"}
                                                                 width={11} height={11} alt="expand-arrow"/>
                                                      </div>
                                                      <div style={{width: '100%'}}>{toolkit.name}</div>
                                                  </div>
                                                  {checkSelectedToolkit(toolkit) && <div style={{order: '1', marginLeft: '10px'}}>
                                                      <Image src="/images/tick.svg" width={17} height={17} alt="selected-toolkit"/>
                                                  </div>}
                                              </div>
                                              {toolkit.isOpen && toolkit.tools.map((tool, index) => (
                                                  <div key={index} className="custom_select_option" onClick={() => addTool(tool)} style={{
                                                      padding: '10px 14px 10px 40px',
                                                      maxWidth: '100%',
                                                      display: 'flex',
                                                      alignItems: 'center',
                                                      justifyContent: 'space-between'
                                                  }}>
                                                      <div>{tool.name}</div>
                                                      {(selectedTools.includes(tool.id) || toolNames.includes(tool.name)) &&
                                                          <div style={{order: '1', marginLeft: '10px'}}>
                                                              <Image src="/images/tick.svg" width={17} height={17} alt="selected-tool"/>
                                                          </div>}
                                                  </div>))}
                                          </div>}
                                      </div>))}
                              </div>}
                          </div>
                      </div>
                  </div>
                  <div style={{backgroundImage :"url('/images/workflow_background.svg')",height:'71.5vh',}}>
                      <CodeEditor getCode={getCode} />
                  </div>
              </div>
              <div style={ {paddingLeft:'0',paddingRight:'0', height:'76vh', width:'50%'}}>
                  <div style={{    background: '#2E294B',
                      color: 'white',
                      fontSize: '14px',
                      padding:'8px',
                      height:'4.5vh',
                      borderTopLeftRadius: '8px', borderTopRightRadius: '8px'
                  }}>Preview</div>
                  <div style={{backgroundImage :"url('/images/workflow_background.svg')",height:'71.5vh', borderBottomLeftRadius: '8px', borderBottomRightRadius: '8px'}}>
                      {yamlContent &&
                          <WorkflowDiagram yamlContent={yamlContent} />}
                  </div>
              </div>
          </div>
        </div>
    )
}