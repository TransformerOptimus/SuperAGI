import React from 'react';
import Image from "next/image";
import styles from '../Toolkits/Tool.module.css';
import styles1 from '../Agents/Agents.module.css'
import {createInternalId} from "@/utils/utils";

export default function Knowledge({sendKnowledgeData, knowledge}) {
  return (
    <>
      <div className={styles1.container}>
        <div className={styles1.title_box}>
          <p className={styles1.title_text}>Knowledges</p>
        </div>
        <div className={styles1.wrapper} style={{marginBottom: '10px', marginTop: '4px'}}>
          <button style={{width: '100%'}} className="secondary_button" onClick={() => sendKnowledgeData({
            id: -6,
            name: "new knowledge",
            contentType: "Add_Knowledge",
            internalId: createInternalId()
          })}>
            + Add Knowledge
          </button>
        </div>

        {knowledge && knowledge.length > 0 ? (
          <div style={{overflowY: 'scroll', height: '80vh'}}>
            <div className={styles.tool_container}>
              {knowledge.map((item, index) => (
                <div key={index} className={styles.tool_box} onClick={() => sendKnowledgeData({
                  id: item.id,
                  name: item.name,
                  contentType: "Knowledge",
                  internalId: createInternalId()
                })}>
                  <div className="row">
                    <div className="col-12">
                      <div
                        style={{display: 'flex', alignItems: 'center', justifyContent: 'flex-start', padding: '5px'}}>
                        <div style={{marginLeft: '8px'}}>
                          <div className={styles.tool_name}>{item.name}&nbsp;{item.is_marketplace &&
                            <Image width={13} height={13} src="/images/widgets.svg" alt="markteplace-icon"/>}</div>
                          <div className={styles.tool_publisher}>by {item.contributed_by}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>)
              )}
            </div>
          </div>
        ) : (
          <div style={{
            marginTop: '30px', display: 'flex', alignItems: 'center', justifyContent: 'center'
          }} className="form_label">
            No Knowledge found
          </div>
        )}
      </div>
    </>
  );
}