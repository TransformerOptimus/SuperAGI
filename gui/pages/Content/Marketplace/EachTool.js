import React, {useState} from 'react';
import Image from "next/image";
import styles from '../Tools/Tool.module.css';
import styles1 from '../Agents/Agents.module.css'
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles2 from "./Market.module.css"

export default function EachTool({}) {
    const [tools, setTools] = useState(['Gmailer','jira','openai','super agi','langchain','zapier','whatsapp'])

    return (
        <>
           <div>
               <div style={{fontWeight: '500', fontSize: '12px', color: '#888888'}}>
                   {'\u2190'} Back
               </div>
               <div className="row" style={{marginLeft:'auto'}}>
               <div className="col-3" >
                   <div className={styles2.left_container}>
                       <div style={{marginBottom:'15px'}}>
                       <Image className={styles.image_class} style={{borderRadius: '25px',}} width={50} height={50} src="/images/custom_tool.svg" alt="tool-icon"/>
                       </div>
                       <span className={styles2.top_heading}>Embedding Name</span>
                       <span style={{fontSize: '12px',marginTop: '15px',}} className={styles.tool_publisher}>By Google <Image width={14} height={14} src="/images/is_verified.svg" alt="is_verified"/>&nbsp;{'\u00B7'}&nbsp;<Image width={14} height={14} src="/images/upload_icon.svg" alt="upload-icon"/>&nbsp;247</span>
                       <button className="primary_button" style={{marginTop:'15px',width:'100%'}}><Image width={14} height={14} src="/images/upload_icon_dark.svg" alt="upload-icon"/>&nbsp;Installed</button>
                   </div>
                   <div className={styles2.left_container} style={{marginTop:'0.7%'}}>
                       <span className={styles2.description_text}>shifting timeline across multiple time strings. Regardless shifting shifting timeline across multiple time strings. Regardless shifting</span>
                       <div className={styles1.agent_info_tools} style={{marginTop:'15px'}}>
                           {tools.map((tool, index) => (<div key={index} className="tool_container" style={{marginTop:'0',marginBottom:'5px'}}>
                               <div className={styles1.tool_text}>{tool || ''}</div>
                           </div>))}
                       </div>
                   </div>
                   <div className={styles2.left_container} style={{marginTop:'0.7%'}}>
                       <span style={{fontSize: '12px',}} className={styles.tool_publisher}>Last updated</span>
                       <span className={styles2.description_text}>23 June 2023</span>
                   </div>
               </div>
               <div className="col-9">
                   <div className={styles2.left_container}>
                   <span className={styles2.description_text}>[![Join our Discord Server](https://img.shields.io/badge/Discord-SuperAGI-blueviolet?logo=discord&logoColor=white)](https://discord.gg/dXbRe5BHJC) ° [![Follow us on Twitter](https://img.shields.io/twitter/follow/_superAGI?label=_superAGI&style=social)](https://twitter.com/_superAGI) ° [![Join the discussion on Reddit](https://img.shields.io/reddit/subreddit-subscribers/Super_AGI?label=%2Fr/Super_AGI&style=social)](https://www.reddit.com/r/Super_AGI)</span>
                   <span className={styles2.description_heading}></span>
                   </div>
               </div>
               </div>
           </div>
            <ToastContainer/>
        </>
    );
}