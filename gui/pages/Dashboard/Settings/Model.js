import React, {useState, useEffect, useRef} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import agentStyles from "@/pages/Content/Agents/Agents.module.css";
import {getOrganisationConfig, updateOrganisationConfig, validateLLMApiKey} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import {removeTab} from "@/utils/utils";
import Image from "next/image";

export default function Model({organisationId}) {
  const [modelApiKey, setKey] = useState('');
  const [temperature, setTemperature] = useState(0.5);
  const [sourceDropdown, setSourceDropdown] = useState(false);
  const sources = ['OpenAi', 'Google Palm'];
  const [source, setSource] = useState(sources[0]);
  const sourceRef = useRef(null);

  function getKey(key) {
    getOrganisationConfig(organisationId, key)
      .then((response) => {
        setKey(response.data.value);
      })
      .catch((error) => {
        console.error('Error fetching project:', error);
      });
  }

  function getSource(key) {
    getOrganisationConfig(organisationId, key)
      .then((response) => {
        setSource(response.data.value);
      })
      .catch((error) => {
        console.error('Error fetching project:', error);
      });
  }

  useEffect(() => {
    getKey("model_api_key");
    getSource("model_source");
  }, [organisationId]);

  useEffect(() => {
    function handleClickOutside(event) {
      if (sourceRef.current && !sourceRef.current.contains(event.target)) {
        setSourceDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  function updateKey(key, value) {
    const configData = {"key": key, "value": value};
    updateOrganisationConfig(organisationId, configData)
      .then((response) => {
        getKey("model_api_key");
        EventBus.emit("keySet", {});
        if (key === "model_source") {
          toast.success("Settings updated", {autoClose: 1800});
        }
      })
      .catch((error) => {
        console.error('Error fetching project:', error);
      });
  }

  const handleModelApiKey = (event) => {
    setKey(event.target.value);
  };

  const handleSourceSelect = (index) => {
    setSource(sources[index]);
    setSourceDropdown(false);
  };

  const saveSettings = () => {
    if (modelApiKey === null || modelApiKey.replace(/\s/g, '') === '') {
      toast.error("API key is empty", {autoClose: 1800});
      return
    }
    validateLLMApiKey(source, modelApiKey)
      .then((response) => {
        if (response.data.status === "success") {
          updateKey("model_api_key", modelApiKey);
          updateKey("model_source", source);
        } else {
          toast.error("Invalid API key", {autoClose: 1800});
        }
      });
  };

  const handleTemperatureChange = (event) => {
    setTemperature(event.target.value);
  };

  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6" style={{overflowY: 'scroll', height: 'calc(100vh - 92px)', padding: '25px 20px'}}>
        <div>
          <div className={agentStyles.page_title}>Settings</div>
        </div>
        <div>
          <label className={agentStyles.form_label}>Model Source</label>
          <div className="dropdown_container_search" style={{width: '100%'}}>
            <div className="custom_select_container" onClick={() => setSourceDropdown(!sourceDropdown)}
                 style={{width: '100%'}}>
              {source}<Image width={20} height={21}
                             src={!sourceDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'}
                             alt="expand-icon"/>
            </div>
            <div>
              {sourceDropdown && <div className="custom_select_options" ref={sourceRef} style={{width: '100%'}}>
                {sources.map((source, index) => (
                  <div key={index} className="custom_select_option" onClick={() => handleSourceSelect(index)}
                       style={{padding: '12px 14px', maxWidth: '100%'}}>
                    {source}
                  </div>))}
              </div>}
            </div>
          </div>
        </div>
        <br/>
        {source === 'OpenAi' && <div>
          <label className={agentStyles.form_label}>Open-AI API Key</label>
          <input placeholder="Enter your Open-AI API key" className="input_medium" type="password" value={modelApiKey}
                 onChange={handleModelApiKey}/>
        </div>}
        {source === 'Google Palm' && <div>
          <label className={agentStyles.form_label}>Palm API Key</label>
          <input placeholder="Enter your Palm API key" className="input_medium" type="password" value={modelApiKey}
                 onChange={handleModelApiKey}/>
        </div>}
        {/*<div style={{marginTop:'15px'}}>*/}
        {/*  <label className={agentStyles.form_label}>Temperature</label>*/}
        {/*  <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>*/}
        {/*    <input style={{width:'89%'}} type="range" step={0.1} min={0} max={1} value={temperature} onChange={handleTemperatureChange}/>*/}
        {/*    <input style={{width:'9%',order:'1',textAlign:'center',paddingLeft:'0',paddingRight:'0'}} disabled={true} className="input_medium" type="text" value={temperature}/>*/}
        {/*  </div>*/}
        {/*</div>*/}
        <div style={{display: 'flex', justifyContent: 'flex-end', marginTop: '15px'}}>
          <button onClick={() => removeTab(-3, "Settings", "Settings", 0)} className="secondary_button"
                  style={{marginRight: '10px'}}>
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