import React, {useState, useEffect} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import agentStyles from "@/pages/Content/Agents/Agents.module.css";
import {getOrganisationConfig, updateOrganisationConfig} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import {removeTab} from "@/utils/utils";

export default function Settings({organisationId}) {
  const [openAIKey, setKey] = useState('');
  const [temperature, setTemperature] = useState(0.5);

  function getKey(key) {
    getOrganisationConfig(organisationId, key)
        .then((response) => {
          setKey(response.data.value);
        })
        .catch((error) => {
          console.error('Error fetching project:', error);
        });
  }

  useEffect(() => {
    getKey("model_api_key");
  }, [organisationId]);

  function updateKey(key, value) {
    const configData = {"key": key, "value": value};
    updateOrganisationConfig(organisationId, configData)
        .then((response) => {
          getKey("model_api_key");
          EventBus.emit("keySet", {});
          toast.success("Settings updated", {autoClose: 1800});
        })
        .catch((error) => {
          console.error('Error fetching project:', error);
        });
  }

  const handleOpenAIKey = (event) => {
    setKey(event.target.value);
  };

  const preventDefault = (e) => {
    e.stopPropagation();
  };

  const saveSettings = () => {
    if (openAIKey === null || openAIKey.replace(/\s/g, '') === '') {
      toast.error("API key is empty", {autoClose: 1800});
      return
    }

    updateKey("model_api_key", openAIKey);
  };

  const handleTemperatureChange = (event) => {
    setTemperature(event.target.value);
  };

  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6" style={{overflowY:'scroll',height:'calc(100vh - 92px)',padding:'25px 20px'}}>
        <div>
          <div className={agentStyles.page_title}>Settings</div>
        </div>
        <div>
          <label className={agentStyles.form_label}>Open-AI API Key</label>
          <input placeholder="Enter your Open-AI API key" className="input_medium" type="password" value={openAIKey} onChange={handleOpenAIKey}/>
        </div>
        {/*<div style={{marginTop:'15px'}}>*/}
        {/*  <label className={agentStyles.form_label}>Temperature</label>*/}
        {/*  <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>*/}
        {/*    <input style={{width:'89%'}} type="range" step={0.1} min={0} max={1} value={temperature} onChange={handleTemperatureChange}/>*/}
        {/*    <input style={{width:'9%',order:'1',textAlign:'center',paddingLeft:'0',paddingRight:'0'}} disabled={true} className="input_medium" type="text" value={temperature}/>*/}
        {/*  </div>*/}
        {/*</div>*/}
        <div style={{display: 'flex', justifyContent: 'flex-end',marginTop:'15px'}}>
          <button onClick={() => removeTab(-3, "Settings", "Settings")} className="secondary_button" style={{marginRight: '10px'}}>
            Cancel
          </button>
          <button className="primary_button" onClick={saveSettings}>
            Update Changes
          </button>
        </div>
      </div>
      <div className="col-3"></div>
    </div>
    <ToastContainer/>
  </>)
}