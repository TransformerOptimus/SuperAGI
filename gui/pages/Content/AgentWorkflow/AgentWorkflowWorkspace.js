import React, {useState, useEffect} from "react";
import Image from "next/image";
import {loadingTextEffect} from "@/utils/utils";
import WorkflowDiagram from "@/pages/Content/AgentWorkflow/WorkflowDiagram";
import CodeEditor from "@/pages/Content/AgentWorkflow/CodeEditor";
import {EventBus} from "@/utils/eventBus";


export default function AgentWorkflowWorkspace({modelId, modelName}){
    const [modelDetails, setModelDetails] = useState([])
    const [selectedOption, setSelectedOption] = useState('metrics')
    const [isLoading, setIsLoading] = useState(true)
    const [loadingText, setLoadingText] = useState("Loading Models");
    const [yamlContent, setYamlContent] = useState(``);


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
          <div className="row">
              <div className="col-6">
                  <div style={{    background: '#2E294B',
                      color: 'white',
                      fontSize: '14px',
                      padding:'8px',
                      height:'4.5vh', borderTopLeftRadius: '8px', borderTopRightRadius: '8px'
                  }}>Code</div>
                  <div style={{backgroundImage :"url('/images/workflow_background.svg')",height:'71.5vh',}}>
                      <CodeEditor getCode={getCode} />
                  </div>
              </div>
              <div className="col-6" style={ {paddingLeft:'0',paddingRight:'0', height:'76vh',}}>
                  <div style={{    background: '#2E294B',
                      color: 'white',
                      fontSize: '14px',
                      padding:'8px',
                      height:'4.5vh',
                      borderTopLeftRadius: '8px', borderTopRightRadius: '8px'
                  }}>Preview</div>
                  <div style={{backgroundImage :"url('/images/workflow_background.svg')",height:'71.5vh', borderBottomLeftRadius: '8px', borderBottomRightRadius: '8px'}}>
                      {yamlContent && <WorkflowDiagram yamlContent={yamlContent} />}
                  </div></div>
          </div>
        </div>
    )
}