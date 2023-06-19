import React, {useEffect, useState} from 'react';
import Image from 'next/image';
import {ToastContainer, toast} from 'react-toastify';
import {EventBus} from "@/utils/eventBus";
import styles from './Tool.module.css';
import axios from 'axios';


export default function ToolWorkspace({tool,toolDetails}){
    const [activeTab,setActiveTab] = useState('Configuration')
    const [showDescription,setShowDescription] = useState(false)
    const defaultDescription = "Shifting timeline accross multiple time strings. Shifting timeline accross multiple time strings.Shifting timeline accross multiple time strings.Shifting timeline accross multiple time strings.";

    const [apiKeys, setApiKeys] = useState([
      {
          "key": "EMAIL_ADDRESS",
          "created_at": "2023-06-16T08:13:26.381501",
          "tool_kit_id": 266,
          "updated_at": "2023-06-16T08:13:26.381521",
          "id": 601,
          "value": null
      },
      {
          "key": "EMAIL_PASSWORD",
          "created_at": "2023-06-16T08:13:26.412588",
          "tool_kit_id": 266,
          "updated_at": "2023-06-16T08:13:26.412604",
          "id": 602,
          "value": null
      },
      {
          "key": "EMAIL_SIGNATURE",
          "created_at": "2023-06-16T08:13:26.447339",
          "tool_kit_id": 266,
          "updated_at": "2023-06-16T08:13:26.447352",
          "id": 603,
          "value": null
      },
      {
          "key": "EMAIL_DRAFT_MODE_WITH_FOLDER",
          "created_at": "2023-06-16T08:13:26.483898",
          "tool_kit_id": 266,
          "updated_at": "2023-06-16T08:13:26.483914",
          "id": 604,
          "value": null
      },
      {
          "key": "EMAIL_SMTP_HOST",
          "created_at": "2023-06-16T08:13:26.521261",
          "tool_kit_id": 266,
          "updated_at": "2023-06-16T08:13:26.521281",
          "id": 605,
          "value": null
      },
      {
          "key": "EMAIL_SMTP_PORT",
          "created_at": "2023-06-16T08:13:26.555442",
          "tool_kit_id": 266,
          "updated_at": "2023-06-16T08:13:26.555458",
          "id": 606,
          "value": null
      },
      {
          "key": "EMAIL_ATTACHMENT_BASE_PATH",
          "created_at": "2023-06-16T08:13:26.590804",
          "tool_kit_id": 266,
          "updated_at": "2023-06-16T08:13:26.590815",
          "id": 607,
          "value": null
      },
      {
          "key": "EMAIL_IMAP_SERVER",
          "created_at": "2023-06-16T08:13:26.627172",
          "tool_kit_id": 266,
          "updated_at": "2023-06-16T08:13:26.627188",
          "id": 608,
          "value": null
      }
  ]);
  
    const handleApiKeyChange = (index, event) => {
      const updatedApiKeys = [...apiKeys];
      updatedApiKeys[index].value = event.target.value;
      setApiKeys(updatedApiKeys);
    };
  

    if (!tool || !tool.description) {
      tool = { ...tool, description: defaultDescription };
    }


    const ConfigurationSection = () => {

        return (
            <div>
            {apiKeys.map((apiKey, index) => (
            <div key={apiKey.id} >
              <div style={{color:' #666666',display:'flex',flexDirection: 'column', alignItems: 'flex-start',marginBottom:'20px'}}>
              <label style={{ marginBottom: '6px' }}>API Key</label>
              <div className={styles.search_box}>
              <input type="text" placeholder="Enter here" style={{color:'white'}} value={apiKey.key || ""} onChange={(event) => handleApiKeyChange(index, event)}/>
              </div>
              </div>
              
              <div style={{color:' #666666',display:'flex',flexDirection: 'column', alignItems: 'flex-start',marginBottom:'20px'}}>
              <label style={{ marginBottom: '6px' }}>Organization ID</label>
              <div className={styles.search_box}>
              <input type="text" placeholder="Enter here" style={{color:'white'}} value={apiKey.id || ""} onChange={(event) => handleApiKeyChange(index, event)}/>
              </div>
              </div>
            </div>))}
    
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button style={{marginRight:'7px'}} className={styles.secondary_button} >Cancel</button>
            <button className={styles.primary_button} >Update Changes</button>
            </div>
            </div>
        );

      };
      
      const ToolsIncludedSection = () => {
        const [toolsIncluded, setToolsIncluded] = useState([]);
        useEffect(() => {
          if (toolDetails && toolDetails.tools) {
            setToolsIncluded(toolDetails.tools);
          }
        }, [toolDetails]);

        return (
            <div>
            {toolsIncluded.map((tool, index) => (
            <div className={styles.tools_included}>
            <div key={index}>
                <div style={{color:'white'}}>{tool.name}</div>
                <div style={{color:'#888888'}}>{tool.description}</div>
            </div>
            </div>
            ))}   
            </div>
        );
      };

    return (
        <>
        <div className={styles.tools_container}>
            <div style={{display: 'flex',justifyContent:'space-between',marginBottom:'20px', width:'600px'}}>
                <div> 
                <Image src="/images/custom_tool.svg" alt={tool.name} width={40} height={40}/>
                </div>
                <div style={{ display: 'flex', alignItems: 'center' }}>

                <div style={{ marginLeft: '15px',textAlign:'left',paddingRight:'10px' }}>
                    <div>{toolDetails.name}</div>
                    <div style={{marginRight:'40px'}}>
                    <div className={styles.description} style={!showDescription ? { maxHeight: '1.5em', overflow: 'hidden' } : {}}>
                    {toolDetails.description}
                    </div>
                    {tool.description.length > 0 && (
                    <div className={styles.show_more_button} onClick={() => setShowDescription(!showDescription)}>
                        {showDescription ? 'Show Less' : '...Show More'}
                    </div>
                    )}
                    </div>
                </div>
                </div>
                <div style={{ marginLeft: 'auto' }}>
                <button className={styles.secondary_button} >...</button>
                </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center',marginBottom:'20px' }}>
            <div className={styles.tool1_box} onClick={() => setActiveTab('Configuration')}
            style={activeTab === 'Configuration' ? { background: '#454254', paddingRight: '15px'} : { background: 'transparent', paddingRight: '15px'}}>
            <div className={styles.tab_text}>Configuration</div>
            </div>
            
            <div className={styles.tool1_box} onClick={() => setActiveTab('Tools_Included')}
            style={activeTab === 'Tools_Included' ? { background: '#454254', paddingRight: '15px' } : { background: 'transparent', paddingRight: '15px' }}>
            <div className={styles.tab_text}>Tools Included</div>
            </div>
            </div>

            {activeTab === 'Configuration' && <ConfigurationSection />}
            {activeTab === 'Tools_Included' && <ToolsIncludedSection />}

        </div>
        </>
    );

}





