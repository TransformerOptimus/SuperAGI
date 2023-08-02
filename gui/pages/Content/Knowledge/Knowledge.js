import React from 'react';
import Image from "next/image";
import styles from '../Toolkits/Tool.module.css';
import styles1 from '../Agents/Agents.module.css'
import {createInternalId} from "@/utils/utils";

export default function Knowledge({sendKnowledgeData, knowledge}) {
  return (
    <>
      <div className="container">
        <p className="text_14 mt_8 mb_12 ml_8">Knowledges</p>
        <div className="w_100 mb_10">
          <button className="secondary_button w_100" onClick={() => sendKnowledgeData({
            id: -6,
            name: "new knowledge",
            contentType: "Add_Knowledge",
            internalId: createInternalId()
          })}>
            + Add Knowledge
          </button>
        </div>

        {knowledge && knowledge.length > 0 ? (
          <div className="vertical_selection_scroll">
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
        ) : (<div className="form_label mt_20 horizontal_container justify_center">No Knowledge found</div>
        )}
      </div>
    </>
  );
}