import React, {useEffect, useState} from 'react';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/mode-yaml';
import 'ace-builds/src-noconflict/theme-twilight';
import {EventBus} from "@/utils/eventBus";
import {updateAgentWorkflow} from "@/pages/api/DashboardService";
import {setLocalStorageValue} from "@/utils/utils";
import {toast, ToastContainer} from "react-toastify";

const YamlEditor = ({internalId, getCode, code, workflowId, getWorkflowDetails, setButtonDisabled }) => {
    const [yamlContent, setYamlContent] = useState('');


    const handleYamlChange = (newContent) => {
        setYamlContent(newContent);
        setLocalStorageValue("agent_workflow_code_" + String(internalId), newContent, setYamlContent);
        setButtonDisabled(false)
    };
    useEffect(() => {
        const sendData = () => {
            // getCode(yamlContent)
            updateAgentWorkflow(workflowId,  {name:"", description: "", code_yaml: yamlContent})
                .then((response) => {
                    getWorkflowDetails();
                })
                .catch((error) => {
                    toast.error('Enter Valid .yaml code', {autoClose: 1800});
                });
        }
        EventBus.on('sendCodeContent', sendData);
        return () => {
            EventBus.off('sendCodeContent', sendData);
        };
    });
    useEffect(() => {
       if(code){
           setLocalStorageValue("agent_workflow_code_" + String(internalId), code, setYamlContent);
       }
    },[code]);

    useEffect(() => {
        if(localStorage.getItem("agent_workflow_code_" + String(internalId))){
            setYamlContent(localStorage.getItem("agent_workflow_code_" + String(internalId)))
        }
    },[]);

    return (
        <div>
            <AceEditor
                mode="yaml"
                theme="twilight"
                value={yamlContent}
                onChange={handleYamlChange}
                name="yaml-editor"
                editorProps={{ $blockScrolling: true, }}
                width="100%"
                height="71.5vh"
                setOptions={{
                    enableBasicAutocompletion: true,
                    enableLiveAutocompletion: true,
                    wrapEnabled: true,
                }}
                style={{
                    borderBottomLeftRadius: '8px',
                    borderBottomRightRadius: '8px',
                }}

            />
            <ToastContainer/>
        </div>
    );
};

export default YamlEditor;
