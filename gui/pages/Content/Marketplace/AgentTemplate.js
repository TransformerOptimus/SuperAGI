import React, {useEffect, useState} from 'react';
import Image from "next/image";
import styles from '.././Toolkits/Tool.module.css';
import styles1 from '../Agents/Agents.module.css'
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles2 from "./Market.module.css"
import {fetchAgentTemplateConfig, installAgentTemplate} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import axios from 'axios';
import {loadingTextEffect} from "@/utils/utils";

export default function AgentTemplate({template, env}) {
  const [tools, setTools] = useState([])
  const [agentWorkflow, setAgentWorkflow] = useState('')
  const [templateModel, setTemplateModel] = useState('')
  const [rightPanel, setRightPanel] = useState('overview')
  const [goals, setGoals] = useState([])
  const [instructions, setInstructions] = useState([])
  const [installed, setInstalled] = useState('')
  const [constraints, setConstraints] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [loadingText, setLoadingText] = useState("Loading Template Details")
  const [isInstalled, setIsInstalled] = useState(false)

  useEffect(() => {
    loadingTextEffect('Loading Template Details', setLoadingText, 500);
    if (window.location.href.toLowerCase().includes('marketplace')) {
      setInstalled('Sign in to install')
      axios.get(`https://app.superagi.com/api/agent_templates/marketplace/template_details/${template.id}`)
        .then((response) => {
          const data = response.data || [];
          setValues(data)
        })
        .catch((error) => {
          console.error('Error fetching agent templates:', error);
        });
    } else {
      setInstalled(template && template.is_installed ? 'Installed' : 'Install');
      fetchAgentTemplateConfig(template.id)
        .then((response) => {
          const data = response.data || [];
          setValues(data)
        })
        .catch((error) => {
          console.error('Error fetching template details:', error);
        });
    }
  }, []);

  function setValues(data) {
    setAgentWorkflow(data.agent_workflow_name)
    setTemplateModel(data.configs.model.value)
    setGoals(data.configs.goal.value)
    setConstraints(data.configs.constraints.value)
    setTools(data.configs.tools.value)
    setInstructions(data.configs.instruction ? data.configs.instruction.value : null);
    setIsLoading(false)
  }

  function handleInstallClick() {
    setIsInstalled(true)
    if (window.location.href.toLowerCase().includes('marketplace')) {
      localStorage.setItem('agent_to_install', template.id);
      if (env === 'PROD') {
        window.open(`https://app.superagi.com/`, '_self');
      } else {
        window.location.href = '/';
      }
      return;
    }

    if (template && template.is_installed) {
      toast.error("Template is already installed", {autoClose: 1800});
      return;
    }

    installAgentTemplate(template.id)
      .then((response) => {
        toast.success("Template installed", {autoClose: 1800});
        setInstalled('Installed');
      })
      .catch((error) => {
        console.error('Error installing template:', error);
      });
  }

  function handleBackClick() {
    EventBus.emit('goToMarketplace', {});
  }

  return (
    <>
      <div>
        {!isLoading ? <div className="row" style={{marginLeft: 'auto'}}>
          <div className={styles2.back_button} style={{margin: '8px 0', padding: '2px'}}
               onClick={() => handleBackClick()}>
            <Image src="/images/arrow_back.svg" alt="back_button" width={14} height={12}/>
            <span className={styles2.back_button_text}>Back</span>
          </div>
          <div className="col-3" style={{maxHeight: '84vh', overflowY: 'auto', padding: '0'}}>
            <div className={styles2.left_container}>
              <span className={styles2.top_heading}>{template.name}</span>
              <span style={{fontSize: '12px', marginTop: '15px',}} className={styles.tool_publisher}>By SuperAGI <Image
                width={14} height={14} src="/images/is_verified.svg" alt="is_verified"/>&nbsp;{'\u00B7'}&nbsp;<Image
                width={14} height={14} src="/images/upload_icon.svg" alt="upload-icon"/></span>
              {isInstalled || (template && template.is_installed) ? (
                  <button
                      className="primary_button"
                      style={{
                        marginTop: '15px',
                        width: '100%',
                        background: 'rgba(255, 255, 255, 0.14)',
                        color: '#FFFFFF'
                      }}
                  >
                    <Image width={14} height={14} src="/images/tick.svg" alt="tick-icon"/>&nbsp; Installed
                  </button>
              ) : (
                  <button
                      className="primary_button"
                      style={{
                        marginTop: '15px',
                        width: '100%',
                        background: '#FFF',
                        color: '#000'
                      }}
                      onClick={() => handleInstallClick()}
                  >
                    <Image width={14} height={14} src="/images/upload_icon_dark.svg" alt="upload-icon"/>&nbsp; Install
                  </button>
              )}

              <hr className={styles2.horizontal_line}/>

              <span className={styles2.description_text}>{template.description}</span>

              <hr className={styles2.horizontal_line}/>

              <span style={{fontSize: '12px',}} className={styles.tool_publisher}>Tools</span>
              <div className={styles1.agent_info_tools} style={{marginTop: '10px'}}>
                {tools.map((tool, index) => (
                  <div key={index} className="tool_container" style={{marginTop: '0', marginBottom: '5px'}}>
                    <div className={styles1.tool_text}>{tool || ''}</div>
                  </div>))}
              </div>
              <br/>
              <span style={{fontSize: '12px'}} className={styles.tool_publisher}>Agent Workflow</span>
              <div className="tool_container" style={{marginTop: '10px', width: 'fit-content'}}>
                <div className={styles1.tool_text}>{agentWorkflow}</div>
              </div>
              <br/>
              <span style={{fontSize: '12px'}} className={styles.tool_publisher}>Model(s)</span>
              <div className="tool_container" style={{marginTop: '10px', width: 'fit-content'}}>
                <div className={styles1.tool_text}>{templateModel}</div>
              </div>

              <hr className={styles2.horizontal_line}/>

              <span style={{fontSize: '12px',}} className={styles.tool_publisher}>Last updated</span>
              <span className={styles2.description_text}>{template.updated_at}</span>
            </div>
          </div>
          <div className="col-9" style={{paddingLeft: '8px'}}>
            {/*<div className={styles2.left_container} style={{marginBottom:'5px'}}>*/}
            {/*    <div className="row">*/}
            {/*        <div className="col-4">*/}
            {/*            <button onClick={() => setRightPanel('overview')} className={styles2.tab_button} style={rightPanel === 'overview' ? {background:'#454254',paddingRight:'15px'} : {background:'transparent',paddingRight:'15px'}}>*/}
            {/*                &nbsp;Overview*/}
            {/*            </button>*/}
            {/*            <button onClick={() => setRightPanel('tool_view')} className={styles2.tab_button} style={rightPanel === 'tool_view' ? {background:'#454254',paddingRight:'15px'} : {background:'transparent',paddingRight:'15px'}}>*/}
            {/*                &nbsp;Toolkits Included*/}
            {/*            </button>*/}
            {/*        </div>*/}
            {/*    </div>*/}
            {/*</div>*/}
            <div style={{maxHeight: '84vh', overflowY: 'auto'}}>
              <div className={styles2.left_container} style={{marginBottom: '8px'}}>
                <div>
                  <span className={styles2.description_heading}
                        style={{fontWeight: '400'}}>{goals.length}&nbsp;Goals</span><br/><br/>
                  {goals.map((goal, index) => (<div key={index} style={{marginTop: '0'}}>
                    <div className={styles2.description_text}>{index + 1}. {goal || ''}</div>
                    {index !== goals.length - 1}
                  </div>))}
                </div>
              </div>
              {instructions && instructions.length > 0 &&
                <div className={styles2.left_container} style={{marginBottom: '8px'}}>
                  <div>
                    <span className={styles2.description_heading}
                          style={{fontWeight: '400'}}>{instructions.length} Instructions</span><br/><br/>
                    {instructions.map((instruction, index) => (
                      <div key={index} style={{marginTop: '0'}}>
                        <div className={styles2.description_text}>{index + 1}. {instruction || ''}</div>
                      </div>))}
                  </div>
                </div>}
              <div className={styles2.left_container} style={{marginBottom: '8px'}}>
                <div>
                  <span className={styles2.description_heading}
                        style={{fontWeight: '400'}}>{constraints.length}&nbsp;Constraints</span><br/><br/>
                  {constraints.map((goal, index) => (<div key={index} style={{marginTop: '0'}}>
                    <div className={styles2.description_text}>{index + 1}. {goal || ''}</div>
                    {index !== constraints.length - 1}
                  </div>))}
                </div>
              </div>
            </div>
          </div>
        </div> : <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '75vh'}}>
          <div className="signInInfo" style={{fontSize: '16px', fontFamily: 'Source Code Pro'}}>{loadingText}</div>
        </div>}
      </div>
      <ToastContainer/>
    </>
  );
}