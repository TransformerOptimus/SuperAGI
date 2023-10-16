import React, {useEffect, useState} from 'react';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/mode-yaml';
import 'ace-builds/src-noconflict/theme-twilight';
import {EventBus} from "@/utils/eventBus";
import {updateAgentWorkflow} from "@/pages/api/DashboardService";

const YamlEditor = ({ getCode, code, workflowId }) => {
    const [yamlContent, setYamlContent] = useState('');


    const handleYamlChange = (newContent) => {
        setYamlContent(newContent);
    };
    useEffect(() => {
        const sendData = () => {
            // getCode(yamlContent)
            console.log('agennefndfsd')
            updateAgentWorkflow(workflowId,  {name:"", description: "", code_yaml: yamlContent})
                .then((response) => {
                    EventBus.emit('setCode',{})
                })
                .catch((error) => {
                    console.error('Error fetching workflow details:', error);
                });
        }
        EventBus.on('sendCodeContent', sendData);
        return () => {
            EventBus.off('sendCodeContent', sendData);
        };
    });
    useEffect(() => {
       if(code){
           setYamlContent(code);
       }
    },[code]);

    // const handleYamlParse = () => {
    //     try {
    //         const parsedYaml = jsYaml.load(yamlContent);
    //         onYamlChange(parsedYaml); // Callback with parsed data
    //         alert('YAML parsed successfully.');
    //     } catch (error) {
    //         alert('Error parsing YAML: ' + error.message);
    //     }
    // };

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

        </div>
    );
};

export default YamlEditor;
