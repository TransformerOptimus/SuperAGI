import React from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import {formatNumber, formatTimeDifference} from "@/utils/utils";

export default function RunHistory({runs, setHistory, selectedRunId, setSelectedRun}) {
  return (<>
    <div style={{width:'20%',height:'100%'}}>
      <div className={styles.detail_top}>
        <div style={{display:'flex'}}>
          <div style={{display:'flex',alignItems:'center',paddingLeft:'0'}} className={styles.tab_text}>
            <div>
              <Image width={16} height={16} src="/images/update.svg" alt="update-icon"/>
            </div>
            <div style={{marginLeft:'7px'}}>Run history</div>
          </div>
        </div>
        <div style={{display:'flex'}}>
          <div style={{display:'flex',alignItems:'center',cursor:'pointer'}} onClick={() => setHistory(false)}>
            <Image width={28} height={28} src="/images/close_history.svg" alt="close-history-icon"/>
          </div>
        </div>
      </div>
      <div className={styles.detail_body} style={{overflowY: "auto",maxHeight:'80vh',position:'relative'}}>
        {runs && runs.map((run) => (<div key={run.id} onClick={() => setSelectedRun(run)} className={styles.history_box} style={selectedRunId === run.id ? {background:'#474255'} : {background:'#272335'}}>
          <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:'10px'}}>
            <div style={{display:'flex',order:'0'}}>
              {run.status === 'RUNNING' && <div><Image width={14} height={14} style={{mixBlendMode: 'exclusion'}} src="/images/loading.gif" alt="loading-icon"/></div>}
              <div className={styles.text_block} style={run.status === 'RUNNING' ? {marginLeft:'7px'} : {}}>{run.name}</div>
            </div>
            {/*{run.notification_count > 0 && <div className={styles.notification_bubble}>{run.notification_count}</div>}*/}
          </div>
          <div style={{display:'flex',alignItems:'center',justifyContent:'flex-start'}}>
            <div style={{display:'flex',alignItems:'center'}}>
              <div>
                <Image width={12} height={12} src="/images/calls_made.svg" alt="call-icon"/>
              </div>
              <div className={styles.history_info}>
                {formatNumber(run?.num_of_calls || 0)} Calls
              </div>
            </div>
            <div style={{display:'flex',alignItems:'center',marginLeft:'10px'}}>
              <div>
                <Image width={12} height={12} src="/images/schedule.svg" alt="schedule-icon"/>
              </div>
              <div className={styles.history_info}>
                {formatTimeDifference(run.time_difference)}
              </div>
            </div>
          </div>
        </div>))}
      </div>
    </div>
  </>)
}