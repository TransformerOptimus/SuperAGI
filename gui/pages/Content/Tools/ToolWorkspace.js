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

    if (!tool || !tool.description) {
      tool = { ...tool, description: defaultDescription };
    }

    
    const ConfigurationSection = () => {
      const [configItems, setConfigItems] = useState([]);
    
      useEffect(() => {
        // Fetch the current key-value pairs from the API
        fetchConfigItems();
      }, []);
    
      const fetchConfigItems = async () => {
        try {
          const response = await axios.get('http://192.168.211.48:8001/tool_configs/get/toolkit/Changed ');
          setConfigItems(response.data);
        } catch (error) {
          console.error(error);
        }
      };
    
      const updateConfigItem = async (id, value) => {
        try {
          const response = await axios.put('http://192.168.211.48:8001/tool_configs/add/Changed');
          console.log(response.data); // Handle the response as per your requirement
        } catch (error) {
          console.error(error);
        }
      };
    
      const handleInputChange = (id, value) => {
        // Update the value in the local state
        const updatedConfigItems = configItems.map((item) =>
          item.id === id ? { ...item, value } : item
        );
        setConfigItems(updatedConfigItems);
      };
    
      const handleUpdateChanges = () => {
        // Send update requests for modified key-value pairs
        configItems.forEach((item) => {
          if (item.value !== null) {
            updateConfigItem(item.id, item.value);
          }
        });
      };
    
      return (
        <div>
          {/* Loop through the configItems and generate the input fields */}
          {configItems.map((configItem) => (
            <div
              key={configItem.id}
              style={{
                color: '#666666',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                marginBottom: '20px',
              }}
            >
              <div style={{ marginBottom: '6px' }}>{configItem.key}</div>
              <div className={styles.search_box}>
                <input
                  type="text"
                  placeholder="Enter here"
                  value={configItem.value || ''}
                  onChange={(e) => handleInputChange(configItem.id, e.target.value)}
                />
              </div>
            </div>
          ))}
    
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button style={{ marginRight: '7px' }} className={styles.secondary_button}>
              Cancel
            </button>
            <button className={styles.primary_button} onClick={handleUpdateChanges}>
              Update Changes
            </button>
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
            style={activeTab === 'Configuration' ? { background: '#454254', paddingRight: '15px' } : { background: 'transparent', paddingRight: '15px' }}>
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





