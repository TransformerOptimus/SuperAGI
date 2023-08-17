import React, {useEffect, useRef, useState} from 'react';
import Image from "next/image";
import styles from '.././Toolkits/Tool.module.css';
import styles1 from '../Agents/Agents.module.css';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles2 from "./Market.module.css"
import styles3 from "../Knowledge/Knowledge.module.css"
import {EventBus} from "@/utils/eventBus";
import axios from 'axios';
import {
  deleteMarketplaceKnowledge,
  fetchKnowledgeTemplateOverview,
  getValidMarketplaceIndices,
  installKnowledgeTemplate
} from "@/pages/api/DashboardService";
import {loadingTextEffect} from "@/utils/utils";

export default function KnowledgeTemplate({template, env}) {
  const [installed, setInstalled] = useState('');
  const [dropdown, setDropdown] = useState(false);
  const [templateData, setTemplateData] = useState([]);
  const [markdownContent, setMarkdownContent] = useState('');
  const indexRef = useRef(null);
  const [indexDropdown, setIndexDropdown] = useState(false);
  const [pinconeIndices, setPineconeIndices] = useState([]);
  const [qdrantIndices, setQdrantIndices] = useState([]);
  const [weaviateIndices, setWeaviateIndices] = useState([]);

  useEffect(() => {
    getValidMarketplaceIndices(template.name)
      .then((response) => {
        const data = response.data || [];
        if (data) {
          setPineconeIndices(data.pinecone || []);
          setQdrantIndices(data.qdrant || []);
          setWeaviateIndices(data.weaviate || [])
        }
      })
      .catch((error) => {
        console.error('Error fetching indices:', error);
      });
  }, []);

  useEffect(() => {
    function handleClickOutside(event) {
      if (indexRef.current && !indexRef.current.contains(event.target)) {
        setIndexDropdown(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    if (template) {
      setInstalled(template.is_installed ? 'Installed' : 'Install');
    }

    if (window.location.href.toLowerCase().includes('marketplace')) {
      setInstalled('Sign in to install');
      axios.get(`https://app.superagi.com/api/knowledges/marketplace/get/details/${template.name}`)
        .then((response) => {
          const data = response.data || [];
          setTemplateData(data);
          if (data) {
            setMarkdownContent(data.readme);
          }
        })
        .catch((error) => {
          console.error('Error fetching template details:', error);
        });
    } else {
      fetchKnowledgeTemplateOverview(template.name)
        .then((response) => {
          const data = response.data || [];
          setTemplateData(data);
          if (data) {
            setMarkdownContent(data.readme);
          }
        })
        .catch((error) => {
          console.error('Error fetching template details:', error);
        });
    }
  }, []);

  const handleInstallClick = (indexId) => {
    setInstalled("Installing");

    if (window.location.href.toLowerCase().includes('marketplace')) {
      localStorage.setItem('knowledge_to_install', template.name);
      localStorage.setItem('knowledge_index_to_install', indexId);

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

    setIndexDropdown(false);

    installKnowledgeTemplate(template.name, indexId)
      .then((response) => {
          toast.success("Knowledge installed", {autoClose: 1800});
          setInstalled('Installed');
          EventBus.emit('reFetchKnowledge', {});
      })
      .catch((error) => {
        toast.error("Error installing Knowledge: ", {autoClose: 1800});
        console.error('Error installing Knowledge:', error);
        setInstalled('Install');
      });
  }

  function handleBackClick() {
    EventBus.emit('goToMarketplace', {});
  }

  const uninstallKnowledge = () => {
    deleteMarketplaceKnowledge(template.name)
      .then((response) => {
        console.log(response)
        toast.success("Knowledge uninstalled successfully", {autoClose: 1800});
        handleBackClick()
      })
      .catch((error) => {
        toast.error("Unable to uninstall knowledge", {autoClose: 1800});
        console.error('Error uninstalling knowledge:', error);
      });
  }

  const checkIndexValidity = (validState, validDimension) => {
    let errorMessage = "";
    let isValid = true;

    if (!validState && validDimension) {
      isValid = false;
      errorMessage = "The configured index already consists of custom knowledge";
    } else if ((!validState && !validDimension) || (validState && !validDimension)) {
      isValid = false;
      errorMessage = "The dimension of the configured index does not match the dimensions of the selected knowledge";
    }

    return [isValid, errorMessage];
  }

  const installClicked = () => {
    setIndexDropdown(!indexDropdown)
    if (window.location.href.toLowerCase().includes('marketplace')) {
      if (env === 'PROD') {
        window.open(`https://app.superagi.com/`, '_self');
      } else {
        window.location.href = '/';
      }
      return;
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
              <span className={styles2.top_heading}>{templateData?.name}</span>
              <span style={{fontSize: '12px', marginTop: '15px',}}
                    className={styles.tool_publisher}>by {templateData?.contributed_by}&nbsp;{'\u00B7'}&nbsp;<Image
                width={14} height={14} src="/images/upload_icon.svg"
                alt="upload-icon"
                style={{marginBottom: '1px'}}/>&nbsp;{'\u00B7'}&nbsp;{templateData?.install_number || 0}</span>

              {!template?.is_installed && <div className="dropdown_container_search" style={{width: '100%'}}>
                <div className="primary_button" onClick={installClicked}
                     style={{marginTop: '15px', cursor: 'pointer', width: '100%'}}>
                  <Image width={14} height={14} src="/images/upload_icon_dark.svg" alt="upload-icon"/>&nbsp;
                  <span>{installed}</span>{installed === 'Installing' && <span className="loader ml_10"></span>}
                </div>
                <div>
                  {indexDropdown && installed === 'Install' &&
                    <div className="custom_select_options" ref={indexRef} style={{width: '100%', maxHeight: '500px'}}>
                      <div className={styles3.knowledge_label} style={{padding: '12px 14px', maxWidth: '100%'}}>Select
                        an existing vector database collection/index to install the knowledge
                      </div>
                      {pinconeIndices && pinconeIndices.length > 0 &&
                        <div className={styles3.knowledge_db} style={{maxWidth: '100%'}}>
                          <div className={styles3.knowledge_db_name}>Pinecone</div>
                          {pinconeIndices.map((index) => (<div key={index.id} className="custom_select_option"
                                                               onClick={() => handleInstallClick(index.id)} style={{
                            padding: '12px 14px',
                            maxWidth: '100%',
                            display: 'flex',
                            justifyContent: 'space-between'
                          }}>
                            <div style={!checkIndexValidity(index.is_valid_state, index.is_valid_dimension)[0] ? {
                              color: '#888888',
                              textDecoration: 'line-through',
                              pointerEvents : 'none',
                            } : {}}>{index.name}</div>
                            {!checkIndexValidity(index.is_valid_state, index.is_valid_dimension)[0] &&
                              <div>
                                <Image width={15} height={15} src="/images/info.svg" alt="info-icon"
                                       title={checkIndexValidity(index.is_valid_state, index.is_valid_dimension)[1]}/>
                              </div>}
                          </div>))}
                        </div>}
                      {qdrantIndices && qdrantIndices.length > 0 &&
                        <div className={styles3.knowledge_db} style={{maxWidth: '100%'}}>
                          <div className={styles3.knowledge_db_name}>Qdrant</div>
                          {qdrantIndices.map((index) => (<div key={index.id} className="custom_select_option"
                                                              onClick={() => handleInstallClick(index.id)} style={{
                            padding: '12px 14px',
                            maxWidth: '100%',
                            display: 'flex',
                            justifyContent: 'space-between'
                          }}>
                            <div style={!checkIndexValidity(index.is_valid_state, index.is_valid_dimension)[0] ? {
                              color: '#888888',
                              textDecoration: 'line-through',
                              pointerEvents : 'none',
                            } : {}}>{index.name}</div>
                            {!checkIndexValidity(index.is_valid_state, index.is_valid_dimension)[0] &&
                              <div>
                                <Image width={15} height={15} src="/images/info.svg" alt="info-icon"
                                       title={checkIndexValidity(index.is_valid_state, index.is_valid_dimension)[1]}/>
                              </div>}
                          </div>))}
                        </div>}
                      {weaviateIndices && weaviateIndices.length > 0 &&
                        <div className={styles3.knowledge_db} style={{maxWidth: '100%'}}>
                          <div className={styles3.knowledge_db_name}>Weaviate</div>
                          {weaviateIndices.map((index) => (<div key={index.id} className="custom_select_option"
                                                              onClick={() => handleInstallClick(index.id)} style={{
                            padding: '12px 14px',
                            maxWidth: '100%',
                            display: 'flex',
                            justifyContent: 'space-between'
                          }}>
                            <div style={!checkIndexValidity(index.is_valid_state, index.is_valid_dimension)[0] ? {
                              color: '#888888',
                              textDecoration: 'line-through',
                              pointerEvents : 'none',
                            } : {}}>{index.name}</div>
                            {!checkIndexValidity(index.is_valid_state, index.is_valid_dimension)[0] &&
                              <div>
                                <Image width={15} height={15} src="/images/info.svg" alt="info-icon"
                                       title={checkIndexValidity(index.is_valid_state, index.is_valid_dimension)[1]}/>
                              </div>}
                          </div>))}
                        </div>}
                    </div>}
                </div>
              </div>}

              {template?.is_installed &&
                <div style={{width: '100%', display: 'flex', justifyContent: 'flex-start', marginTop: '15px'}}>
                  <div className="secondary_button" style={{cursor: 'default', width: '85%'}}>
                    <Image width={14} height={14} src="/images/tick.svg" alt="tick-icon"/>&nbsp;{installed}
                  </div>
                  <div style={{width: '5%', marginLeft: '10px'}}>
                    <button className="secondary_button" style={{padding: '8px', height: '31px'}}
                            onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
                      <Image width={14} height={14} src="/images/three_dots.svg" alt="run-icon"/>
                    </button>
                    {dropdown && <div onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
                      <ul className="dropdown_container" style={{marginTop: '0', width: '165px'}}>
                        <li className="dropdown_item" onClick={uninstallKnowledge}>Uninstall knowledge</li>
                      </ul>
                    </div>}
                  </div>
                </div>}

              <hr className={styles2.horizontal_line}/>

              <span className={styles2.description_text}>{templateData?.description}</span>

              <hr className={styles2.horizontal_line}/>

              <span style={{fontSize: '12px'}} className={styles.tool_publisher}>Model</span>
              <div className="tool_container" style={{marginTop: '10px', width: 'fit-content'}}>
                <div className={styles1.tool_text}>{templateData?.model}</div>
              </div>
              <br/>

              <span style={{fontSize: '12px'}} className={styles.tool_publisher}>Knowledge datatype</span>
              <div className="tool_container" style={{marginTop: '10px', width: 'fit-content'}}>
                <div className={styles1.tool_text}>{templateData?.data_type}</div>
              </div>
              <br/>

              <span style={{fontSize: '12px'}} className={styles.tool_publisher}>Tokenizer</span>
              <div className="tool_container" style={{marginTop: '10px', width: 'fit-content'}}>
                <div className={styles1.tool_text}>{templateData?.tokenizer}</div>
              </div>
              <br/>

              <span style={{fontSize: '12px'}} className={styles.tool_publisher}>Chunk size</span>
              <div className="tool_container" style={{marginTop: '10px', width: 'fit-content'}}>
                <div className={styles1.tool_text}>{templateData?.chunk_size}</div>
              </div>
              <br/>

              <span style={{fontSize: '12px'}} className={styles.tool_publisher}>Chunk overlap</span>
              <div className="tool_container" style={{marginTop: '10px', width: 'fit-content'}}>
                <div className={styles1.tool_text}>{templateData?.chunk_overlap}</div>
              </div>
              <br/>

              <span style={{fontSize: '12px'}} className={styles.tool_publisher}>Text splitter</span>
              <div className="tool_container" style={{marginTop: '10px', width: 'fit-content'}}>
                <div className={styles1.tool_text}>{templateData?.text_splitter}</div>
              </div>
              <br/>

              <span style={{fontSize: '12px'}} className={styles.tool_publisher}>Dimensions</span>
              <div className="tool_container" style={{marginTop: '10px', width: 'fit-content'}}>
                <div className={styles1.tool_text}>{templateData?.dimensions}</div>
              </div>

              <hr className={styles2.horizontal_line}/>

              <span style={{fontSize: '12px',}} className={styles.tool_publisher}>Last updated</span>
              <span className={styles2.description_text}>{templateData?.updated_at}</span>
            </div>
          </div>
          <div className="col-9" style={{paddingLeft: '8px'}}>
            <div style={{overflowY: 'scroll', height: '84vh'}}>
              <div className={styles2.left_container}
                   style={{marginBottom: '5px', color: 'white', padding: '16px'}}>
                <span className="text_20_bold">Overview</span><br/>
                {/*{templateData?.overview.map((item, index) => (<div key={index} style={{marginTop: '0'}}>*/}
                {/*  <div className={styles2.description_text}>{index + 1}. {item || ''}</div>*/}
                {/*  {index !== item.length - 1}*/}
                {/*</div>))}*/}
                <span className={styles2.sub_text}>{templateData?.overview}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <ToastContainer/>
    </>
  );
}