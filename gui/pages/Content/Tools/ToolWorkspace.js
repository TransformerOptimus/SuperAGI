import React, {useEffect, useState} from 'react';
import Image from 'next/image';
import {ToastContainer, toast} from 'react-toastify';
import {EventBus} from "@/utils/eventBus";
import {updateToolConfig, getToolConfig} from "@/pages/api/DashboardService";
import styles from './Tool.module.css';
import axios from 'axios';

export default function ToolWorkspace({tool,toolDetails}){
    const [activeTab,setActiveTab] = useState('Configuration')
    const [showDescription,setShowDescription] = useState(false)
    const [apiConfigs, setApiConfigs] = useState([]);
    const defaultDescription = "Shifting timeline accross multiple time strings. Shifting timeline accross multiple time strings.Shifting timeline accross multiple time strings.Shifting timeline accross multiple time strings.";
    const [toolsIncluded, setToolsIncluded] = useState([]);

    const handleKeyChange = (event, index) => {
      const updatedData = [...apiConfigs];
      updatedData[index].value = event.target.value;
      setApiConfigs(updatedData);
    };
    

    useEffect(() => {
      if (toolDetails && toolDetails.tools) {
        setToolsIncluded(toolDetails.tools);
      }
    }, [toolDetails]);

    if (!tool || !tool.description) {
      tool = { ...tool, description: defaultDescription };
    }

    useEffect(() => {
      if(toolDetails !== null) {
        getToolConfig(toolDetails.name)
        .then((response) => {
          const apiConfigs = response.data || [];
          setApiConfigs(apiConfigs);
        })
        .catch((error) => {
          console.log('Error fetching API data:', error);
        });
      }
    }, []);

    const handleUpdateChanges = async () => {
      const updatedConfigData = apiConfigs.map((config) => ({
        key: config.key,
        value: config.value,
      }));

      updateToolConfig(toolDetails.name, updatedConfigData)
      .then((response) => {
          console.log(response);
      })
      .catch((error) => {
        console.error('Error updating tool config:', error);
      });
    };

    return (
        <>
        <div className={styles.tools_container}>
            <div style={{display: 'flex',justifyContent:'space-between',marginBottom:'20px', width:'600px'}}>
                <div> 
                <Image src="/images/custom_tool.svg" alt="toolkit-icon" width={40} height={40}/>
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

            {activeTab === 'Configuration' && <div>
              {apiConfigs && apiConfigs.map((config, index) => (
                <div key={index}>
                  <div style={{ color: '#666666', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', marginBottom: '20px' }}>
                    <label style={{ marginBottom: '6px' }}>{config.key}</label>
                    <div className={styles.search_box}>
                      <input
                        type="text"
                        style={{ color: 'white' }}
                        value={config.value || ''}
                        onChange={(event) => handleKeyChange(event, index)}
                      />
                    </div>
                  </div>
                </div>
              ))}
      
              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button style={{marginRight:'7px'}} className={styles.secondary_button}>Cancel</button>
              <button className={styles.primary_button} onClick={handleUpdateChanges} >Update Changes</button>
              </div>
            </div>}
            {activeTab === 'Tools_Included' && <div>
            {toolsIncluded.map((tool, index) => (
            <div className={styles.tools_included}>
            <div key={index}>
                <div style={{color:'white'}}>{tool.name}</div>
                <div style={{color:'#888888'}}>{tool.description}</div>
            </div>
            </div>
            ))}   
            </div>}

        </div>
        </>
    );

}





