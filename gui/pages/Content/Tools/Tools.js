import React, {useState, useEffect} from 'react';
import Image from "next/image";
import styles from './Tool.module.css';
import styles1 from '../Agents/Agents.module.css'
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import axios from 'axios';

export default function Tools({ sendToolData, tools }) {
  const [filterSelected, setFilter] = useState('all');
 

  const excludedTools = ["ThinkingTool", "LlmThinkingTool", "Human", "ReasoningTool"];

  // useEffect(() => {
  //   // Fetch tools from the endpoint
  //   axios.get('http://192.168.211.48:8001/tool_kits/get/local/list')
  //     .then(response => {
  //       console.log(response.data)
  //       const data = response.data || [];
  //       const updatedData = data.map(item => {
  //         return { ...item, contentType: "Tools" };
  //       });
  //       setTools(updatedData);
  //     })
  //     .catch(error => {
  //       console.log('Error fetching tools:', error);
  //       // Handle error if needed
  //     });
  // }, []);

  const toolsArray = [
    {
      id: 1,
      name: "Tool 1",
      description: "custom",
    },
    {
      id: 2,
      name: "Tool 2",
      description: "default",
    },
    {
      id: 3,
      name: "Tool 3",
      description: "custom",
    },
    {
      id: 4,
      name: "Tool 4",
      description: "default",
    },
  ];
  
  
  const handleFilter = (value) => {
    setFilter(value);
    const filteredTools = value === 'custom' ? toolsArray.filter(tool => tool.type === 'custom') : toolsArray;
    setTools(filteredTools);
  };

  return (
    <>
      <div className={styles1.container}>
        <div className={styles1.title_box}>
          <p className={styles1.title_text}>Tools</p>
        </div>

        <div className={styles.wrapper} style={{ marginBottom: '10px', marginTop: '4px' }}>
          <button style={{ width: '100%' }} className="secondary_button" onClick={() => sendToolData({ id: -2, name: 'new tool', contentType: 'Create_Tool' })}>
            + Create Tool
          </button>
        </div>
      </div>

      <div className="row" style={{ padding: '10px' }}>
        <div className="col-12" style={{ overflowY: 'scroll', height: '84vh' }}>
          {toolsArray && toolsArray.length > 0 ? (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-evenly', marginBottom: '10px' }}>
                <button onClick={() => handleFilter('all')} className={styles.tab_button} style={filterSelected === 'all' ? { background: '#454254' } : { background: 'transparent' }}>
                  All
                </button>
                <button onClick={() => handleFilter('custom')} className={styles.tab_button} style={filterSelected === 'custom' ? { background: '#454254' } : { background: 'transparent' }}>
                  Custom
                </button>
              </div>

              <div className={styles.tool_container}>
                {toolsArray.map((tool) => (
                  <div key={tool.id} style={{ width: '100%' }}>
                    {tool.name !== null && !excludedTools.includes(tool.name) && (
                      <div className={styles.tool_box} onClick={() => sendToolData({tool,contentType: 'Tools'})}>
                        <div className="row">
                          <div className="col-12">
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-start', padding: '5px' }}>
                              <div>
                                <Image className={styles.image_class} width={30} height={30} src="/images/custom_tool.svg"
                                  alt="tool-icon" />
                              </div>
                              <div style={{ marginLeft: '8px' }}>
                                <div className={styles.tool_name}>{tool.name}</div>
                                <div className={styles.tool_publisher}>by SuperAGI</div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div style={{
              marginTop: '30px', display: 'flex', alignItems: 'center', justifyContent: 'center'
            }} className="form_label">
              No Tools found
            </div>
          )}
        </div>
      </div>

      <ToastContainer />
    </>
  );
}

