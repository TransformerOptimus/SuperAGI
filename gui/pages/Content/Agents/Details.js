import React, {useEffect, useState} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import {formatNumber} from "@/utils/utils";
import {EventBus} from "@/utils/eventBus";

export default function Details({agentDetails1, runCount, agentScheduleDetails, agent}) {
  const [showGoals, setShowGoals] = useState(false);
  const [showConstraints, setShowConstraints] = useState(false);
  const [showInstructions, setShowInstructions] = useState(false);
  const [filteredInstructions, setFilteredInstructions] = useState([]);
  const [scheduleText, setScheduleText] = useState('');
  const [agentDetails, setAgentDetails] = useState(null)
  const info_text = {
    marginLeft: '7px',
  };

  const info_text_secondary = {
    marginLeft: '3px',
    marginTop: '2px',
    color: '#888888',
    lineHeight: '13px',
    fontSize: '11px'
  };

  const openToolkitTab = (toolId) => {
    EventBus.emit('openToolkitTab', {toolId: toolId});
  }

  useEffect(() => {
    if (Array.isArray(agentDetails?.instruction)) {
      setFilteredInstructions(agentDetails.instruction.filter(instruction => instruction.trim() !== ''));
    }
  }, [agentDetails]);
  useEffect(() => {
    setAgentDetails(agentDetails1)
  }, [agentDetails1]);

  useEffect(() => {
    if(!agentScheduleDetails){
      setScheduleText('')
      return
    }
    if (agent?.is_scheduled) {
      if (agentScheduleDetails?.recurrence_interval !== null) {
        if ((agentScheduleDetails?.expiry_runs === -1 || agentScheduleDetails?.expiry_runs == null) && agentScheduleDetails?.expiry_date !== null) {
          let expiryDate;

          if (agentScheduleDetails?.expiry_date) {
            const [day, month, year] = agentScheduleDetails.expiry_date.split("/");
            expiryDate = new Date(year, month - 1, day);
          }

          const tempScheduleText = `The agent is scheduled to run on ${agentScheduleDetails?.start_date} ${agentScheduleDetails?.start_time} and will recursively run after every ${agentScheduleDetails?.recurrence_interval} and will expire after ${
            expiryDate ? new Intl.DateTimeFormat('en-GB', {
              day: '2-digit',
              month: 'short',
              year: 'numeric'
            }).format(expiryDate) : ''
          }`;

          setScheduleText(tempScheduleText);
        } else if ((agentScheduleDetails?.expiry_runs > 0) && agentScheduleDetails?.expiry_date == null) {
          setScheduleText('The agent is scheduled to run on ' + agentScheduleDetails?.start_date + ' ' + agentScheduleDetails?.start_time + ' and will recursively run after every ' + agentScheduleDetails?.recurrence_interval + ' and will expire after ' + agentScheduleDetails?.expiry_runs + ' runs')
        } else {
          setScheduleText('The agent is scheduled to run on ' + agentScheduleDetails?.start_date + ' ' + agentScheduleDetails?.start_time + ' and will recursively run after every ' + agentScheduleDetails?.recurrence_interval + ' and will never expire')
        }
      } else {
        setScheduleText('The agent is scheduled to run on ' + agentScheduleDetails?.start_date + ' ' + agentScheduleDetails?.start_time)
      }
    }
  }, [agentScheduleDetails]);

  return (<>
    <div className={styles.history_box} style={{background: '#272335', padding: '15px', cursor: 'default'}}>
      <div className={styles.detail_name}>{agentDetails?.name || ''}</div>
      <div>{agentDetails?.description || ''}</div>
      <div className={styles.separator}></div>
      <div
        style={{display: 'flex', marginBottom: '5px', alignItems: 'center', justifyContent: 'flex-start', gap: '7.5%'}}>
        <div>
          <div className={styles.agent_info_box}>
            <div><Image width={12} height={12} src="/images/calls_made.svg" alt="calls-icon"/></div>
            <div style={info_text_secondary}>Total Calls</div>
          </div>
          <div className={styles.feed_title}
               style={{fontSize: '20px', marginLeft: '0'}}>{formatNumber(agentDetails?.calls || 0)}</div>
        </div>
        <div>
          <div className={styles.agent_info_box}>
            <div><Image width={12} height={12} src="/images/runs_made.svg" alt="runs-icon"/></div>
            <div style={info_text_secondary}>Total Runs</div>
          </div>
          <div className={styles.feed_title} style={{fontSize: '20px', marginLeft: '0'}}>{runCount || 0}</div>
        </div>
        <div>
          <div className={styles.agent_info_box}>
            <div><Image width={12} height={12} src="/images/tokens_consumed.svg" alt="tokens-icon"/></div>
            <div style={info_text_secondary}>Tokens Consumed</div>
          </div>
          <div className={styles.feed_title}
               style={{fontSize: '20px', marginLeft: '0'}}>{formatNumber(agentDetails?.tokens || 0)}</div>
        </div>
      </div>
      <div className={styles.separator}></div>
      <div className={styles.agent_info_box}>
        <div><Image width={15} height={15} src="/images/flag.svg" alt="goals-icon"/></div>
        <div style={info_text}>{agentDetails?.goal?.length || 0} Goals</div>
      </div>
      {agentDetails?.goal && agentDetails?.goal?.length > 0 && <div>
        <div className={styles.large_text_box} style={!showGoals ? {overflow: 'hidden', display: '-webkit-box'} : {}}>
          {agentDetails?.goal?.map((goal, index) => (<div key={index} style={{marginTop: '0'}}>
            <div>{index + 1}. {goal || ''}</div>
            {index !== agentDetails?.goal?.length - 1 && <br/>}
          </div>))}
        </div>
        <div className={styles.show_more_button} onClick={() => setShowGoals(!showGoals)}>
          {showGoals ? 'Show Less' : 'Show More'}
        </div>
      </div>}
      {filteredInstructions && filteredInstructions.length > 0 && <div>
        <div className={styles.separator}></div>
        <div className={styles.agent_info_box}>
          <div><Image width={15} height={15} src="/images/instructions.svg" alt="instruction-icon"/></div>
          <div style={info_text}>{filteredInstructions.length || 0} Instructions</div>
        </div>
        <div>
          <div className={styles.large_text_box}
               style={!showInstructions ? {overflow: 'hidden', display: '-webkit-box'} : {}}>
            {filteredInstructions.map((instruction, index) => (<div key={index} style={{marginTop: '0'}}>
              <div>{index + 1}. {instruction || ''}</div>
              {index !== filteredInstructions.length - 1 && <br/>}
            </div>))}
          </div>
          <div className={styles.show_more_button}
               onClick={() => setShowInstructions(!showInstructions)}>{showInstructions ? 'Show Less' : 'Show More'}</div>
        </div>
      </div>}
      {agentDetails && <div>{agentDetails.tools && agentDetails.tools.length > 0 && <div>
        <div className={styles.separator}></div>
        <div className={styles.agent_info_box}>
          <div><Image width={15} height={15} src="/images/tools_dark.svg" alt="tools-icon"/></div>
          <div style={info_text}>Tools assigned</div>
        </div>
        <div className={styles.agent_info_tools}>
          {agentDetails?.tools?.map((tool, index) =>
            (<div onClick={() => openToolkitTab(tool.id)} key={index} className="tool_container"
                  style={{marginTop: '0', marginBottom: '5px', cursor: 'pointer'}}>
              <div className={styles.tool_text}>{tool.name || ''}</div>
            </div>))}
        </div>
      </div>}</div>}
      {agentDetails && <div>{agentDetails.constraints && agentDetails.constraints?.length > 0 && <div>
        <div className={styles.separator}></div>
        <div className={styles.agent_info_box}>
          <div><Image width={15} height={15} src="/images/close_fullscreen.svg" alt="constraint-icon"/></div>
          <div style={info_text}>{agentDetails?.constraints.length || 0} Constraints</div>
        </div>
        <div className={styles.large_text_box}
             style={!showConstraints ? {overflow: 'hidden', display: '-webkit-box'} : {}}>
          {agentDetails?.constraints?.map((constraint, index) => (<div key={index} style={{marginTop: '0'}}>
            <div>{index + 1}. {constraint || ''}</div>
            {index !== agentDetails.constraints.length - 1 && <br/>}
          </div>))}
        </div>
        <div className={styles.show_more_button}
             onClick={() => setShowConstraints(!showConstraints)}>{showConstraints ? 'Show Less' : 'Show More'}</div>
      </div>}</div>}
      <div className={styles.separator}></div>
      <div className={styles.agent_info_box}>
        <div><Image width={15} height={15} src="/images/fact_check.svg" alt="queue-icon"/></div>
        <div style={info_text}>{agentDetails?.agent_workflow || ''}</div>
      </div>
      {agentDetails?.knowledge_name && <div className={styles.agent_info_box}>
        <div><Image width={15} height={15} src="/images/books.svg" alt="book-icon"/></div>
        <div style={info_text}>{agentDetails?.knowledge_name}</div>
      </div>}
      <div className={styles.agent_info_box}>
        <div><Image width={15} height={15} src="/images/deployed_code.svg" alt="model-icon"/></div>
        <div style={info_text}>{agentDetails?.model || ''}</div>
      </div>
      {/*<div className={styles.agent_info_box}>*/}
      {/*  <div><Image width={15} height={15} src="/images/cancel_presentation.svg" alt="exit-icon"/></div>*/}
      {/*  <div style={info_text}>{exit}</div>*/}
      {/*</div>*/}
      {/* <div className={styles.agent_info_box}>
        <div><Image width={15} height={15} src="/images/overview.svg" alt="window-icon"/></div>
        <div style={info_text}>{agentDetails?.memory_window || 0} milliseconds</div>
      </div> */}
      <div className={styles.agent_info_box}>
        <div><Image width={15} height={15} src="/images/key.svg" alt="permission-type-icon"/></div>
        <div style={info_text}>{agentDetails?.permission_type?.replace(/\s*\([^)]*\)/g, '') || ''}</div>
      </div>
      {agentDetails?.max_iterations && <div className={styles.agent_info_box}>
        <div><Image width={15} height={15} src="/images/info.svg" alt="info-icon"/></div>
        <div style={info_text}>Stop after {agentDetails.max_iterations} iterations</div>
      </div>}
      {agent?.is_scheduled && scheduleText && <div className={styles.agent_info_box}>
        <div><Image width={15} height={15} src="/images/event_repeat.svg" alt="info-icon"/></div>
        <div style={info_text}>{scheduleText}</div>
      </div>}
    </div>
  </>)
}