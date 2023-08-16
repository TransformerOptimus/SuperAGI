import React, {useState, useEffect, useRef} from 'react';
import {setLocalStorageValue, convertToGMT, preventDefault} from "@/utils/utils";
import styles from "@/pages/Content/Agents/Agents.module.css";
import styles1 from "@/pages/Content/Agents/react-datetime.css";
import Image from "next/image";
import Datetime from "react-datetime";
import {toast} from "react-toastify";
import {agentScheduleComponent, createAndScheduleRun, updateSchedule} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import moment from 'moment';

export default function AgentSchedule({
                                        internalId,
                                        closeCreateModal,
                                        type,
                                        agentId,
                                        setCreateModal,
                                        setCreateEditModal,
                                        env,
                                      }) {
  const [isRecurring, setIsRecurring] = useState(false);
  const [timeDropdown, setTimeDropdown] = useState(false);
  const [expiryDropdown, setExpiryDropdown] = useState(false);

  const [startTime, setStartTime] = useState('');

  const timeUnitArray = (env === 'PROD') ? ['Days', 'Hours'] : ['Days', 'Hours', 'Minutes'];
  const [timeUnit, setTimeUnit] = useState(timeUnitArray[1]);
  const [timeValue, setTimeValue] = useState(null);

  const expiryTypeArray = ['Specific Date', 'After certain number of runs', 'No expiry'];
  const [expiryType, setExpiryType] = useState(expiryTypeArray[1]);
  const [expiryRuns, setExpiryRuns] = useState(0);
  const [expiryDate, setExpiryDate] = useState(null);

  const timeRef = useRef(null);
  const expiryRef = useRef(null);

  const [modalHeading, setModalHeading] = useState('Schedule Run')
  const [modalButton, setModalButton] = useState('Create and Schedule Run')
  const [localStartTime, setLocalStartTime] = useState('')

  useEffect(() => {
    function handleClickOutside(event) {
      if (timeRef.current && !timeRef.current.contains(event.target)) {
        setTimeDropdown(false)
      }

      if (expiryRef.current && !expiryRef.current.contains(event.target)) {
        setExpiryDropdown(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    if (type === "edit_schedule_agent") {
      setModalHeading('Edit Schedule')
      setModalButton("Update Schedule")
      fetchAgentScheduleComponent();
    }
  }, []);

  useEffect(() => {
    if (internalId !== null) {
      const agent_is_recurring = localStorage.getItem("agent_is_recurring_" + String(internalId));
      if (agent_is_recurring) {
        setIsRecurring(JSON.parse(agent_is_recurring));
      }

      const agent_time_unit = localStorage.getItem("agent_time_unit_" + String(internalId));
      if (agent_time_unit) {
        setTimeUnit(agent_time_unit);
      }

      const agent_time_value = localStorage.getItem("agent_time_value_" + String(internalId));
      if (agent_time_value) {
        setTimeValue(Number(agent_time_value));
      }

      const agent_expiry_type = localStorage.getItem("agent_expiry_type_" + String(internalId));
      if (agent_expiry_type) {
        setExpiryType(agent_expiry_type);
      }

      const agent_expiry_runs = localStorage.getItem("agent_expiry_runs_" + String(internalId));
      if (agent_expiry_runs) {
        setExpiryRuns(Number(agent_expiry_runs));
      }

      const agent_start_time = localStorage.getItem("agent_start_time_" + String(internalId));
      if (agent_start_time) {
        setStartTime(agent_start_time);
      }

      const agent_expiry_date = localStorage.getItem("agent_expiry_date_" + String(internalId));
      if (agent_expiry_date) {
        setExpiryDate(agent_expiry_date);
      }
    }
  }, [internalId])

  const handleDateTimeChange = (momentObj) => {
    const expiryDate = convertToGMT(momentObj);
    setLocalStorageValue("agent_expiry_date_" + String(internalId), expiryDate, setExpiryDate);
  };

  const handleTimeChange = (momentObj) => {
    const startTime = convertToGMT(momentObj);
    setLocalStartTime(typeof momentObj === 'string' ? '' : momentObj.toDate())
    setLocalStorageValue("agent_start_time_" + String(internalId), startTime, setStartTime);
  };

  const toggleRecurring = () => {
    setLocalStorageValue("agent_is_recurring_" + String(internalId), !isRecurring, setIsRecurring);
  };

  const handleTimeSelect = (index) => {
    setLocalStorageValue("agent_time_unit_" + String(internalId), timeUnitArray[index], setTimeUnit);
    setTimeDropdown(false);
  }

  const handleExpirySelect = (index) => {
    setLocalStorageValue("agent_expiry_type_" + String(internalId), expiryTypeArray[index], setExpiryType);
    setExpiryDropdown(false);
  }

  const handleDateChange = (event) => {
    setLocalStorageValue("agent_time_value_" + String(internalId), event.target.value, setTimeValue);
  };

  const handleExpiryRuns = (event) => {
    setLocalStorageValue("agent_expiry_runs_" + String(internalId), event.target.value, setExpiryRuns);
  };

  const addScheduledAgent = () => {
    if ((startTime === '' || (isRecurring === true && (timeValue == null || (expiryType === "After certain number of runs" && (parseInt(expiryRuns, 10) < 1)) || (expiryType === "Specific date" && expiryDate == null))))) {
      toast.error('Please input correct details', {autoClose: 1800});
      return;
    }

    if (type === "create_agent") {
      const scheduleData = {
        "start_time": startTime,
        "recurrence_interval": timeValue ? `${timeValue} ${timeUnit}` : null,
        "expiry_runs": expiryType === 'After certain number of runs' ? parseInt(expiryRuns) : -1,
        "expiry_date": expiryType === 'Specific Date' ? expiryDate : null,
      }
      EventBus.emit('handleAgentScheduling', scheduleData);
    } else {
      if (type === "schedule_agent") {
        const requestData = {
          "agent_id": agentId,
          "start_time": startTime,
          "recurrence_interval": timeValue && isRecurring ? `${timeValue} ${timeUnit}` : null,
          "expiry_runs": expiryType === 'After certain number of runs' && isRecurring ? parseInt(expiryRuns) : -1,
          "expiry_date": expiryType === 'Specific Date' && isRecurring ? expiryDate : null,
        };

        createAndScheduleRun(requestData)
          .then(response => {
            const {schedule_id} = response.data;
            toast.success('Scheduled successfully!', {autoClose: 1800});
            setCreateModal();
            EventBus.emit('reFetchAgents', {});
            setTimeout(() => {
                EventBus.emit('refreshDate', {});
            }, 1000)
          })
          .catch(error => {
            console.error('Error:', error);
          });
      } else {
        if (type === "edit_schedule_agent") {
          fetchUpdateSchedule();
        }
      }
    }
  };

  function checkTime() {
    if (expiryDate === null) {
      return true;
    }
    let date1 = expiryDate;
    if (typeof expiryDate === 'string' && expiryDate.includes('/')) {
      date1 = moment(expiryDate, 'DD/MM/YYYY').toDate();
    } else if (typeof expiryDate === 'string') {
      date1 = moment.utc(expiryDate, 'YYYY-MM-DD HH:mm:ss').local().toDate();
    } else
      return
    let date2 = moment.utc(startTime, 'YYYY-MM-DD HH:mm:ss').local().toDate();

    date1.setHours(0, 0, 0, 0);
    date2.setHours(0, 0, 0, 0);

    date1 = convertToGMT(date1);
    date2 = convertToGMT(date2);

    return date1 <= date2;
  }

  function fetchUpdateSchedule() {
    if (expiryType === 'Specific Date' && checkTime()) {
      toast.error('Expiry Date of agent is before Start Date')
      return;
    }
    const requestData = {
      "agent_id": agentId,
      "start_time": startTime,
      "recurrence_interval": timeValue && isRecurring ? `${timeValue} ${timeUnit}` : null,
      "expiry_runs": expiryType === 'After certain number of runs' && isRecurring ? parseInt(expiryRuns) : -1,
      "expiry_date": expiryType === 'Specific Date' && isRecurring ? (expiryDate && expiryDate.includes('/') ? convertToGMT(moment(expiryDate, 'DD/MM/YYYY').toDate()) : expiryDate) : null,
    };

    updateSchedule(requestData)
      .then((response) => {
        if (response.status === 200) {
          toast.success('Schedule updated successfully', {autoClose: 1800});
          EventBus.emit('refreshDate', {});
          setCreateEditModal();
          EventBus.emit('reFetchAgents', {});
        } else {
          toast.error('Error updating agent schedule', {autoClose: 1800});
        }
      })
      .catch((error) => {
        console.error('Error updating agent schedule:', error);
      });
  }

  function fetchAgentScheduleComponent() {
    agentScheduleComponent(agentId)
      .then((response) => {
        const {current_datetime, recurrence_interval, expiry_date, expiry_runs, start_date, start_time} = response.data;
        setExpiryRuns(expiry_runs);
        setExpiryDate(expiry_date);
        if ((expiry_date || expiry_runs !== -1) && recurrence_interval !== null) {
          setTimeValue(parseInt(recurrence_interval.substring(0, 1), 10))
          setTimeUnit(recurrence_interval.substring(2,))
          setIsRecurring(true);
          setExpiryType(expiry_date ? 'Specific Date' : 'After certain number of runs');
        } else {
          setExpiryType('No expiry');
        }
      })
      .catch((error) => {
        console.error('Error fetching agent data:', error);
      });
  }

  return (
    <div>
      <div className="modal" onClick={closeCreateModal}>
        <div className="modal-content" style={{width: '35%'}} onClick={preventDefault}>
          <div className={styles.detail_name}>{modalHeading}</div>
          <div>
            <label className={styles.form_label}>Select a date and time</label>
            <div>
              <Datetime className={`${styles1.className} ${styles.rdtPicker}`} onChange={handleTimeChange}
                        inputProps={{placeholder: new Date()}}
                        isValidDate={current => current.isAfter(Datetime.moment().subtract(1, 'day'))}/>
            </div>
          </div>
          <div style={{display: 'flex', marginTop: '20px'}}>
            <input className="checkbox" type="checkbox" checked={isRecurring} onChange={toggleRecurring}/>
            <label className={styles.form_label} style={{marginLeft: '7px', cursor: 'pointer'}}
                   onClick={toggleRecurring}>
              Recurring run
            </label>
          </div>
          {isRecurring && (<div style={{marginTop: '20px'}}>
            <div style={{color: "white", marginBottom: '10px'}}>Recurring run details</div>
            <label className={styles.form_label}>Repeat every</label>
            <div style={{display: 'flex', marginBottom: '20px'}}>
              <div style={{width: '70%', marginRight: '5px'}}>
                <input className="input_medium" type="number" value={timeValue} onChange={handleDateChange}
                       placeholder='Enter here'/>
              </div>
              <div style={{width: '30%'}}>
                <div className="custom_select_container" onClick={() => setTimeDropdown(!timeDropdown)}
                     style={{width: '100%'}}>
                  {timeUnit}<Image width={20} height={21}
                                   src={!timeDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'}
                                   alt="expand-icon"/>
                </div>
                <div>
                  {timeDropdown && <div className="custom_select_options" ref={timeRef} style={{width: '137px'}}>
                    {timeUnitArray.map((timeUnit, index) => (
                      <div key={index} className="custom_select_option" onClick={() => handleTimeSelect(index)}
                           style={{padding: '12px 14px', maxWidth: '100%'}}>
                        {timeUnit}
                      </div>))}
                  </div>}
                </div>
              </div>
            </div>
            <label className={styles.form_label}>Recurring expiry</label>
            <div>
              <div style={{display: 'inline'}}>
                <div style={{width: '100%', marginRight: '5px'}}>
                  <div className="custom_select_container" onClick={() => setExpiryDropdown(!expiryDropdown)}
                       style={{width: '100%'}}>
                    {expiryType}<Image width={20} height={21}
                                       src={!expiryDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'}
                                       alt="expand-icon"/>
                  </div>
                  <div>
                    {expiryDropdown && <div className="custom_select_options" ref={expiryRef}>
                      {expiryTypeArray.map((expiryType, index) => (
                        <div key={index} className="custom_select_option" onClick={() => handleExpirySelect(index)}
                             style={{padding: '12px 14px', maxWidth: '100%'}}>
                          {expiryType}
                        </div>))}
                    </div>}
                  </div>
                </div>
                {expiryType === 'After certain number of runs' && (
                  <div style={{width: '100%', marginTop: '10px'}}>
                    <input className="input_medium" type="number" value={expiryRuns} onChange={handleExpiryRuns}
                           placeholder="Enter the number of runs"/>
                  </div>
                )}
                {expiryType === 'Specific Date' && (
                  <div style={{width: '100%', marginTop: '10px'}}>
                    {type !== "edit_schedule_agent" &&
                      <Datetime timeFormat={false} className={`${styles1.className} ${styles.rdtPicker}`}
                                onChange={handleDateTimeChange} inputProps={{placeholder: new Date()}}
                                isValidDate={current => current.isAfter(moment(localStartTime))}/>}
                    {type === "edit_schedule_agent" && expiryDate && <div className={styles.form_label} style={{
                      display: 'flex',
                      fontSize: '14px',
                      justifyContent: 'space-between'
                    }}>
                      <div>The expiry date of the run
                        is {(new Date(`${expiryDate}Z`).toLocaleString()).substring(0, 10) == "Invalid Da" ? expiryDate : (new Date(`${expiryDate}Z`).toLocaleString()).substring(0, 10)}</div>
                      <div className="secondary_button" style={{cursor: 'pointer', height: '20px', fontSize: '12px'}}
                           onClick={() => setExpiryDate(null)}>Edit
                      </div>
                    </div>}
                    {type === "edit_schedule_agent" && !expiryDate &&
                      <Datetime timeFormat={false} className={`${styles1.className} ${styles.rdtPicker}`}
                                onChange={handleDateTimeChange} inputProps={{placeholder: new Date()}}
                                isValidDate={current => current.isAfter(moment(localStartTime))}/>}
                  </div>
                )}
              </div>
            </div>
          </div>)}
          <div style={{display: 'flex', justifyContent: 'flex-end', marginTop: '20px'}}>
            <button className="secondary_button" style={{marginRight: '10px'}} onClick={closeCreateModal}>
              Cancel
            </button>
            <button className={styles.run_button} style={{paddingLeft: '15px', paddingRight: '15px', height: '32px'}}
                    onClick={addScheduledAgent}>
              {modalButton}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};