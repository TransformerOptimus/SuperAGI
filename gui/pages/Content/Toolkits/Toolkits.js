import React from 'react';
import Image from "next/image";
import styles from './Tool.module.css';
import styles1 from '../Agents/Agents.module.css'
import 'react-toastify/dist/ReactToastify.css';
import {createInternalId, returnToolkitIcon} from "@/utils/utils";

export default function Toolkits({ sendToolkitData, toolkits, env }) {
  const excludedToolkits = ["Thinking Toolkit", "Human Input Toolkit", "Resource Toolkit"];

  return (
    <>
      <div className={styles1.container}>
        <div className={styles1.title_box}>
          <p className={styles1.title_text}>Toolkits</p>
        </div>
        {env !== 'PROD' && <div className={styles1.wrapper} style={{marginBottom:'10px',marginTop:'4px'}}>
          <button style={{width:'100%'}} className="secondary_button" onClick={() => sendToolkitData({ id: -2, name: "new tool", contentType: "Add_Toolkit", internalId: createInternalId() })}>
            + Add Tool
          </button>
        </div>}
        {toolkits && toolkits.length > 0 ? (
          <div style={{ overflowY: 'scroll', height: '80vh' }}>
            <div className={styles.tool_container}>
              {toolkits.map((tool, index) =>
                  tool.name !== null && !excludedToolkits.includes(tool.name) && (
                  <div key={index} className={styles.tool_box} onClick={() => sendToolkitData(tool)}>
                    <div className="row">
                      <div className="col-12">
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-start', padding: '5px' }}>
                          <div>
                            <Image className={styles.image_class} style={{background: 'black'}} width={30} height={30} src={returnToolkitIcon(tool.name)}
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
                  )
              )}
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
    </>
  );
}

