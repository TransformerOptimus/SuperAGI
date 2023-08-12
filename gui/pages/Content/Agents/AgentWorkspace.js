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
import {createInternalId, preventDefault} from "@/utils/utils";
import {
  getAgentDetails,
  getAgentExecutions,
  updateExecution,
  addExecution,
  getExecutionDetails,
  saveAgentAsTemplate,
  stopSchedule,
  getDateTime,
  deleteAgent
} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import 'moment-timezone';
import AgentSchedule from "@/pages/Content/Agents/AgentSchedule";

export default function AgentWorkspace({env, agentId, agentName, selectedView, agents, internalId, sendAgentData}) {
  const [leftPanel, setLeftPanel] = useState('activity_feed')
  const [rightPanel, setRightPanel] = useState('details')
  const [history, setHistory] = useState(true)
  const [selectedRun, setSelectedRun] = useState(null)
  const [runModal, setRunModal] = useState(false)
  const [deleteModal, setDeleteModal] = useState(false)
  const [goals, setGoals] = useState(null)
  const [currentGoals, setCurrentGoals] = useState(null)
  const [runName, setRunName] = useState("New Run")
  const [agentDetails, setAgentDetails] = useState(null)
  const [agentExecutions, setAgentExecutions] = useState(null)
  const [dropdown, setDropdown] = useState(false);
  const [fetchedData, setFetchedData] = useState(null);
  const [instructions, setInstructions] = useState(['']);
  const [currentInstructions, setCurrentInstructions] = useState(['']);
  const [pendingPermission, setPendingPermissions] = useState(0);

  const agent = agents.find(agent => agent.id === agentId);

  const [createModal, setCreateModal] = useState(false);
  const [createEditModal, setCreateEditModal] = useState(false);
  const [createStopModal, setCreateStopModal] = useState(false);
  const [agentScheduleDetails, setAgentScheduleDetails] = useState(null)

  const closeCreateModal = () => {
    setCreateModal(false);
    setCreateEditModal(false);
    setCreateStopModal(false);
  };

  const handleEditScheduleClick = () => {
    setCreateEditModal(true);
    setDropdown(false);
  };

  const handleStopScheduleClick = () => {
    setCreateStopModal(true);
    setCreateModal(false);
    setDropdown(false);
  };

  function fetchStopSchedule() {//Stop Schedule
    stopSchedule(agentId)
      .then((response) => {
        if (response.status === 200) {
          toast.success('Schedule stopped successfully!', {autoClose: 1800});
          setCreateStopModal(false);
          EventBus.emit('reFetchAgents', {});
          setAgentScheduleDetails(null)
        }
      })
      .catch((error) => {
        console.error('Error stopping agent schedule:', error);
      });
  };

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
    setGoals(goals.length< 0 ? agentDetails.goal : goals)
    setInstructions(instructions.length < 0 ? agentDetails.instruction : instructions)

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
        fetchAgentDetails(agentId, selectedRun?.id);
        EventBus.emit('reFetchAgents', {});
        toast.success("New run created", {autoClose: 1800});
      })
      .catch((error) => {
        console.error('Error creating execution:', error);
        toast.error("Could not create run", {autoClose: 1800});
      });
  };

  const handleDeleteAgent = () => {
    deleteAgent(agentId)
      .then((response) => {
        setDeleteModal(false);
        if (response.status === 200) {
          EventBus.emit('reFetchAgents', {});
          EventBus.emit('removeTab', {
            element: {
              id: agentId,
              name: agentName,
              contentType: "Agents",
              internalId: internalId
            }
          })
          toast.success("Agent Deleted Successfully", {autoClose: 1800});
        } else {
          toast.error("Agent Could not be Deleted", {autoClose: 1800});
        }
      })
      .catch((error) => {
        setDeleteModal(false);
        toast.error("Agent Could not be Deleted", {autoClose: 1800});
        console.error("Agent could not be deleted: ", error);
      });
  }
  const closeRunModal = () => {
    setRunName("New Run");
    setRunModal(false);
  };

  const closeDeleteModal = () => {
    setDeleteModal(false);
  }

  const updateRunStatus = (status) => {
    const executionData = {"status": status};

    updateExecution(selectedRun.id, executionData)
      .then((response) => {
        EventBus.emit('updateRunStatus', {selectedRunId: selectedRun.id, status: status});
        if (status !== 'TERMINATED') {
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

  useEffect(() => {
    fetchAgentDetails(agentId, selectedRun?.id);
    fetchExecutions(agentId);
    fetchAgentScheduleComponent()
  }, [agentId])

  useEffect(() => {
    // fetchExecutionDetails(selectedRun?.id);
    fetchAgentDetails(agentId, selectedRun?.id);
  }, [selectedRun?.id])

  useEffect(() => {
    if (agentDetails) {
      setRightPanel(agentDetails.permission_type === 'RESTRICTED' ? 'action_console' : 'details');
    }
  }, [agentDetails])

  function setNewRunDetails() {
    getAgentDetails(agentId,  -1)
      .then((response) => {
        setGoals(response.data.goal)
        setInstructions(response.data.instruction)
        setRunModal(true);
      })
      .catch((error) => {
        console.error('Error fetching agent details:', error);
      });
  }

  function fetchAgentDetails(agentId, runId) {
    getAgentDetails(agentId, runId ? runId : -1)
      .then((response) => {
        const data = response.data
        setAgentDetails(data);
      })
      .catch((error) => {
        console.error('Error fetching agent details:', error);
      });
  }

  function fetchAgentScheduleComponent() {
    if (agent?.is_scheduled) {
      getDateTime(agentId)
        .then((response) => {
          setAgentScheduleDetails(response.data)
        })
        .catch((error) => {
          console.error('Error fetching agent data:', error);
        });
    }
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

  // function fetchExecutionDetails(executionId) {
  //   getExecutionDetails(executionId || -1, agentId)
  //     .then((response) => {
  //       setGoals(response.data.goal);
  //       setCurrentGoals(response.data.goal);
  //       setInstructions(response.data.instruction);
  //       setCurrentInstructions(response.data.instruction);
  //     })
  //     .catch((error) => {
  //       console.error('Error fetching agent execution details:', error);
  //     });
  // }

  function saveAgentTemplate() {
    saveAgentAsTemplate(selectedRun?.id)
      .then((response) => {
        toast.success("Agent saved as template successfully", {autoClose: 1800});
      })
      .catch((error) => {
        console.error('Error saving agent as template:', error);
      });

    setDropdown(false);
  }

  useEffect(() => {
    const resetRunStatus = (eventData) => {
      if (eventData.executionId === selectedRun.id) {
        setSelectedRun((prevSelectedRun) => (
          {...prevSelectedRun, status: eventData.status}
        ));
      }
    };

    const refreshDate = () => {
      fetchAgentScheduleComponent()
    };

    EventBus.on('resetRunStatus', resetRunStatus);
    EventBus.on('refreshDate', refreshDate);

    return () => {
      EventBus.off('resetRunStatus', resetRunStatus);
      EventBus.off('refreshDate', refreshDate);
    };
  });

  return (<>
    <div style={{display: 'flex'}}>
      {history && selectedRun !== null &&
        <RunHistory runs={agentExecutions} selectedRunId={selectedRun?.id} setSelectedRun={setSelectedRun}
                    setHistory={setHistory} setAgentExecutions={setAgentExecutions}/>}
      <div style={{width: history ? '40%' : '60%'}}>
        <div className={styles.detail_top}>
          <div style={{display: 'flex'}}>
            {!history && selectedRun !== null &&
              <div style={{display: 'flex', alignItems: 'center', cursor: 'pointer', marginRight: '7px'}}
                   onClick={() => setHistory(true)}>
                <div className={styles.run_history_button}><Image style={{marginTop: '-2px'}} width={16} height={16}
                                                                  src="/images/update.svg"
                                                                  alt="update-icon"/><span>&nbsp;Show run history</span>
                </div>
              </div>}
            <div style={{display: 'flex', alignItems: 'center', marginLeft: '2px'}} className={styles.tab_text}>
              {selectedRun && selectedRun.status === 'RUNNING' &&
                <div style={{marginLeft: '-6px'}}><Image width={14} height={14} style={{mixBlendMode: 'exclusion'}}
                                                         src="/images/loading.gif" alt="loading-icon"/></div>}
              <div className={styles.single_line_block} style={selectedRun && selectedRun.status === 'RUNNING' ? {
                marginLeft: '7px',
                maxWidth: '100px'
              } : {marginLeft: '-8px', maxWidth: '100px'}}>{selectedRun?.name || ''}</div>
            </div>
            <div style={{marginLeft: '7px'}}>
              <button onClick={() => setLeftPanel('activity_feed')} className={styles.tab_button}
                      style={leftPanel === 'activity_feed' ? {background: '#454254'} : {background: 'transparent'}}>Activity
                Feed
              </button>
            </div>
            {agentDetails && (agentDetails.agent_workflow === 'Dynamic Task Workflow' || agentDetails.agent_workflow === "Fixed Task Workflow") &&
              <div style={{marginLeft: '7px'}}>
                <button onClick={() => setLeftPanel('agent_workflow')} className={styles.tab_button}
                        style={leftPanel === 'agent_workflow' ? {background: '#454254'} : {background: 'transparent'}}>Task
                  Queue
                </button>
              </div>}
          </div>
          <div style={{display: 'flex'}}>
            <div>
              <button className={styles.run_button} onClick={setNewRunDetails}>
                <Image width={14} height={14} src="/images/run_icon.svg" alt="run-icon"/>&nbsp;New Run
              </button>
            </div>
            <button className="secondary_button" style={{padding: '8px', height: '31px'}}
                    onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
              <Image width={14} height={14} src="/images/three_dots.svg" alt="run-icon"/>
            </button>
            {dropdown && <div onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
              <ul className="dropdown_container" style={{marginTop: '31px', marginLeft: '-32px'}}>
                <li className="dropdown_item" onClick={() => saveAgentTemplate()}>Save as Template</li>
                {selectedRun && selectedRun.status === 'RUNNING' && <li className="dropdown_item" onClick={() => {
                  updateRunStatus("PAUSED")
                }}>Pause</li>}
                {selectedRun && (selectedRun.status === 'CREATED' || selectedRun.status === 'PAUSED') &&
                  <li className="dropdown_item" onClick={() => {
                    updateRunStatus("RUNNING")
                  }}>Resume</li>}
                {agentExecutions && agentExecutions.length > 1 && <li className="dropdown_item" onClick={() => {
                  updateRunStatus("TERMINATED")
                }}>Delete Run</li>}

                {agent?.is_scheduled ? (<div>
                  <li className="dropdown_item" onClick={handleEditScheduleClick}>Edit Schedule</li>
                  <li className="dropdown_item" onClick={handleStopScheduleClick}>Stop Schedule</li>
                </div>) : (<div>
                  {agent && !agent?.is_running && !agent?.is_scheduled &&
                    <li className="dropdown_item" onClick={() => {
                      setDropdown(false);
                      setCreateModal(true)
                    }}>Schedule Run</li>}
                </div>)}
                <li className="dropdown_item" onClick={() => sendAgentData({
                  id: agentId,
                  name: "Edit Agent",
                  contentType: "Edit_Agent",
                  internalId: createInternalId()
                })}>Edit Agent</li>
                <li className="dropdown_item" onClick={() => {
                  setDropdown(false);
                  setDeleteModal(true)
                }}>Delete Agent
                </li>
              </ul>
            </div>}

            {createModal &&
              <AgentSchedule env={env} internalId={internalId} closeCreateModal={closeCreateModal} type="schedule_agent"
                             agentId={agentId} setCreateModal={() => setCreateModal(false)}/>}
            {createEditModal &&
              <AgentSchedule env={env} internalId={internalId} closeCreateModal={closeCreateModal}
                             type="edit_schedule_agent"
                             agentId={agentId} setCreateEditModal={() => setCreateEditModal(false)}/>}
            {createStopModal && (
              <div className="modal" onClick={closeCreateModal}>
                <div className="modal-content" style={{width: '35%'}} onClick={preventDefault}>
                  <div className={styles.detail_name}>Stop Schedule</div>
                  <label className={styles.form_label}>All further schedules of this agent will be stopped. Are you sure
                    you want to proceed?</label>
                  <div style={{display: 'flex', justifyContent: 'flex-end', marginTop: '20px'}}>
                    <button className="secondary_button" style={{marginRight: '10px'}} onClick={closeCreateModal}>
                      Cancel
                    </button>
                    <button className={styles.run_button} style={{paddingLeft: '15px', paddingRight: '25px'}}
                            onClick={fetchStopSchedule}>
                      Stop Schedule
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
        <div className={styles.detail_body}>
          {leftPanel === 'activity_feed' && <div className={styles.detail_content}>
            <ActivityFeed selectedView={selectedView} selectedRunId={selectedRun?.id || null}
                          setFetchedData={setFetchedData} agent={agent}/>
          </div>}
          {leftPanel === 'agent_workflow' &&
            <div className={styles.detail_content}><TaskQueue selectedRunId={selectedRun?.id || 0}/></div>}
        </div>
      </div>
      <div style={{width: '40%'}}>
        <div className={styles.detail_top}>
          <div style={{display: 'flex', overflowX: 'scroll'}}>
            {agentDetails && ((fetchedData && fetchedData.length > 0) || agentDetails.permission_type === 'RESTRICTED') && <div>
              <button onClick={() => setRightPanel('action_console')} className={styles.tab_button}
                      style={rightPanel === 'action_console' ? {background: '#454254'} : {background: 'transparent'}}>
                <Image style={{marginTop: '-1px'}} width={14} height={14} src="/images/action_console.svg"
                       alt="action-console-icon"/>&nbsp;Action Console &nbsp; {pendingPermission > 0 &&
                <span className={styles.notification_circle}>{pendingPermission}</span>}
              </button>
            </div>}
            {/*<div>*/}
            {/*  <button onClick={() => setRightPanel('feedback')} className={styles.tab_button} style={rightPanel === 'feedback' ? {background:'#454254'} : {background:'transparent'}}>*/}
            {/*    Feedback*/}
            {/*  </button>*/}
            {/*</div>*/}
            <div>
              <button onClick={() => setRightPanel('details')} className={styles.tab_button}
                      style={rightPanel === 'details' ? {
                        background: '#454254',
                        paddingRight: '15px'
                      } : {background: 'transparent', paddingRight: '15px'}}>
                <Image width={14} height={14} src="/images/info.svg" alt="details-icon"/>&nbsp;Details
              </button>
            </div>
            <div>
              <button onClick={() => setRightPanel('resource_manager')} className={styles.tab_button}
                      style={rightPanel === 'resource_manager' ? {
                        background: '#454254',
                        paddingRight: '15px'
                      } : {background: 'transparent', paddingRight: '15px'}}>
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
        <div className={styles.detail_body} style={{paddingRight: '0'}}>
          {rightPanel === 'action_console' && agentDetails && (
            <div className={styles.detail_content}>
              <ActionConsole key={JSON.stringify(fetchedData)} actions={fetchedData}
                             pendingPermission={pendingPermission} setPendingPermissions={setPendingPermissions}/>
            </div>
          )}
          {rightPanel === 'details' && agentDetails && agentDetails !== null &&
            <div className={styles.detail_content}><Details agentDetails1={agentDetails}
                                                            runCount={agentExecutions?.length || 0}
                                                            agentScheduleDetails={agentScheduleDetails} agent={agent}/>
            </div>}
          {rightPanel === 'resource_manager' &&
            <div className={styles.detail_content}><ResourceManager agentId={agentId} runs={agentExecutions}/></div>}
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
            {goals.map((goal, index) => (<div key={index} style={{
              marginBottom: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <div style={{flex: '1'}}><input className="input_medium" type="text" value={goal}
                                              onChange={(event) => handleGoalChange(index, event.target.value)}/></div>
              {goals.length > 1 && <div>
                <button className="secondary_button" style={{marginLeft: '4px', padding: '5px'}}
                        onClick={() => handleGoalDelete(index)}>
                  <Image width={20} height={21} src="/images/close.svg" alt="close-icon"/>
                </button>
              </div>}
            </div>))}
            <div>
              <button className="secondary_button" onClick={addGoal}>+ Add</button>
            </div>
          </div>}
          <div style={{marginTop: '15px'}}>
            <div><label className={styles.form_label}>Instructions<span
              style={{fontSize: '9px'}}>&nbsp;(optional)</span></label></div>
            {instructions.map((goal, index) => (<div key={index} style={{
              marginBottom: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <div style={{flex: '1'}}><input className="input_medium" type="text" value={goal}
                                              onChange={(event) => handleInstructionChange(index, event.target.value)}/>
              </div>
              {instructions.length > 1 && <div>
                <button className="secondary_button" style={{marginLeft: '4px', padding: '5px'}}
                        onClick={() => handleInstructionDelete(index)}>
                  <Image width={20} height={21} src="/images/close.svg" alt="close-icon"/>
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
            <button className={styles.run_button} style={{paddingLeft: '15px', paddingRight: '25px'}}
                    onClick={() => handleCreateRun()}>
              <Image width={14} height={14} src="/images/run_icon.svg" alt="run-icon"/>&nbsp;Run
            </button>
          </div>
        </div>
      </div>)}

      {deleteModal && (<div className="modal" onClick={closeDeleteModal}>
        <div className="modal-content" style={{width: '502px', padding: '16px', gap: '24px'}} onClick={preventDefault}>
          <div>
            <label className={styles.delete_agent_modal_label}>Delete Agent</label>
          </div>
          <div>
            <label className={styles.delete_modal_text}>All the runs and details of this agent will be deleted. Are you
              sure you want to proceed?</label>
          </div>
          <div style={{display: 'flex', justifyContent: 'flex-end'}}>
            <button className="secondary_button" style={{marginRight: '10px'}} onClick={closeDeleteModal}>
              Cancel
            </button>
            <button className="primary_button" onClick={() => handleDeleteAgent()}>
              Delete Agent
            </button>
          </div>
        </div>
      </div>)}

    </div>
    <ToastContainer/>
  </>);
}