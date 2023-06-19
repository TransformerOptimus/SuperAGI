import React, { useState, useEffect } from 'react';
import Image from "next/image";
import axios from 'axios';
import styles from '../Tools/Tool.module.css';
import styles1 from '../Agents/Agents.module.css'
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles2 from "./Market.module.css"
import EachToolOverview from "./EachToolOverview"

export default function EachTool({ handleToolClick }) {
    const [tools, setTools] = useState(['Gmailer','jira','openai','super agi','langchain','zapier','whatsapp'])
    const [rightPanel, setRightPanel] = useState('overview')
    const [eachtoolData, setEachToolData] = useState(null);
    const [toolsIncluded, setToolsIncluded] = useState([]);


    const handleBackClick = () => {
        handleToolClick(false); // Notify the parent component (Market) to go back to the marketplace
    };

    useEffect(() => {
        const fetchToolsIncluded = async () => {
          try {
            const response = await axios.get('http://192.168.211.48:8001/tool_kits/get/list?page=0'); 
            setToolsIncluded(response.data[0]?.tools || []); 
          } catch (error) {
            console.error('Error fetching tools included:', error);
          }
        };
    
        fetchToolsIncluded();
      }, []);

    useEffect(() => {
        const fetchData = async () => {
          try {
            const response = await axios.get('http://192.168.211.48:8001/tool_kits/get?search_str=details&tool_kit_name=Changed'); 
            setEachToolData(response.data); // Assuming the response data is an object containing the tool information
          } catch (error) {
            console.error('Error fetching tool data:', error);
          }
        };
      
        fetchData();
      }, []);
      
      const toolCodeLinkName = eachtoolData && eachtoolData.tool_code_link.split('/')[3];
    return (
        <>
           <div>
               <div className="row" style={{marginLeft:'auto'}}>
                   <div className={styles2.back_button} onClick={handleBackClick}>
                       {'\u2190'} Back
                   </div>
               <div className="col-3" >
                   <div className={styles2.left_container}>
                       <div style={{marginBottom:'15px'}}>
                       <Image className={styles.image_class} style={{borderRadius: '25px',}} width={50} height={50} src="/images/custom_tool.svg" alt="tool-icon"/>
                       </div>
                       <span className={styles2.top_heading}>{eachtoolData && eachtoolData.name}</span>
                       <span style={{fontSize: '12px',marginTop: '15px',}} className={styles.tool_publisher}>By {toolCodeLinkName} <Image width={14} height={14} src="/images/is_verified.svg" alt="is_verified"/>&nbsp;{'\u00B7'}&nbsp;<Image width={14} height={14} src="/images/upload_icon.svg" alt="upload-icon"/>&nbsp;247</span>
                       {/*<button className="primary_button" style={{marginTop:'15px',width:'100%'}}><Image width={14} height={14} src="/images/upload_icon_dark.svg" alt="upload-icon"/>&nbsp;Installed</button>*/}
                   </div>
                   {/*<div className={styles2.left_container} style={{marginTop:'0.7%'}}>
                       <span className={styles2.description_text}>{eachtoolData && eachtoolData.description}</span>
                       <div className={styles1.agent_info_tools} style={{marginTop:'15px'}}>
                           {tools.map((tool, index) => (<div key={index} className="tool_container" style={{marginTop:'0',marginBottom:'5px'}}>
                               <div className={styles1.tool_text}>{tool || ''}</div>
                           </div>))}
                       </div>
                    </div>*/}
                   <div className={styles2.left_container} style={{marginTop:'0.7%'}}>
                       <span style={{fontSize: '12px',}} className={styles.tool_publisher}>Last updated</span>
                       <span className={styles2.description_text}>{eachtoolData && eachtoolData.updated_at}</span>
                   </div>
               </div>
               <div className="col-9">
                   <div className={styles2.left_container} style={{marginBottom:'5px'}}>
                       <div className="row">
                           <div className="col-4">
                              <button onClick={() => setRightPanel('overview')} className={styles2.tab_button} style={rightPanel === 'overview' ? {background:'#454254',paddingRight:'15px'} : {background:'transparent',paddingRight:'15px'}}>
                                  &nbsp;Overview
                              </button>
                              <button onClick={() => setRightPanel('tool_view')} className={styles2.tab_button} style={rightPanel === 'tool_view' ? {background:'#454254',paddingRight:'15px'} : {background:'transparent',paddingRight:'15px'}}>
                                  &nbsp;Tools Included
                              </button>
                           </div>
                       </div>
                   </div>
                   {rightPanel==='overview' && <div>
                       <EachToolOverview />
                   </div>}
                   {rightPanel==='tool_view' && <div>
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
                   </div>}
               </div>
               </div>
           </div>
            <ToastContainer/>
        </>
    );
}