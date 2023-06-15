import React, {useEffect, useState} from 'react';
import Image from 'next/image';
import {ToastContainer, toast} from 'react-toastify';
import {EventBus} from "@/utils/eventBus";
import styles from './Tool.module.css';


export default function ToolWorkspace({tool}){
    const [activeTab,setActiveTab] = useState('Configuration')
    const [showDescription,setShowDescription] = useState(false)
    const defaultDescription = "Shifting timeline accross multiple time strings. Shifting timeline accross multiple time strings.Shifting timeline accross multiple time strings.Shifting timeline accross multiple time strings.";

    if (!tool || !tool.description) {
      tool = { ...tool, description: defaultDescription };
    }
    const ConfigurationSection = () => {

        return (
            <div>
            <div style={{color:' #666666',display:'flex',flexDirection: 'column', alignItems: 'flex-start',marginBottom:'20px'}}>
            <div style={{ marginBottom: '6px' }}>API Key</div>
            <div className={styles.search_box}>
            <input type="text" placeholder="Enter here" />
            </div>
            </div>
    
            <div style={{color:' #666666',display:'flex',flexDirection: 'column', alignItems: 'flex-start',marginBottom:'20px'}}>
            <div style={{ marginBottom: '6px' }}>Organization ID</div>
            <div className={styles.search_box}>
            <input type="text" placeholder="Enter here" />
            </div>
            </div>
    
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button style={{marginRight:'7px'}} className={styles.secondary_button} >Cancel</button>
            <button className={styles.primary_button} >Update Changes</button>
            </div>
            </div>
        );

      };
      
      const ToolsIncludedSection = () => {
        // Add the desired content for the "Tools Included" section
        return (
            <div className={styles.tools_included}>
                <div>Create issue</div>
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
                    <div>{tool.name}</div>
                    <div style={{marginRight:'40px'}}>
                    <div className={styles.description} style={!showDescription ? { maxHeight: '1.5em', overflow: 'hidden' } : {}}>
                    {tool.description}
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





