import React, {useState} from 'react';
import Image from "next/image";
import styles from './Tool.module.css';
import styles1 from '../Agents/Agents.module.css'
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function ToolList({sendToolData}) {
  const [filterSelected, setFilter] = useState('all');
  const [showDeleteModal, setDeleteModal] = useState(false);
  const [selectedTool, setSelectedTool] = useState(-1);

  const toolArray = [
    {
      id: 0,
      name: 'gmailer',
      publisher: 'Google',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'default',
      isEditing: false,
      icon: '/images/default_tool.svg',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: true,
      contentType: 'Tools',
    },
    {
      id: 1,
      name: 'stock parser',
      publisher: 'Yourself',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'custom',
      isEditing: false,
      icon: '/images/custom_tool.svg',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: false,
      contentType: 'Tools',
    },
    {
      id: 2,
      name: 'gmailer',
      publisher: 'Google',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'default',
      isEditing: false,
      icon: '/images/default_tool.svg',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: true,
      contentType: 'Tools',
    },
    {
      id: 3,
      name: 'stock parser',
      publisher: 'Yourself',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'custom',
      isEditing: false,
      icon: '/images/custom_tool.svg',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: false,
      contentType: 'Tools',
    },
    {
      id: 4,
      name: 'gmailer',
      publisher: 'Google',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'default',
      isEditing: false,
      icon: '/images/default_tool.svg',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: true,
      contentType: 'Tools',
    },
    {
      id: 5,
      name: 'stock parser',
      publisher: 'Yourself',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'custom',
      isEditing: false,
      icon: '/images/custom_tool.svg',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: false,
      contentType: 'Tools',
    },
    {
      id: 6,
      name: 'gmailer',
      publisher: 'Google',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'default',
      isEditing: false,
      icon: '/images/default_tool.svg',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: true,
      contentType: 'Tools',
    }
  ]

  const [tools, setTools] = useState(toolArray);

  const handleFilter = (value) => {
    setFilter(value)
    const filteredTools = value === 'custom' ? toolArray.filter(tool => tool.type === 'custom') : toolArray;
    setTools(filteredTools);
  };

  return (
    <>
      <div>
        <div className={styles1.container}>
          <div className={styles1.title_box}>
            <p className={styles1.title_text}>Tools</p>
          </div>
          {/*<div className={styles1.wrapper} style={{marginBottom:'10px',marginTop:'3px'}}>*/}
          {/*  <button style={{width:'100%'}} className={styles1.agent_button} onClick={() => sendToolData({ id: -2, name: 'new tool', contentType: 'Create_Tool' })}>*/}
          {/*    + Add Tool*/}
          {/*  </button>*/}
          {/*</div>*/}
        </div>
        <div className="row" style={{padding: '10px'}}>
          <div className="col-12">
            {tools.length > 0 ? <div>
              <div style={{display:'flex',alignItems:'center',justifyContent:'space-evenly',marginBottom:'10px'}}>
                <button onClick={() => handleFilter('all')} className={styles.tab_button} style={filterSelected === 'all' ? {background:'#454254'} : {background:'transparent'}}>
                  All
                </button>
                <button onClick={() => handleFilter('custom')} className={styles.tab_button} style={filterSelected === 'custom' ? {background:'#454254'} : {background:'transparent'}}>
                  Custom
                </button>
              </div>
              <div className={styles.tool_container}>
                {tools.map((tool) => (<div key={tool.id} className={styles.tool_box}>
                  <div className="row">
                    <div className="col-12">
                      <div style={{display:'flex',alignItems:'center',justifyContent:'flex-start',padding:'5px'}}>
                        <div>
                          <Image className={styles.image_class} width={30} height={30} src={tool.icon} alt="tool-icon"/>
                        </div>
                        <div style={{marginLeft:'8px',marginTop:'3px'}}>
                          <div className={styles.tool_name}>{tool.name}</div>
                          <div className={styles.tool_publisher}>by {tool.publisher}&nbsp;{tool.isVerified && <Image width={16} height={16} src="/images/is_verified.svg" alt="verified-icon"/>}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>))}
              </div>
            </div> : <div style={{
              marginTop: '30px', display: 'flex', alignItems: 'center', justifyContent: 'center'
            }} className="form_label">
              No tools yet!
            </div>}
          </div>
        </div>
      </div>
      <ToastContainer/>
    </>
  );
}