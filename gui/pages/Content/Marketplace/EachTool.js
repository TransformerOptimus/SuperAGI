import React, {useEffect, useState} from 'react';
import Image from "next/image";
import styles from '../Tools/Tool.module.css';
import styles1 from '../Agents/Agents.module.css'
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles2 from "./Market.module.css"
import {installAgentTemplate,fetchToolTemplateOverview} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import axios from "axios";
import ReactMarkdown from 'react-markdown';

export default function EachTool({template}) {
    const [rightPanel, setRightPanel] = useState('overview')
    const [installed, setInstalled] = useState('')
    const [markdownContent, setMarkdownContent] = useState('');

    useEffect(() => {
        setInstalled(template && template.is_installed? 'Install' : 'Install');
        if(window.location.href.toLowerCase().includes('marketplace')) {
            setInstalled('Sign in to install')
        }
        fetchToolTemplateOverview(template.name)
            .then((response) => {
                const data = response.data || [];
                setMarkdownContent(data);
            })
            .catch((error) => {
                console.error('Error fetching template details:', error);
            });
    }, []);


    function handleInstallClick(){
        if(window.location.href.toLowerCase().includes('marketplace')) {
            if (window.location.href.toLowerCase().includes('localhost')) {
                window.location.href = '/';
            }
            else
                window.open(`https://app.superagi.com/`, '_self')
            return;
        }

        if(template && template.is_installed) {
            toast.error("Template is already installed", {autoClose: 1800});
            return;
        }

        installAgentTemplate(template.id)
            .then((response) => {
                toast.success("Template installed", {autoClose: 1800});
                setInstalled('Installed');
            })
            .catch((error) => {
                console.error('Error fetching template details:', error);
            });
    }

    function handleBackClick(){
        EventBus.emit('goToMarketplace', {});
    }

    return (
        <>
            <div>
                <div className="row" style={{marginLeft:'auto'}}>
                    <div className={styles2.back_button} style={{margin: '8px 0',padding: '2px'}} onClick={() => handleBackClick()}>
                        <Image src="/images/arrow_back.svg" alt="back_button" width={14} height={12}/>
                        <span className={styles2.back_button_text}>Back</span>
                    </div>
                    <div className="col-3" style={{maxHeight:'84vh',overflowY:'auto',padding:'0'}}>
                        <div className={styles2.left_container}>
                            <div style={{marginBottom:'15px'}}>
                                <Image style={{borderRadius: '25px',background:'black'}} width={50} height={50} src="/images/app-logo-light.png" alt="tool-icon"/>
                            </div>
                            <span className={styles2.top_heading}>{template.name}</span>
                            <span style={{fontSize: '12px',marginTop: '15px',}} className={styles.tool_publisher}>By SuperAGI <Image width={14} height={14} src="/images/is_verified.svg" alt="is_verified"/>&nbsp;{'\u00B7'}&nbsp;<Image width={14} height={14} src="/images/upload_icon.svg" alt="upload-icon"/></span>
                            <button className="primary_button" style={{marginTop:'15px',width:'100%', pointerEvents:!(window.location.href.toLowerCase().includes('marketplace')) ? 'none':'',}} onClick={() => handleInstallClick()}><Image width={14} height={14} src="/images/upload_icon_dark.svg" alt="upload-icon"/>&nbsp;{installed}
                                {!(window.location.href.toLowerCase().includes('marketplace')) && <span style={{fontWeight:'400',fontSize:'12px',color: '#888888',}}>(coming soon)</span>}
                            </button>
                            <hr className={styles2.horizontal_line} />
                            <span className={styles2.description_text}>{template.description}</span>
                            <hr className={styles2.horizontal_line} />
                            <span style={{fontSize: '12px',}} className={styles.tool_publisher}>Last updated</span>
                            <span className={styles2.description_text}>{template.updated_at}</span>
                        </div>
                    </div>
                    <div className="col-9" style={{paddingLeft: '8px'}}>
                        <div>
                            <div className={styles2.left_container} style={{marginBottom:'5px',padding:'8px'}}>
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
                            {rightPanel === 'overview' && <div className={styles2.left_container} style={{marginBottom: '8px'}}>
                                <div className={styles2.markdown_container}>
                                    <ReactMarkdown className={styles2.markdown_style}>{markdownContent}</ReactMarkdown>
                                </div>
                                {/*<div>*/}
                                {/*    <span className={styles2.description_heading} style={{fontWeight: '400'}}>{goals.length}&nbsp;Goals</span><br/><br/>*/}
                                {/*    {goals.map((goal, index) => (<div key={index} style={{marginTop: '0'}}>*/}
                                {/*        <div className={styles2.description_text}>{index + 1}. {goal || ''}</div>*/}
                                {/*        {index !== goals.length - 1}*/}
                                {/*    </div>))}*/}
                                {/*</div>*/}
                            </div>}
                            {rightPanel==='tool_view' && <div>
                                <div  style={{overflowY:'scroll',height:'70vh'}}>
                                    {template.tools.map((value, index) => (
                                        <div key={index} className={styles2.left_container} style={{marginBottom: '5px',color:'white',padding:'16px'}}>
                                            <span className={styles2.description_text}>{value.name}</span><br />
                                            <span className={styles2.sub_text}>{value.description}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>}
                        </div>
                    </div>
                </div>
            </div>
            <ToastContainer/>
        </>
    );
}