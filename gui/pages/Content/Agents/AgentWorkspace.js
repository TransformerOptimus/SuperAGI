import React, {useEffect, useState, useMemo, useRef} from 'react';
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
import {getAgentDetails, getAgentExecutions, updateExecution, addExecution, updateAgents, saveAgentAsTemplate} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import axios from 'axios';

import Datetime from "react-datetime";
import "react-datetime/css/react-datetime.css";
import moment from 'moment';
import 'moment-timezone';

export default function AgentWorkspace({agentId, selectedView}) {
  const [leftPanel, setLeftPanel] = useState('activity_feed')
  const [rightPanel, setRightPanel] = useState('')
  const [history, setHistory] = useState(true)
  const [selectedRun, setSelectedRun] = useState(null)
  const [runModal, setRunModal] = useState(false)
  const [goals, setGoals] = useState(null)
  const [tools, setTools] = useState([])
  const [runName, setRunName] = useState("New Run")
  const [agentDetails, setAgentDetails] = useState(null)
  const [agentExecutions, setAgentExecutions] = useState(null)
  const [dropdown, setDropdown] = useState(false);
  const [fetchedData, setFetchedData] = useState(null);
  const [instructions, setInstructions] = useState(['']);
  const [pendingPermission, setPendingPermissions] = useState(0);



  const [timeValue, setTimeValue] = useState(null);
  const [expiryRuns, setExpiryRuns] = useState(null);
  const [createDropdown, setCreateDropdown] = useState(false);	
  const [createModal, setCreateModal] = useState(false);	
  const [createEditModal , setCreateEditModal] = useState(false);	
  const [createStopModal, setCreateStopModal] = useState(false);
  const [isRecurring, setIsRecurring] = useState(false);	
  const [timeDropdown, setTimeDropdown] = useState(false);	
  const [expiryDropdown, setExpiryDropdown] = useState(false);	
  // const [selectedDateTime, setSelectedDateTime] = useState(null);	
  // const [selectedTime, setSelectedTime] = useState(null);	
  // const [gmtDateTime, setgmtDateTime] = useState(null);	
  // const [gmtTime, setGmtTime] = useState(null);	
  const timeUnitArray = ['Days', 'Hours', 'Minutes']
  const expiryArray = ['Specific Date', 'After certain number of runs', 'No expiry']
 
  const [expiry, setExpiry] = useState(expiryArray[1]);
  const timeRef = useRef(null);	
  const expiryRef = useRef(null);
  const [startTime, setStartTime] = useState('');
  const [timeUnit, setTimeUnit] = useState(timeUnitArray[1]);
  const [expiryDate, setExpiryDate] = useState(null);

  const handleTimeChange = (momentObj) => {	
    const startTime = convertToGMT(momentObj);
    setLocalStorageValue("agent_start_time_" + String(internalId), startTime, setStartTime);
  };
  const handleDateChange = (event) => {	
    setLocalStorageValue("agent_time_value_" + String(internalId), event.target.value, setTimeValue);
  };
  const handleTimeSelect = (index) => {
    setLocalStorageValue("agent_time_unit_" + String(internalId), timeUnitArray[index], setTimeUnit);
    setTimeDropdown(false);	
  };
  const handleDateTimeChange = (momentObj) => {	
    const expiryDate = convertToGMT(momentObj);
    setLocalStorageValue("agent_expiry_date_" + String(internalId), expiryDate, setExpiryDate);
  };
  const handleExpiryRuns = (event) => {	
    setLocalStorageValue("agent_expiry_runs_" + String(internalId), event.target.value, setExpiryRuns);
  };

  const toggleRecurring = () => {	
    setIsRecurring(!isRecurring);	
  };
  const closeCreateModal = () => {	
    setCreateModal(false);
    setCreateEditModal(false);	
    setCreateStopModal(false);
  };
  const handleExpirySelect = (index) => {	
    setExpiry(expiryArray[index]);	
    setExpiryDropdown(false);	
  }

  useEffect(() => {
    const agent_start_time = localStorage.getItem("agent_start_time_" + String(internalId));
    if(agent_start_time) {
      setStartTime(agent_start_time);
    }
    const agent_time_value = localStorage.getItem("agent_time_value_" + String(internalId));
    if(agent_time_value) {
      setTimeValue(Number(agent_time_value));
    }
    const agent_time_unit = localStorage.getItem("agent_time_unit_" + String(internalId));
    if(agent_time_unit) {
      setTimeUnit(agent_time_unit);
    }
    const agent_expiry_date = localStorage.getItem("agent_expiry_date_" + String(internalId));
    if(agent_expiry_date) {
      setExpiryDate(agent_expiry_date);
    }
    const agent_expiry_runs = localStorage.getItem("agent_expiry_runs_" + String(internalId));
    if(agent_expiry_runs) {
      setExpiryRuns(Number(agent_expiry_runs));
    }
  },[internalId])

  const stopSchedule = () => {
    const apiUrl = `http://192.168.1.170:3000/api/agents/stop/schedule?agent_id=${agentId}`;
    axios.post(apiUrl)
      .then((response) => {
        if (response.status === 200) {
          toast.success('Schedule stopped successfully!');
        }
      })
      .catch((error) => {
        console.error('Error stopping agent schedule:', error);
      });
  };

  const createAndScheduleRun = () => {//schedule existing data
    const requestData = {
      "agent_id": agentId,
      "start_time": startTime,
      "recurrence_interval": timeValue? `${timeValue} ${timeUnit}` : null,
      "expiry_runs":expiryRuns,
      "expiry_date":expiryDate,
    };
    console.log("start_time", "recurrence_interval", "expiry_runs","expiry_date");
    axios.post('http://192.168.1.170:3000/api/agentexecutions/schedule', requestData)
      .then(response => {
        const { schedule_id } = response.data;
        console.log('Schedule ID:', schedule_id);
      })
      .catch(error => {
        console.error('Error:', error);
      });
  };

  const AgentScheduleComponent = () => {
    const [agentData, setAgentData] = useState(null);//get agent data
  
    useEffect(() => {
      const agentId = 2; 
      const apiUrl = ``;
  //{{localhost}}/agents/get/schedule_data/${agentId}
      axios.get(apiUrl)
        .then((response) => {
          setAgentData(response.data);
        })
        .catch((error) => {
          console.error('Error fetching agent data:', error);
        });
    }, []);
  }

  const handleUpdateSchedule = () => {//update agent data
    const agentId = 2; 
    const apiUrl = ``;

    const requestData = {
      "agent_id": agentId,
      "start_time": agentData.current_datetime,
      "recurrence_interval": agentData.recurrence_interval,
      "expiry_runs": agentData.expiry_runs,
      "expiry_date": agentData.expiry_date,
    };

    axios.post(apiUrl, requestData)
      .then((response) => {
        toast.error('Schedule updated successfully');
      })
      .catch((error) => {
        console.error('Error updating agent schedule:', error);
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

    if (goals.length <= 0) {
      toast.error("Agent needs to have goals", {autoClose: 1800});
      return
    }

    const executionData = { "agent_id": agentId, "name": runName }
    const agentData = { "agent_id": agentId, "key": "goal", "value": goals}
    const agentData1 = { "agent_id": agentId, "key": "instruction", "value": instructions}

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

    updateAgents(agentData)
        .then((response) => {
          EventBus.emit('reFetchAgents', {});
        })
        .catch((error) => {
          console.error('Error updating agent:', error);
        });

    updateAgents(agentData1)
        .then((response) => {
          EventBus.emit('reFetchAgents', {});
        })
        .catch((error) => {
          console.error('Error updating agent:', error);
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
    console.log(agentDetails)
    fetchAgentDetails(agentId);
    fetchExecutions(agentId);
  }, [agentId])

  useEffect(() => {
    if(agentDetails) {
      setRightPanel(agentDetails.permission_type.includes('RESTRICTED') ? 'action_console' : 'details');
    }
  }, [agentDetails])

  function fetchAgentDetails(agentId) {
    getAgentDetails(agentId)
      .then((response) => {
        setAgentDetails(response.data);
        setTools(response.data.tools);
        setGoals(response.data.goal);
        setInstructions(response.data.instruction);
      })
      .catch((error) => {
        console.error('Error fetching agent details:', error);
      });
  }

  function fetchExecutions(agentId, currentRun = null){
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
      {history  && selectedRun !== null && <RunHistory runs={agentExecutions} selectedRunId={selectedRun?.id} setSelectedRun={setSelectedRun} setHistory={setHistory} setAgentExecutions={setAgentExecutions}/>}
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
                <li className="dropdown_item" onClick={() => setCreateModal(true)}>Schedule Run</li>     
                <li className="dropdown_item" onClick={() => {setCreateEditModal(true);AgentScheduleComponent;}}>Edit Schedule</li>
                <li className="dropdown_item" onClick={() => setCreateStopModal(true)}>Stop Schedule</li>
              </ul>
            </div>}


            {createModal && (
            <div className="modal" onClick={closeCreateModal}>
            <div className="modal-content" style={{width: '35%'}} onClick={preventDefault}>
            <div className={styles.detail_name}>Schedule Run</div>

            <div style={{marginBottom:'20px'}}>
              <label className={styles.form_label}>Select a date and time</label>
              <div >
              <Datetime className={styles.rdtPicker} onChange={handleTimeChange} inputProps={{ placeholder: 'Enter here' }}/>
              </div>          
            </div>
             
            <div style={{marginBottom:'20px', display:'flex'}}>
            <input type="checkbox" className="checkbox" checked={isRecurring} onChange={toggleRecurring} style={{ marginRight: '5px'}}/>
            <label className={styles.form_label}>Recurring run</label>
            </div>

            {isRecurring && (<div>
            <div style={{color:"white", marginBottom:'20px'}}>Recurring run details</div>
            <label className={styles.form_label}>Repeat every</label>

            <div style={{display:'flex',marginBottom:'20px'}}>
              <div style={{width:'70%', marginRight:'5px'}}>
                <input className="input_medium" type="text" value={timeValue} onChange={handleDateChange} placeholder='Enter here'/>
              </div>
              <div style={{width:'30%'}} >
                <div className="custom_select_container" onClick={() => setTimeDropdown(!timeDropdown)} style={{width:'100%'}}>
                {timeUnit}<Image width={20} height={21} src={!timeDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'} alt="expand-icon"/>
                </div>
                <div>
                {timeDropdown && <div className="custom_select_options" ref={timeRef} style={{width:'30%'}}>
                {timeUnitArray.map((timeUnit, index) => (<div key={index} className="custom_select_option" onClick={() => handleTimeSelect(index)} style={{padding:'12px 14px',maxWidth:'100%'}}>
                  {timeUnit}
                </div>))}
                </div>} 
                </div>
              </div>
            </div>

            <label className={styles.form_label}>Recurring expiry</label>
            <div>
            <div style={{display:'inline'}}>
              <div style={{width:'100%', marginRight:'5px'}}>
              <div className="custom_select_container" onClick={() => setExpiryDropdown(!expiryDropdown)} style={{width:'100%'}}>
                {expiry}<Image width={20} height={21} src={!expiryDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'} alt="expand-icon"/>
              </div>
              <div>
                {expiryDropdown && <div className="custom_select_options" ref={expiryRef} style={{width:'30%'}}>
                {expiryArray.map((expiry, index) => (<div key={index} className="custom_select_option" onClick={() => handleExpirySelect(index)} style={{padding:'12px 14px',maxWidth:'100%'}}>
                  {expiry}
                </div>))}
                </div>} 
              </div>
              </div>
              {expiry==='After certain number of runs' && (
                <div style={{width:'100%', marginTop:'10px'}}>
                  <input className="input_medium" type="text" value={expiryRuns} onChange={handleExpiryRuns} placeholder="Enter the number of runs" />
                </div>
              )}
              {expiry==='Specific Date' && (
                <div style={{width:'100%', marginTop:'10px'}}>
                  {/* <input className="input_medium" type="text" placeholder="Select the date" /> */}
                  <Datetime timeFormat={false} className={styles.rdtPicker} onChange={handleDateTimeChange} inputProps={{ placeholder: 'Enter here' }}/>
                </div>
              )}
            </div>
            </div>
            </div>)}
            <div style={{display: 'flex', justifyContent: 'flex-end',marginTop: '20px'}}>
              <button className="secondary_button" style={{marginRight: '10px'}} onClick={closeCreateModal}>
                Cancel
              </button>
              <button className={styles.run_button} style={{paddingLeft:'15px',paddingRight:'25px'}} onClick={createAndScheduleRun}>
                Create and Schedule Run
              </button>
            </div>
          </div>
        </div>)}


            {createEditModal && (
            <div className="modal" onClick={closeCreateModal}>
            <div className="modal-content" style={{width: '35%'}} onClick={preventDefault}>
            <div className={styles.detail_name}>Edit Schedule</div>

            <div style={{marginBottom:'20px'}}>
              <label className={styles.form_label}>Select a date and time</label>
              <div >
              <Datetime className={styles.rdtPicker} onChange={handleTimeChange} inputProps={{ placeholder: 'Enter here' }}/>
              </div>          
            </div>
             
            <div style={{marginBottom:'20px', display:'flex'}}>
            <input type="checkbox" className="checkbox" checked={isRecurring} onChange={toggleRecurring} style={{ marginRight: '5px'}}/>
            <label className={styles.form_label}>Recurring run</label>
            </div>

            {isRecurring && (<div>
            <div style={{color:"white", marginBottom:'20px'}}>Recurring run details</div>
            <label className={styles.form_label}>Repeat every</label>

            <div style={{display:'flex',marginBottom:'20px'}}>
              <div style={{width:'70%', marginRight:'5px'}}>
                <input className="input_medium" type="text" value={timeValue} onChange={handleDateChange} placeholder='Enter here'/>
              </div>
              <div style={{width:'30%'}} >
                <div className="custom_select_container" onClick={() => setTimeDropdown(!timeDropdown)} style={{width:'100%'}}>
                {timeUnit}<Image width={20} height={21} src={!timeDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'} alt="expand-icon"/>
                </div>
                <div>
                {timeDropdown && <div className="custom_select_options" ref={timeRef} style={{width:'30%'}}>
                {timeUnitArray.map((timeUnit, index) => (<div key={index} className="custom_select_option" onClick={() => handleTimeSelect(index)} style={{padding:'12px 14px',maxWidth:'100%'}}>
                  {timeUnit}
                </div>))}
                </div>} 
                </div>
              </div>
              </div>

            <label className={styles.form_label}>Recurring expiry</label>
            <div>
            <div style={{display:'inline'}}>
              <div style={{width:'100%', marginRight:'5px'}}>
              <div className="custom_select_container" onClick={() => setExpiryDropdown(!expiryDropdown)} style={{width:'100%'}}>
                {expiry}<Image width={20} height={21} src={!expiryDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'} alt="expand-icon"/>
                </div>
                <div>
                {expiryDropdown && <div className="custom_select_options" ref={expiryRef} style={{width:'30%'}}>
                {expiryArray.map((expiry, index) => (<div key={index} className="custom_select_option" onClick={() => handleExpirySelect(index)} style={{padding:'12px 14px',maxWidth:'100%'}}>
                  {expiry}
                </div>))}
                </div>} 
                </div>
              </div>
              {expiry==='After certain number of runs' && (
                <div style={{width:'100%', marginTop:'10px'}}>
                  <input className="input_medium" type="text" value={expiryRuns} onChange={handleExpiryRuns} placeholder="Enter the number of runs" />
                </div>
              )}
              {expiry==='Specific Date' && (
                <div style={{width:'100%', marginTop:'10px'}}>
                  {/* <input className="input_medium" type="text" placeholder="Select the date" /> */}
                  <Datetime timeFormat={false} className={styles.rdtPicker} onChange={handleDateTimeChange} inputProps={{ placeholder: 'Enter here' }}/>
                </div>
              )}
            </div>
            </div>
            </div>)}
            <div style={{display: 'flex', justifyContent: 'flex-end',marginTop: '20px'}}>
              <button className="secondary_button" style={{marginRight: '10px'}} onClick={closeCreateModal}>
                Cancel
              </button>
              <button className={styles.run_button} onClick={handleUpdateSchedule} style={{paddingLeft:'15px',paddingRight:'25px'}}>
                Update Schedule
              </button>
            </div>
          </div>
        </div>)}

        {createStopModal && (
          <div className="modal" onClick={closeCreateModal}>
            <div className="modal-content" style={{width: '35%'}} onClick={preventDefault}>
            <div className={styles.detail_name}>Stop Schedule</div>
            <label className={styles.form_label}>All further schedules of this agent will be stopped. Are you sure you want to proceed?</label>
            <div style={{display: 'flex', justifyContent: 'flex-end',marginTop: '20px'}}>
              <button className="secondary_button" style={{marginRight: '10px'}} onClick={closeCreateModal}>
                Cancel
              </button>
              <button className={styles.run_button} style={{paddingLeft:'15px',paddingRight:'25px'}} onClick={stopSchedule}>
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
            <ActivityFeed selectedView={selectedView} selectedRunId={selectedRun?.id || 0} setFetchedData={setFetchedData}/>
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
          {rightPanel === 'details' && <div className={styles.detail_content}><Details agentDetails={agentDetails} tools={tools} runCount={agentExecutions?.length || 0}/></div>}
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
