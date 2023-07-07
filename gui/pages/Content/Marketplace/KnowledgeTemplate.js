import React, {useEffect, useRef, useState} from 'react';
import Image from "next/image";
import styles from '.././Toolkits/Tool.module.css';
import styles1 from '../Agents/Agents.module.css';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles2 from "./Market.module.css"
import styles3 from "../Knowledge/Knowledge.module.css"
import {EventBus} from "@/utils/eventBus";
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

export default function KnowledgeTemplate({template, env}) {
  const [installed, setInstalled] = useState('')
  const [markdownContent, setMarkdownContent] = useState('');
  const indexRef = useRef(null);
  const [indexDropdown, setIndexDropdown] = useState(false);
  const collections = [
    {
      name: 'database name • Pinecone',
      indices: ['index name 1', 'index name 2', 'index name 3']
    },
    {
      name: 'database name • Qdrant',
      indices: ['index name 4', 'index name 5']
    }
  ];
  const [selectedIndex, setSelectedIndex] = useState(collections[0].indices[0]);

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
    setInstalled(template && template.is_installed ? 'Installed' : 'Install');
    if (window.location.href.toLowerCase().includes('marketplace')) {
      setInstalled('Sign in to install');
    } else {
      
    }
  }, []);

  const handleInstallClick = (item) => {

  }

  function handleBackClick() {
    EventBus.emit('goToMarketplace', {});
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
              <span className={styles2.top_heading}>{template.name}</span>
              <span style={{fontSize: '12px',marginTop: '15px',}} className={styles.tool_publisher}>by {template.contributor}</span>

              <div className="dropdown_container_search" style={{width:'100%'}}>
                <div className="primary_button" onClick={() => setIndexDropdown(!indexDropdown)}
                     style={{marginTop:'15px',cursor:'pointer',width:'100%',background: template && template.is_installed ? 'rgba(255, 255, 255, 0.14)':'#FFF',color:template && template.is_installed ? '#FFFFFF':'#000'}}>
                  {(template && template.is_installed) ? <Image width={14} height={14} src="/images/tick.svg" alt="tick-icon"/> : <Image width={14} height={14} src="/images/upload_icon_dark.svg" alt="upload-icon"/>}&nbsp;{installed}
                </div>
                <div>
                  {indexDropdown && <div className="custom_select_options" ref={indexRef} style={{width:'100%',maxHeight:'500px'}}>
                    <div className={styles3.knowledge_label} style={{padding:'12px 14px',maxWidth:'100%'}}>Select an existing vector database collection/index to install the knowledge</div>
                    {collections.map((collection, index) => (<div key={index} className={styles3.knowledge_db} style={{maxWidth:'100%'}}>
                      <div className={styles3.knowledge_db_name}>{collection.name}</div>
                      {collection.indices.map((item, index) => (<div key={index} className="custom_select_option" onClick={() => handleInstallClick(item)} style={{padding:'12px 14px',maxWidth:'100%'}}>
                        {item}
                      </div>))}
                    </div>))}
                  </div>}
                </div>
              </div>

              <hr className={styles2.horizontal_line} />

              <span className={styles2.description_text}>{template.description}</span>

              <hr className={styles2.horizontal_line} />

              <span style={{fontSize: '12px'}} className={styles.tool_publisher}>Model(s)</span>
              <div className="tool_container" style={{marginTop:'10px',width: 'fit-content'}}>
                <div className={styles1.tool_text}>{template.model}</div>
              </div><br />

              <span style={{fontSize: '12px'}} className={styles.tool_publisher}>Knowledge datatype</span>
              <div className="tool_container" style={{marginTop:'10px',width: 'fit-content'}}>
                <div className={styles1.tool_text}>{template.datatype}</div>
              </div><br />

              <span style={{fontSize: '12px'}} className={styles.tool_publisher}>Tokenizer</span>
              <div className="tool_container" style={{marginTop:'10px',width: 'fit-content'}}>
                <div className={styles1.tool_text}>{template.tokenizer}</div>
              </div><br />

              <span style={{fontSize: '12px'}} className={styles.tool_publisher}>Chunk size</span>
              <div className="tool_container" style={{marginTop:'10px',width: 'fit-content'}}>
                <div className={styles1.tool_text}>{template.chunk_size}</div>
              </div><br />

              <span style={{fontSize: '12px'}} className={styles.tool_publisher}>Chunk overlap</span>
              <div className="tool_container" style={{marginTop:'10px',width: 'fit-content'}}>
                <div className={styles1.tool_text}>{template.chunk_overlap}</div>
              </div><br />

              <span style={{fontSize: '12px'}} className={styles.tool_publisher}>Text splitter</span>
              <div className="tool_container" style={{marginTop:'10px',width: 'fit-content'}}>
                <div className={styles1.tool_text}>{template.text_splitter}</div>
              </div><br />

              <span style={{fontSize: '12px'}} className={styles.tool_publisher}>Dimensions</span>
              <div className="tool_container" style={{marginTop:'10px',width: 'fit-content'}}>
                <div className={styles1.tool_text}>{template.dimension}</div>
              </div>

              <hr className={styles2.horizontal_line} />

              <span style={{fontSize: '12px',}} className={styles.tool_publisher}>Last updated</span>
              <span className={styles2.description_text}>{template.updated_at}</span>
            </div>
          </div>
          <div className="col-9" style={{paddingLeft: '8px'}}>
              <div className={styles2.left_container} style={{marginBottom: '8px'}}>
                <div className={styles2.markdown_container}>
                  {markdownContent && markdownContent !== '' ? <ReactMarkdown
                      className={styles2.markdown_style}>{markdownContent}</ReactMarkdown> :
                    <div style={{display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',marginTop:'40px',width:'100%'}}>
                      <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions" />
                      <span className={styles1.feed_title} style={{marginTop: '8px'}}>No Overview to display!</span>
                    </div>
                  }
                </div>
              </div>
          </div>
        </div>
      </div>
      <ToastContainer/>
    </>
  );
}