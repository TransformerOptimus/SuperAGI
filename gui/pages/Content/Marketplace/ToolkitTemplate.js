import React, {useEffect, useState} from 'react';
import Image from "next/image";
import styles from '.././Toolkits/Tool.module.css';
import styles3 from '../Agents/Agents.module.css';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles2 from "./Market.module.css"
import {
  checkToolkitUpdate,
  fetchToolTemplateOverview,
  installToolkitTemplate,
  updateMarketplaceToolTemplate
} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import {returnToolkitIcon} from "@/utils/utils";

export default function ToolkitTemplate({template, env}) {
  const [rightPanel, setRightPanel] = useState('tool_view')
  const [installed, setInstalled] = useState('')
  const [markdownContent, setMarkdownContent] = useState('');

  useEffect(() => {
    if(template.is_installed && !window.location.href.toLowerCase().includes('marketplace')) {
      checkToolkitUpdate(template.name).then((response) => {
        setInstalled(response.data ? 'Update' :  'Installed');
      })
          .catch((error) => {
            console.error('Error fetching update details:', error);
          });
    }
    else{
      setInstalled(window.location.href.toLowerCase().includes('marketplace') ? 'Sign in to install' : 'Install');
    }
    fetchReadme()
  }, []);

  function handleInstallClick() {
    if (window.location.href.toLowerCase().includes('marketplace')) {
      localStorage.setItem('toolkit_to_install', template.name);
      if (env === 'PROD') {
        window.open(`https://app.superagi.com/`, '_self');
      } else {
        window.location.href = '/';
      }
      return;
    }

    if(installed === "Update"){
      updateMarketplaceToolTemplate(template.name)
          .then((response) => {
            toast.success("Template Updated", {autoClose: 1800});
            setInstalled('Installed');
          })
          .catch((error) => {
            console.error('Error installing template:', error);
          });
      return;
    }

    if (template && template.is_installed) {
      toast.error("Template is already installed", {autoClose: 1800});
      return;
    }

    installToolkitTemplate(template.name)
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

  function fetchReadme() {
    if (window.location.href.toLowerCase().includes('marketplace')) {
      axios.get(`https://app.superagi.com/api/toolkits/marketplace/readme/${template.name}`)
          .then((response) => {
            setMarkdownContent(response.data || '');
            setRightPanel(response.data ? 'overview' : 'tool_view');
          })
          .catch((error) => {
            setRightPanel('tool_view');
            console.error('Error fetching template details:', error);
          });
    } else {
      fetchToolTemplateOverview(template.name)
          .then((response) => {
            setMarkdownContent(response.data || '');
            setRightPanel(response.data ? 'overview' : 'tool_view');
          })
          .catch((error) => {
            setRightPanel('tool_view');
            console.error('Error fetching template details:', error);
          });
    }
  }

  return (
    <>
      <div>
        <div className="row" style={{marginLeft: 'auto'}}>
          <div className={styles2.back_button} style={{margin: '8px 0', padding: '2px'}}
               onClick={() => handleBackClick()}>
            <Image src="/images/arrow_back.svg" alt="back_button" width={14} height={12}/>
            <span className={styles2.back_button_text}>Back</span>
          </div>
          <div className="col-3" style={{maxHeight: '84vh', overflowY: 'auto', padding: '0'}}>
            <div className={styles2.left_container}>
              <div style={{marginBottom: '15px'}}>
                <Image style={{borderRadius: '25px', background: 'black'}} width={50} height={50}
                       src={returnToolkitIcon(template.name)} alt="tool-icon"/>
              </div>
              <span className={styles2.top_heading}>{template.name}</span>
              <span style={{fontSize: '12px', marginTop: '15px',}} className={styles.tool_publisher}>By SuperAGI <Image
                width={14} height={14} src="/images/is_verified.svg"
                alt="is_verified"/>&nbsp;{'\u00B7'}&nbsp;<Image width={14} height={14}
                                                                src="/images/upload_icon.svg"
                                                                alt="upload-icon"/></span>
              <button className="primary_button" style={{
                marginTop: '15px',
                width: '100%',
                background: template && template.is_installed && installed !== 'Update' ? 'rgba(255, 255, 255, 0.14)' : '#FFF',
                color: template && template.is_installed && installed !== 'Update' ? '#FFFFFF' : '#000'
              }} onClick={() => handleInstallClick()}>
                {(template && template.is_installed && installed !== 'Update') ?
                  <Image width={14} height={14} src="/images/tick.svg" alt="tick-icon"/> :
                  <Image width={14} height={14} src="/images/upload_icon_dark.svg"
                         alt="upload-icon"/>}&nbsp;{installed}</button>
              <hr className={styles2.horizontal_line}/>
              <span className={styles2.description_text}>{template.description}</span>
              <hr className={styles2.horizontal_line}/>
              <span style={{fontSize: '12px',}} className={styles.tool_publisher}>Last updated</span>
              <span className={styles2.description_text}>{template.updated_at}</span>
            </div>
          </div>
          <div className="col-9" style={{paddingLeft: '8px'}}>
            <div>
              <div className={styles2.left_container} style={{marginBottom: '5px', padding: '8px'}}>
                <div className="row">
                  <div className="col-4">
                    {markdownContent && markdownContent !== '' &&
                      <button onClick={() => setRightPanel('overview')} className={styles2.tab_button}
                              style={rightPanel === 'overview' ? {
                                background: '#454254',
                                paddingRight: '15px'
                              } : {background: 'transparent', paddingRight: '15px'}}>
                        &nbsp;Overview
                      </button>}
                    <button onClick={() => setRightPanel('tool_view')}
                            className={styles2.tab_button} style={rightPanel === 'tool_view' ? {
                      background: '#454254',
                      paddingRight: '15px'
                    } : {background: 'transparent', paddingRight: '15px'}}>
                      &nbsp;Tools Included
                    </button>
                  </div>
                </div>
              </div>
              {rightPanel === 'overview' &&
                <div className={styles2.left_container} style={{marginBottom: '8px'}}>
                  <div className={styles2.markdown_container}>
                    {markdownContent && markdownContent !== '' ? <ReactMarkdown
                        className={styles2.markdown_style}>{markdownContent}</ReactMarkdown> :
                      <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        marginTop: '40px',
                        width: '100%'
                      }}>
                        <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions"/>
                        <span className={styles3.feed_title} style={{marginTop: '8px'}}>No Overview to display!</span>
                      </div>
                    }
                  </div>
                </div>}
              {rightPanel === 'tool_view' && <div>
                <div style={{overflowY: 'scroll', height: '70vh'}}>
                  {template.tools.map((value, index) => (
                    <div key={index} className={styles2.left_container}
                         style={{marginBottom: '5px', color: 'white', padding: '16px'}}>
                      <span className={styles2.description_text}>{value.name}</span><br/>
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