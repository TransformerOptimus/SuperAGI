import React, {useState} from 'react';
import Image from "next/image";
import styles from './Tool.module.css';
import styles1 from '../Agents/Agents.module.css'
import 'react-toastify/dist/ReactToastify.css';

export default function Toolkits({ sendToolkitData, toolkits }) {
  const excludedToolkits = ["Thinking Toolkit", "Human Input Toolkit"];

  return (
    <>
      <div className={styles1.container}>
        <div className={styles1.title_box}>
          <p className={styles1.title_text}>Toolkits</p>
        </div>
      </div>

      <div className="row" style={{ padding: '10px' }}>
        <div className="col-12" style={{ overflowY: 'scroll', height: '84vh' }}>
          {toolkits && toolkits.length > 0 ? (
            <div>
              <div className={styles.tool_container}>
                {toolkits.map((tool) => (
                  <div key={tool.id} style={{ width: '100%' }}>
                    {tool.name !== null && !excludedToolkits.includes(tool.name) && (
                      <div className={styles.tool_box} onClick={() => sendToolkitData(tool)}>
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
              No Toolkits found
            </div>
          )}
        </div>
      </div>
    </>
  );
}

