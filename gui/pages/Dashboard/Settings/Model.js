import React, {useState, useEffect, useRef} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import agentStyles from "@/pages/Content/Agents/Agents.module.css";
import {
  getOrganisationConfig,
  updateOrganisationConfig,
  validateAPI,
  validateLLMApiKey
} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import {removeTab} from "@/utils/utils";
import Image from "next/image";

export default function Model({organisationId}) {
  const [modelApiKey, setKey] = useState('');
  const [temperature, setTemperature] = useState(0.5);
  const [sourceDropdown, setSourceDropdown] = useState(false);
  const sources = ['OpenAi', 'Google Palm'];
  const models = [{'name':'Open AI API key','api_key':'asdfsddfgdfgd','logo':'/images/openai_logo.svg'},
                                          {'name':'Hugging Face auth token','api_key':'','logo':'/images/huggingface_logo.svg'},
                                          {'name':'Replicate auth token','api_key':'asdfsddfgdfgd','logo':'/images/replicate_logo.svg'},
                                          {'name':'Google AI API key','api_key':'','logo':'/images/google_palm_logo.svg'}]
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
        toast.success("Settings updated", {autoClose: 1800});
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

  return (
      <>
        <div className="row">
          <div className="col-3"></div>
          <div className="col-6 col-6-scrollable">
            {models.map(model => (
                <div key={model.name}>
                  <div className="horizontal_container align_center mt_24 gap_8">
                    <Image width={16} height={16} src={model.logo} alt={`${model.name}-icon`} />
                    <span className="text_13 color_gray">{model.name}</span>
                  </div>
                  <input placeholder={`Enter your ${model.name}`} className="input_medium mt_8" type="password" value={model.api_key} />
                </div>
            ))}
            <div style={{display: 'flex', justifyContent: 'flex-end', marginTop: '15px'}}>
              <button onClick={() => removeTab(-3, "Settings", "Settings", 0)} className="secondary_button mr_10">Cancel</button>
              <button className="primary_button" onClick={saveSettings}>Update Changes</button>
              <button className="primary_button" onClick={saveSettings2}>Changes</button>
            </div>
          </div>
          <div className="col-3"></div>
        </div>
        <ToastContainer/>
      </>
  )
}