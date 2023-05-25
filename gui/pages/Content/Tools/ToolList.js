import React, {useState} from 'react';
import Image from "next/image";
import styles from './Tool.module.css';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function ToolList({onSelectEvent}) {
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
      icon: '/images/default_tool.png',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: true
    },
    {
      id: 1,
      name: 'stock parser',
      publisher: 'Yourself',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'custom',
      isEditing: false,
      icon: '/images/custom_tool.png',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: false
    },
    {
      id: 2,
      name: 'gmailer',
      publisher: 'Google',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'default',
      isEditing: false,
      icon: '/images/default_tool.png',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: true
    },
    {
      id: 3,
      name: 'stock parser',
      publisher: 'Yourself',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'custom',
      isEditing: false,
      icon: '/images/custom_tool.png',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: false
    },
    {
      id: 4,
      name: 'gmailer',
      publisher: 'Google',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'default',
      isEditing: false,
      icon: '/images/default_tool.png',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: true
    },
    {
      id: 5,
      name: 'stock parser',
      publisher: 'Yourself',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'custom',
      isEditing: false,
      icon: '/images/custom_tool.png',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: false
    },
    {
      id: 6,
      name: 'gmailer',
      publisher: 'Google',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'default',
      isEditing: false,
      icon: '/images/default_tool.png',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: true
    },
    {
      id: 7,
      name: 'stock parser',
      publisher: 'Yourself',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'custom',
      isEditing: false,
      icon: '/images/custom_tool.png',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: false
    },
    {
      id: 8,
      name: 'gmailer',
      publisher: 'Google',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'default',
      isEditing: false,
      icon: '/images/default_tool.png',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: true
    },
    {
      id: 9,
      name: 'stock parser',
      publisher: 'Yourself',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'custom',
      isEditing: false,
      icon: '/images/custom_tool.png',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: false
    },
    {
      id: 10,
      name: 'gmailer',
      publisher: 'Google',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'default',
      isEditing: false,
      icon: '/images/default_tool.png',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: true
    },
    {
      id: 11,
      name: 'stock parser',
      publisher: 'Yourself',
      description: 'shifting timeline across multiple time strings. Regardless shifting timeline across multiple time strings',
      type: 'custom',
      isEditing: false,
      icon: '/images/custom_tool.png',
      tags: ['gmailer', 'jira-v2', 'openai', 'superagi'],
      isVerified: false
    }
  ]
  const [tools, setTools] = useState(toolArray);

  const handleFilter = (value) => {
    setFilter(value)
    const filteredTools = value === 'custom' ? toolArray.filter(tool => tool.type === 'custom') : toolArray;
    setTools(filteredTools);
  };

  const handleEditDropdown = (toolId, mouseOver) => {
    const updatedAgents = tools.map((tool) => tool.id === toolId ? {...tool, isEditing: mouseOver} : tool);

    setTools(updatedAgents);
  };
  const openDeleteModal = (value) => {
    setDeleteModal(true);
    setSelectedTool(value)
  };

  const closeDeleteModal = () => {
    setDeleteModal(false);
    setSelectedTool(-1)
  };

  const handleToolDelete = (toolId) => {
    const updatedAgents = tools.filter((tool) => tool.id !== toolId);
    setTools(updatedAgents);
    closeDeleteModal();
    toast.dark('Tool uninstalled', {autoClose: 1800});
  };

  const preventDefault = (e) => {
    e.stopPropagation()
  }

  return (
    <>
    <div>
      <div className="row">
        <div className="col-6">
          <div className="page_title">Tools</div>
        </div>
        <div className="col-6">
          <button className="primary_medium" style={{float: 'right', marginRight: '10px'}} onClick={() => onSelectEvent('create_tool')}>
            <Image width={16} height={16} src="/images/add_circle.png" alt="tool-icon"/>&nbsp;Add
          </button>
        </div>
      </div>
      <div className="row" style={{padding: '10px'}}>
        <div className="col-12">
          {tools.length > 0 ? <div>
            <div style={{display: 'flex', marginBottom: '15px'}}>
              <div onClick={() => handleFilter('all')} className={`${styles.tool_filter} ${filterSelected === 'all' ? styles.selected : styles.not_selected}`}>
                All
              </div>
              <div onClick={() => handleFilter('custom')} className={`${styles.tool_filter} ${filterSelected === 'custom' ? styles.selected : styles.not_selected}`}>
                Custom
              </div>
            </div>
            <div className={styles.tool_container}>
              {tools.map((tool) => (<div key={tool.id} className={styles.tool_box}>
                <div className="report_card" style={{paddingBottom:'10px',marginBottom:'-6px'}}>
                  <div className="row">
                    <div className="col-12">
                      <div style={{display:'flex'}}>
                        <div>
                          <Image width={40} height={40} src={tool.icon} alt="tool-icon"/>
                        </div>
                        <div style={{marginLeft:'15px'}}>
                          <div className={styles.tool_name}>{tool.name}</div>
                          <div className={styles.tool_publisher}>by {tool.publisher}&nbsp;{tool.isVerified && <Image width={16} height={16} src="/images/is_verified.png" alt="verified-icon"/>}</div>
                        </div>
                        <div className="dropdown_container" style={{marginTop:'-2px',flexBasis:'auto',marginLeft:'auto'}}
                             onMouseLeave={() => handleEditDropdown(tool.id, false)}>
                          <div style={{
                            display: 'flex', alignItems: 'center', justifyContent: 'flex-end'
                          }}>
                            <button style={{marginLeft: '10px'}} className="more_button"
                                    onMouseEnter={() => handleEditDropdown(tool.id, true)}>
                              <Image width={15} height={16} className="three_dots_img"
                                     src="/images/three_dots.svg" alt="more-options"/>
                            </button>
                          </div>
                          {tool.isEditing && (<div className="dropdown" style={{marginLeft: '-38px'}}
                                                    onMouseEnter={() => handleEditDropdown(tool.id, true)}
                                                    onMouseLeave={() => handleEditDropdown(tool.id, false)}>
                            <ul>
                              <li>Edit</li>
                              <li onClick={() => openDeleteModal(tool.id)}
                                  style={{color: '#FF5454'}} className="act_delete">Uninstall
                              </li>
                            </ul>
                          </div>)}
                        </div>
                      </div>
                      <div className={styles.tool_description}>{tool.description}</div>
                      <div className={styles.tag_box}>
                        {tool.tags.map((tag, index) => (<div key={index} className="tool_container" style={{marginBottom:'10px'}}>
                          {tag}
                        </div>))}
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
      {showDeleteModal && (<div className="modal" onClick={closeDeleteModal}>
        <div className="modal-content" style={{width: '35%'}} onClick={preventDefault}>
          <div style={{padding: '30px 30px 10px 30px'}}>
            <p className="form_label" style={{fontSize: '18px'}}>Are you sure you want to uninstall
              this tool?</p>
          </div>
          <br/>
          <div style={{display: 'flex', justifyContent: 'flex-end', padding: '0 30px 20px 0'}}>
            <button className="secondary_medium" style={{marginRight: '10px'}}
                    onClick={closeDeleteModal}>Cancel
            </button>
            <button className="primary_medium" onClick={() => handleToolDelete(selectedTool)}>
              Uninstall
            </button>
          </div>
        </div>
      </div>)}
      </div>
      <ToastContainer/>
    </>
  );
}
