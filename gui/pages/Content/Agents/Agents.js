import React from 'react';
import Image from "next/image";
import styles from './Agents.module.css';
import 'react-toastify/dist/ReactToastify.css';
import {createInternalId} from "@/utils/utils";

export default function Agents({sendAgentData, agents}) {
  return (<>
      <div className={styles.container}>
        <div className={styles.title_box}>
          <p className={styles.title_text}>Agents</p>
        </div>
        <div className={styles.wrapper} style={{marginBottom: '10px', marginTop: '4px'}}>
          <button style={{width: '100%'}} className="secondary_button" onClick={() => sendAgentData({
            id: -1,
            name: "new agent",
            contentType: "Create_Agent",
            internalId: createInternalId()
          })}>
            + Create Agent
          </button>
        </div>

        {agents && agents.length > 0 ? <div className={styles.wrapper} style={{overflowY: 'scroll', height: '80vh'}}>
          {agents.map((agent, index) => (
            <div key={index}>
              <div className={styles.agent_box} onClick={() => sendAgentData(agent)}>
                {agent.is_running &&
                  <div className={styles.agent_active}><Image width={14} height={14} style={{mixBlendMode: 'exclusion'}}
                                                              src="/images/loading.gif" alt="active-icon"/></div>}
                <div style={{display: 'flex', height: '15px'}}>
                  <div className={styles.text_block}><span className={styles.agent_text}>{agent.name}</span></div>
                  {agent.is_scheduled &&
                    <div style={{marginLeft: '8px'}}><Image style={{paddingBottom: '12px'}} width={20} height={28}
                                                            src="/images/event_repeat.svg" alt="check-icon"/></div>}
                </div>
              </div>
            </div>
          ))}
        </div> : <div style={{
          marginTop: '30px', display: 'flex', alignItems: 'center', justifyContent: 'center'
        }} className="form_label">
          No Agents found
        </div>}
      </div>
    </>
  );
}
