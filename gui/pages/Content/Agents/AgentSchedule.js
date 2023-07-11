import React, {useState, useEffect, useRef} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles from "@/pages/Content/Agents/Agents.module.css";
import {getOrganisationConfig, updateOrganisationConfig} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import {removeTab, setLocalStorageValue} from "@/utils/utils";
import Image from "next/image";
import DateTimePicker from 'react-datetime-picker';
import 'react-datetime-picker/dist/DateTimePicker.css';
import 'react-calendar/dist/Calendar.css';
import 'react-clock/dist/Clock.css';
import './Agents.module.css'
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
// import styles1 from "@/pages/Content/Agents/Agents.module.css";

export default function AgentSchedule({organisationId}) {
    const [modelApiKey, setKey] = useState('');
    const [isRecurring, setIsRecurring] = useState(false);
    const [timeValue, setTimeValue] = useState('');
    const expiryTypeArray = ['Specific Date', 'After certain number of runs', 'No expiry'];
    const [expiryType, setExpiryType] = useState(expiryTypeArray[1]);
    const [expiryDropdown, setExpiryDropdown] = useState(false);
    const [expiryRuns, setExpiryRuns] = useState(-1);
    const timeUnitArray = ['Days', 'Hours', 'Minutes', 'Weeks', 'Months'];
    const [timeUnit, setTimeUnit] = useState(timeUnitArray[1]);
    const [timeDropdown, setTimeDropdown] = useState(false);
    const expiryRef = useRef(null);
    const timeRef = useRef(null);

    const [startDate, setStartDate] = useState(new Date());
    const [showPicker, setShowPicker] = useState(false);

    const onDateChange = (value) => {
        setDate(value);
    };

    const togglePicker = () => {
        setShowPicker(!showPicker);
    };
    const onChange = (value) => {
        setDate(value);
    };

    const preventDefault = (e) => {
        e.stopPropagation();
    };
    const toggleRecurring = () => {
        setIsRecurring(!isRecurring)
        // setLocalStorageValue("agent_is_recurring_" + String(internalId), !isRecurring, setIsRecurring);
    };
    const handleDateChange = (event) => {
        setTimeValue(event.target.value);
    };
    const handleExpirySelect = (index) => {
        // setLocalStorageValue("agent_expiry_type_" + String(internalId), expiryTypeArray[index], setExpiryType);
        setExpiryType(expiryTypeArray[index])
        setExpiryDropdown(false);
    }
    const handleExpiryRuns = (event) => {
        setExpiryRuns(event.target.value);
    };
    const handleTimeSelect = (index) => {
        setTimeUnit(timeUnitArray[index])
        // setLocalStorageValue("agent_time_unit_" + String(internalId), timeUnitArray[index], setTimeUnit);
        setTimeDropdown(false);
    }

    return (<>
            <div className="modal">
                <div className="modal-content" style={{width:'35%'}} onClick={preventDefault}>
                    <div className={styles.detail_name}>Schedule Run</div>
                    <div>
                        <label className={styles.form_label}>Select a date and time</label>
                        <div className="input_medium">
                            <DatePicker
                                selected={startDate}
                                onChange={date => setStartDate(date)}
                                showTimeSelect
                                timeFormat="HH:mm"
                                timeIntervals={15}
                                timeCaption="time"
                                dateFormat="MMMM d, yyyy h:mm aa"
                            />
                            {/*<Datetime className={`${styles1.className} ${styles.rdtPicker}`} onChange={handleTimeChange} inputProps={{ placeholder: 'Enter here' }}/>*/}
                        </div>
                    </div>
                    <div style={{display:'flex',marginTop:'20px'}}>
                        <input className="checkbox" type="checkbox" checked={isRecurring} onChange={toggleRecurring} />
                        <label className={styles.form_label} style={{marginLeft:'7px',cursor:'pointer'}} onClick={toggleRecurring}>
                            Recurring run
                        </label>
                    </div>
                    {isRecurring && (<div style={{marginTop:'20px'}}>
                        <div style={{color:"white", marginBottom:'10px'}}>Recurring run details</div>
                        <label className={styles.form_label}>Repeat every</label>
                        <div style={{display:'flex',marginBottom:'20px'}}>
                            <div style={{width:'70%', marginRight:'5px'}}>
                                <input className="input_medium" type="number" value={timeValue} onChange={handleDateChange} placeholder='Enter here'/>
                            </div>
                            <div style={{width:'30%'}}>
                                <div className="custom_select_container" onClick={() => setTimeDropdown(!timeDropdown)} style={{width:'100%'}}>
                                    {timeUnit}<Image width={20} height={21} src={!timeDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'} alt="expand-icon"/>
                                </div>
                                <div>
                                    {timeDropdown && <div className="custom_select_options" ref={timeRef} style={{width:'137px'}}>
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
                                        {expiryType}<Image width={20} height={21} src={!expiryDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'} alt="expand-icon"/>
                                    </div>
                                    <div>
                                        {expiryDropdown && <div className="custom_select_options" ref={expiryRef}>
                                            {expiryTypeArray.map((expiryType, index) => (<div key={index} className="custom_select_option" onClick={() => handleExpirySelect(index)} style={{padding:'12px 14px',maxWidth:'100%'}}>
                                                {expiryType}
                                            </div>))}
                                        </div>}
                                    </div>
                                </div>
                                {expiryType === 'After certain number of runs' && (
                                    <div style={{width:'100%', marginTop:'10px'}}>
                                        <input className="input_medium" type="number" value={expiryRuns} onChange={handleExpiryRuns} placeholder="Enter the number of runs" />
                                    </div>
                                )}
                                {expiryType === 'Specific Date' && (
                                    <div style={{width:'100%', marginTop:'10px'}}>
                                        {/*<Datetime timeFormat={false} className={`${styles1.className} ${styles.rdtPicker}`} onChange={handleDateTimeChange} inputProps={{ placeholder: 'Enter here' }}/>*/}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>)}
                </div>
            </div>
        <ToastContainer/>
    </>)
}