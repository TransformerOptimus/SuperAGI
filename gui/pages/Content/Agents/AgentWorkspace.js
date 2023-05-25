import React, {useState} from 'react';
import Image from 'next/image';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles from './Agents.module.css';
import ActivityFeed from './ActivityFeed';
import TaskQueue from './TaskQueue';
import RunHistory from "./RunHistory";
import ActionConsole from "./ActionConsole";
import Details from "./Details";
import ResourceManager from "./ResourceManager";
import { EventBus } from "../../eventBus";

export default function AgentWorkspace({agent}) {
  const [leftPanel, setLeftPanel] = useState('activity_feed')
  const [rightPanel, setRightPanel] = useState('details')
  const [history, setHistory] = useState(false)
  const [selectedRun, setSelectedRun] = useState(agent.runs[0])
  const [runModal, setRunModal] = useState(false)
  const agent_goals = agent.goal
  const [goals, setGoals] = useState(agent_goals);
  const [runName, setRunName] = useState("new run");

  const addGoal = () => {
    setGoals((prevArray) => [...prevArray, 'new goal']);
  };

  const handleGoalChange = (index, newValue) => {
    const updatedGoals = [...goals];
    updatedGoals[index] = newValue;
    setGoals(updatedGoals);
  };

  const handleGoalDelete = (index) => {
    const updatedGoals = [...goals];
    updatedGoals.splice(index, 1);
    setGoals(updatedGoals);
  };

  const handleRunNameChange = (event) => {
    setRunName(event.target.value);
  }

  const handleCreateRun = () => {
    if (runName.replace(/\s/g, '') === '') {
      toast.dark("Run name can't be blank", {autoClose: 1800});
      return
    }

    if (goals.length <= 0) {
      toast.dark("Agent needs to have goals", {autoClose: 1800});
      return
    }

    EventBus.emit('runCreate', {
      agentId: agent.id,
      newRun: {
        id: agent.runs.length,
        name: runName,
        is_running: false,
        calls: 0,
        last_active: 0,
        notification_count: 0,
        tasks: [],
        feeds: []
      },
      updatedGoals: goals
    });
    setRunModal(false);
  };

  const closeRunModal = () => {
    setGoals(agent_goals);
    setRunName("new run");
    setRunModal(false);
  };

  const preventDefault = (e) => {
    e.stopPropagation();
  };

  return (<>
    <div style={{display:'flex',height:'100%'}}>
      {history && <RunHistory runs={agent.runs} selectedRun={selectedRun} setSelectedRun={setSelectedRun} setHistory={setHistory}/>}
      <div style={{width: history ? '40%' : '60%',height:'100%'}}>
        <div className={styles.detail_top}>
          <div style={{display:'flex'}}>
            {!history && <div style={{display:'flex',alignItems:'center',cursor:'pointer',marginRight:'7px'}} onClick={() => setHistory(true)}>
              <Image width={16} height={16} src="/images/history.png" alt="history-icon"/>
            </div>}
            <div style={{display:'flex',alignItems:'center',marginLeft:'2px'}} className={styles.tab_text}>
              {selectedRun.is_running && <div style={{marginLeft:'-6px'}}><Image width={14} height={14} style={{mixBlendMode: 'exclusion'}} src="/images/loading.gif" alt="loading-icon"/></div>}
              <div style={selectedRun.is_running ? {marginLeft:'7px'} : {marginLeft:'-8px'}}>{selectedRun.name}</div>
            </div>
            <div style={{marginLeft:'7px'}}>
              <button onClick={() => setLeftPanel('activity_feed')} className={styles.tab_button} style={leftPanel === 'activity_feed' ? {background:'#454254'} : {background:'transparent'}}>Activity Feed</button>
            </div>
            {agent.agent_type === 'Maintain Task Queue' && <div style={{marginLeft:'7px'}}>
              <button onClick={() => setLeftPanel('agent_type')} className={styles.tab_button} style={leftPanel === 'agent_type' ? {background:'#454254'} : {background:'transparent'}}>Task Queue</button>
            </div>}
          </div>
          <div style={{display:'flex'}}>
            <div>
              <button className={styles.run_button} onClick={() => setRunModal(true)}>
                <Image width={14} height={14} src="/images/run_icon.png" alt="run-icon"/>&nbsp;New Run
              </button>
            </div>
          </div>
        </div>
        <div className={styles.detail_body}>
          {leftPanel === 'activity_feed' && <ActivityFeed feeds={selectedRun.feeds} is_running={selectedRun.is_running}/>}
          {leftPanel === 'agent_type' && <TaskQueue tasks={selectedRun.tasks}/>}
        </div>
      </div>
      <div style={{width:'40%',height:'100%'}}>
        <div className={styles.detail_top}>
          <div style={{display:'flex',overflowX:'scroll'}}>
            <div>
              <button onClick={() => setRightPanel('action_console')} className={styles.tab_button} style={rightPanel === 'action_console' ? {background:'#454254'} : {background:'transparent'}}>
                Action Console
              </button>
            </div>
            {/*<div style={{marginLeft:'5px'}}>*/}
            {/*  <button onClick={() => setRightPanel('feedback')} className={styles.tab_button} style={rightPanel === 'feedback' ? {background:'#454254'} : {background:'transparent'}}>*/}
            {/*    Feedback*/}
            {/*  </button>*/}
            {/*</div>*/}
            <div style={{marginLeft:'5px'}}>
              <button onClick={() => setRightPanel('details')} className={styles.tab_button} style={rightPanel === 'details' ? {background:'#454254'} : {background:'transparent'}}>
                Details
              </button>
            </div>
            <div style={{marginLeft:'5px'}}>
              <button onClick={() => setRightPanel('resource_manager')} className={styles.tab_button} style={rightPanel === 'resource_manager' ? {background:'#454254'} : {background:'transparent'}}>
                Resource Manager
              </button>
            </div>
            {/*<div style={{marginLeft:'5px'}}>*/}
            {/*  <button onClick={() => setRightPanel('logs')} className={styles.tab_button} style={rightPanel === 'logs' ? {background:'#454254'} : {background:'transparent'}}>*/}
            {/*    Logs*/}
            {/*  </button>*/}
            {/*</div>*/}
          </div>
        </div>
        <div className={styles.detail_body} style={{paddingRight:'0'}}>
          {rightPanel === 'action_console' && <ActionConsole/>}
          {rightPanel === 'details' && <Details agent={agent}/>}
          {rightPanel === 'resource_manager' && <ResourceManager/>}
        </div>
      </div>

      {runModal && (<div className="modal" onClick={closeRunModal}>
        <div className="modal-content" style={{width: '35%'}} onClick={preventDefault}>
          <div className={styles.detail_name}>Run agent name</div>
          <div>
            <label className={styles.form_label}>Name</label>
            <input className="input_medium" type="text" value={runName} onChange={handleRunNameChange}/>
          </div>
          <div style={{marginTop: '15px'}}>
            <label className={styles.form_label}>Goals</label>
            {goals.map((goal, index) => (<div key={index} style={{marginBottom:'10px',display:'flex',alignItems:'center',justifyContent:'space-between'}}>
              <div style={{flex:'1'}}><input className="input_medium" type="text" value={goal} onChange={(event) => handleGoalChange(index, event.target.value)}/></div>
              <div>
                <button className={styles.agent_button} style={{marginLeft:'4px',padding:'5px'}} onClick={() => handleGoalDelete(index)}>
                  <Image width={20} height={21} src="/images/close_light.png" alt="close-icon"/>
                </button>
              </div>
            </div>))}
            <button className={styles.agent_button} onClick={addGoal}>+ Add</button>
          </div>
          <div style={{display: 'flex', justifyContent: 'flex-end'}}>
            <button className={styles.agent_button} style={{marginRight: '10px'}} onClick={closeRunModal}>
              Cancel
            </button>
            <button className={styles.run_button} style={{paddingLeft:'15px',paddingRight:'25px'}} onClick={() => handleCreateRun()}>
              <Image width={14} height={14} src="/images/run_icon.png" alt="run-icon"/>&nbsp;Run
            </button>
          </div>
        </div>
      </div>)}
    </div>
    <ToastContainer/>
  </>);
}
