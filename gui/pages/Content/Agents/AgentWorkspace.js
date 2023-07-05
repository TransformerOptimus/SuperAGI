import React, {useEffect, useState, useMemo} from 'react';
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
import {getAgentDetails, getAgentExecutions, updateExecution, addExecution, getExecutionDetails, saveAgentAsTemplate} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";

export default function AgentWorkspace({agentId, selectedView}) {
  const [leftPanel, setLeftPanel] = useState('activity_feed')
  const [rightPanel, setRightPanel] = useState('')
  const [history, setHistory] = useState(true)
  const [selectedRun, setSelectedRun] = useState(null)
  const [runModal, setRunModal] = useState(false)
  const [goals, setGoals] = useState(null)
  const [currentGoals, setCurrentGoals] = useState(null)
  const [runName, setRunName] = useState("New Run")
  const [agentDetails, setAgentDetails] = useState(null)
  const [agentExecutions, setAgentExecutions] = useState(null)
  const [dropdown, setDropdown] = useState(false);
  const [fetchedData, setFetchedData] = useState(null);
  const [instructions, setInstructions] = useState(['']);
  const [currentInstructions, setCurrentInstructions] = useState(['']);
  const [pendingPermission, setPendingPermissions] = useState(0)

  const pendingPermissions = useMemo(() => {
    if (!fetchedData) return 0;
    setPendingPermissions(fetchedData.filter(permission => permission.status === "PENDING").length);
  }, [fetchedData]);

  const addInstruction = () => {
    setInstructions((prevArray) => [...prevArray, 'new instructions']);
  };

  const handleInstructionDelete = (index) => {
    const updatedInstructions = [...instructions];
    updatedInstructions.splice(index, 1);
    setInstructions(updatedInstructions);
  };

  const handleInstructionChange = (index, newValue) => {
    const updatedInstructions = [...instructions];
    updatedInstructions[index] = newValue;
    setInstructions(updatedInstructions);
  };

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
      toast.error("Run name can't be blank", {autoClose: 1800});
      return
    }

    if (goals.length <= 0) {
      toast.error("Agent needs to have goals", {autoClose: 1800});
      return
    }

    const executionData = {
      "agent_id": agentId,
      "name": runName,
      "goal": goals,
      "instruction": instructions
    }

    addExecution(executionData)
        .then((response) => {
          setRunModal(false);
          fetchExecutions(agentId, response.data);
          fetchAgentDetails(agentId);
          EventBus.emit('reFetchAgents', {});
          toast.success("New run created", {autoClose: 1800});
        })
        .catch((error) => {
          console.error('Error creating execution:', error);
          toast.error("Could not create run", {autoClose: 1800});
        });
  };

  const closeRunModal = () => {
    setRunName("New Run");
    setRunModal(false);
  };

  const updateRunStatus = (status) => {
    const executionData = {"status": status};

    updateExecution(selectedRun.id, executionData)
        .then((response) => {
          EventBus.emit('updateRunStatus', {selectedRunId: selectedRun.id, status: status});
          if(status !== 'TERMINATED') {
            fetchExecutions(agentId, response.data);
          } else {
            fetchExecutions(agentId);
          }
          EventBus.emit('reFetchAgents', {});
        })
        .catch((error) => {
          console.error('Error updating execution:', error);
        });

    setDropdown(false);
  };

  const preventDefault = (e) => {
    e.stopPropagation();
  };

  useEffect(() => {
    fetchAgentDetails(agentId);
    fetchExecutions(agentId);
  }, [agentId])

  useEffect(() => {
    fetchExecutionDetails(selectedRun?.id);
  }, [selectedRun?.id])

  useEffect(() => {
    if(agentDetails) {
      setRightPanel(agentDetails.permission_type.includes('RESTRICTED') ? 'action_console' : 'details');
    }
  }, [agentDetails])

  function fetchAgentDetails(agentId) {
    getAgentDetails(agentId)
      .then((response) => {
        setAgentDetails(response.data);
      })
      .catch((error) => {
        console.error('Error fetching agent details:', error);
      });
  }

  function fetchExecutions(agentId, currentRun = null) {
    getAgentExecutions(agentId)
        .then((response) => {
          let data = response.data
          data = data.filter((run) => run.status !== 'TERMINATED');
          setAgentExecutions(data);
          setSelectedRun(currentRun ? currentRun : data[0]);
        })
        .catch((error) => {
          console.error('Error fetching agent executions:', error);
        });
  }

  function fetchExecutionDetails(executionId) {
    getExecutionDetails(executionId)
      .then((response) => {
        setGoals(response.data.goal);
        setCurrentGoals(response.data.goal);
        setInstructions(response.data.instruction);
        setCurrentInstructions(response.data.instruction);
      })
      .catch((error) => {
        console.error('Error fetching agent execution details:', error);
      });
  }

  function saveAgentTemplate() {
    saveAgentAsTemplate(agentId)
        .then((response) => {
          toast.success("Agent saved as template successfully", {autoClose: 1800});
        })
        .catch((error) => {
          console.error('Error saving agent as template:', error);
        });
  }

  useEffect(() => {
    const resetRunStatus = (eventData) => {
      if (eventData.executionId === selectedRun.id) {
        setSelectedRun((prevSelectedRun) => (
          { ...prevSelectedRun, status: eventData.status }
        ));
      }
    };

    EventBus.on('resetRunStatus', resetRunStatus);

    return () => {
      EventBus.off('resetRunStatus', resetRunStatus);
    };
  });

  return (<>
    <div style={{display:'flex'}}>
      {history  && selectedRun !== null && <RunHistory runs={agentExecutions} selectedRunId={selectedRun.id} setSelectedRun={setSelectedRun} setHistory={setHistory} setAgentExecutions={setAgentExecutions}/>}
      <div style={{width: history ? '40%' : '60%'}}>
        <div className={styles.detail_top}>
          <div style={{display:'flex'}}>
            {!history && selectedRun !== null && <div style={{display:'flex',alignItems:'center',cursor:'pointer',marginRight:'7px'}} onClick={() => setHistory(true)}>
              <div className={styles.run_history_button}><Image style={{marginTop:'-2px'}} width={16} height={16} src="/images/update.svg" alt="update-icon"/><span>&nbsp;Show run history</span>
              </div>
            </div>}
            <div style={{display:'flex',alignItems:'center',marginLeft:'2px'}} className={styles.tab_text}>
              {selectedRun && selectedRun.status === 'RUNNING' && <div style={{marginLeft:'-6px'}}><Image width={14} height={14} style={{mixBlendMode: 'exclusion'}} src="/images/loading.gif" alt="loading-icon"/></div>}
              <div className={styles.single_line_block} style={selectedRun && selectedRun.status === 'RUNNING' ? {marginLeft:'7px', maxWidth:'100px'} : {marginLeft:'-8px', maxWidth:'100px'}}>{selectedRun?.name || ''}</div>
            </div>
            <div style={{marginLeft:'7px'}}>
              <button onClick={() => setLeftPanel('activity_feed')} className={styles.tab_button} style={leftPanel === 'activity_feed' ? {background:'#454254'} : {background:'transparent'}}>Activity Feed</button>
            </div>
            {agentDetails && agentDetails.agent_type === 'Maintain Task Queue' && <div style={{marginLeft:'7px'}}>
              <button onClick={() => setLeftPanel('agent_type')} className={styles.tab_button} style={leftPanel === 'agent_type' ? {background:'#454254'} : {background:'transparent'}}>Task Queue</button>
            </div>}
          </div>
          <div style={{display:'flex'}}>
            <div>
              <button className={styles.run_button} onClick={() => setRunModal(true)}>
                <Image width={14} height={14} src="/images/run_icon.svg" alt="run-icon"/>&nbsp;New Run
              </button>
            </div>
            {<button className="secondary_button" style={{padding:'8px',height:'31px'}} onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
              <Image width={14} height={14} src="/images/three_dots.svg" alt="run-icon"/>
            </button>}
            {dropdown && <div onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
              <ul className="dropdown_container" style={{marginTop:'31px',marginLeft:'-32px'}}>
                <li className="dropdown_item" onClick={() => saveAgentTemplate()}>Save as Template</li>
                {selectedRun && selectedRun.status === 'RUNNING' && <li className="dropdown_item" onClick={() => {updateRunStatus("PAUSED")}}>Pause</li>}
                {selectedRun && (selectedRun.status === 'CREATED' || selectedRun.status === 'PAUSED') && <li className="dropdown_item" onClick={() => {updateRunStatus("RUNNING")}}>Resume</li>}
                {agentExecutions && agentExecutions.length > 1 && <li className="dropdown_item" onClick={() => {updateRunStatus("TERMINATED")}}>Delete</li>}
              </ul>
            </div>}
          </div>
        </div>
        <div className={styles.detail_body}>
          {leftPanel === 'activity_feed' && <div className={styles.detail_content}>
            <ActivityFeed runModal={runModal} selectedView={selectedView} selectedRunId={selectedRun?.id || 0} setFetchedData={setFetchedData}/>
          </div>}
          {leftPanel === 'agent_type' && <div className={styles.detail_content}><TaskQueue selectedRunId={selectedRun?.id || 0}/></div>}
        </div>
      </div>
      <div style={{width:'40%'}}>
        <div className={styles.detail_top}>
          <div style={{display:'flex',overflowX:'scroll'}}>
            {agentDetails && agentDetails.permission_type.includes('RESTRICTED') && <div>
              <button onClick={() => setRightPanel('action_console')} className={styles.tab_button} style={rightPanel === 'action_console' ? {background:'#454254'} : {background:'transparent'}}>
                <Image style={{marginTop:'-1px'}} width={14} height={14} src="/images/action_console.svg" alt="action-console-icon"/>&nbsp;Action Console &nbsp; {pendingPermission>0 && <span className={styles.notification_circle}>{pendingPermission}</span>}
              </button>
            </div>}
            {/*<div>*/}
            {/*  <button onClick={() => setRightPanel('feedback')} className={styles.tab_button} style={rightPanel === 'feedback' ? {background:'#454254'} : {background:'transparent'}}>*/}
            {/*    Feedback*/}
            {/*  </button>*/}
            {/*</div>*/}
            <div>
              <button onClick={() => setRightPanel('details')} className={styles.tab_button} style={rightPanel === 'details' ? {background:'#454254',paddingRight:'15px'} : {background:'transparent',paddingRight:'15px'}}>
                <Image width={14} height={14} src="/images/info.svg" alt="details-icon"/>&nbsp;Details
              </button>
            </div>
            <div>
              <button onClick={() => setRightPanel('resource_manager')} className={styles.tab_button} style={rightPanel === 'resource_manager' ? {background:'#454254',paddingRight:'15px'} : {background:'transparent',paddingRight:'15px'}}>
                <Image width={14} height={14} src="/images/home_storage.svg" alt="manager-icon"/>&nbsp;Resource Manager
              </button>
            </div>
            {/*<div>*/}
            {/*  <button onClick={() => setRightPanel('logs')} className={styles.tab_button} style={rightPanel === 'logs' ? {background:'#454254'} : {background:'transparent'}}>*/}
            {/*    Logs*/}
            {/*  </button>*/}
            {/*</div>*/}
          </div>
        </div>
        <div className={styles.detail_body} style={{paddingRight:'0'}}>
          {rightPanel === 'action_console' && agentDetails && agentDetails?.permission_type !== 'God Mode' && (
              <div className={styles.detail_content}>
                <ActionConsole key={JSON.stringify(fetchedData)} actions={fetchedData} pendingPermission={pendingPermission} setPendingPermissions={setPendingPermissions}/>
              </div>
          )}
          {rightPanel === 'details' && <div className={styles.detail_content}><Details agentDetails={agentDetails} goals={currentGoals} instructions={currentInstructions} runCount={agentExecutions?.length || 0}/></div>}
          {rightPanel === 'resource_manager' && <div className={styles.detail_content}><ResourceManager agentId={agentId}/></div>}
        </div>
      </div>

      {runModal && (<div className="modal" onClick={closeRunModal}>
        <div className="modal-content" style={{width: '35%'}} onClick={preventDefault}>
          <div className={styles.detail_name}>Run agent name</div>
          <div>
            <label className={styles.form_label}>Name</label>
            <input className="input_medium" type="text" value={runName} onChange={handleRunNameChange}/>
          </div>
          {goals && goals.length > 0 && <div style={{marginTop: '15px'}}>
            <div><label className={styles.form_label}>Goals</label></div>
            {goals.map((goal, index) => (<div key={index} style={{marginBottom:'10px',display:'flex',alignItems:'center',justifyContent:'space-between'}}>
              <div style={{flex:'1'}}><input className="input_medium" type="text" value={goal} onChange={(event) => handleGoalChange(index, event.target.value)}/></div>
              {goals.length > 1 && <div>
                <button className="secondary_button" style={{marginLeft: '4px', padding: '5px'}}
                        onClick={() => handleGoalDelete(index)}>
                  <Image width={20} height={21} src="/images/close_light.svg" alt="close-icon"/>
                </button>
              </div>}
            </div>))}
            <div><button className="secondary_button" onClick={addGoal}>+ Add</button></div>
          </div>}
          <div style={{marginTop: '15px'}}>
            <div><label className={styles.form_label}>Instructions<span style={{fontSize:'9px'}}>&nbsp;(optional)</span></label></div>
            {instructions.map((goal, index) => (<div key={index} style={{marginBottom: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
              <div style={{flex: '1'}}><input className="input_medium" type="text" value={goal} onChange={(event) => handleInstructionChange(index, event.target.value)}/>
              </div>{instructions.length > 1 && <div>
              <button className="secondary_button" style={{marginLeft: '4px', padding: '5px'}} onClick={() => handleInstructionDelete(index)}>
                <Image width={20} height={21} src="/images/close_light.svg" alt="close-icon"/>
              </button>
            </div>}
            </div>))}
            <div>
              <button className="secondary_button" onClick={addInstruction}>+ Add</button>
            </div>
          </div>
          <div style={{display: 'flex', justifyContent: 'flex-end'}}>
            <button className="secondary_button" style={{marginRight: '10px'}} onClick={closeRunModal}>
              Cancel
            </button>
            <button className={styles.run_button} style={{paddingLeft:'15px',paddingRight:'25px'}} onClick={() => handleCreateRun()}>
              <Image width={14} height={14} src="/images/run_icon.svg" alt="run-icon"/>&nbsp;Run
            </button>
          </div>
        </div>
      </div>)}
    </div>
    <ToastContainer/>
  </>);
}
