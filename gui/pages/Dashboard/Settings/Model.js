import React, {useState, useEffect, useRef} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import agentStyles from "@/pages/Content/Agents/Agents.module.css";
import {storeApiKey, fetchApiKeys, validateLLMApiKey, fetchApiKey} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import {removeTab} from "@/utils/utils";
import Image from "next/image";

export default function Model({organisationId}) {
  const [temperature, setTemperature] = useState(0.5);
  const [models, setModels] = useState([
    {'name':'Open AI API key','logo':'/images/openai_logo.svg','source':'OpenAi', 'api_key': ''},
    {'name':'Hugging Face auth token','logo':'/images/huggingface_logo.svg','source':'Hugging Face', 'api_key': ''},
    {'name':'Replicate auth token','logo':'/images/replicate_logo.svg','source':'Replicate', 'api_key': ''},
    {'name':'Google Palm API key','logo':'/images/google_palm_logo.svg','source':'Google Palm', 'api_key': ''}
  ]);
  const [updatedModels, setUpdatedModels] = useState([]);

  useEffect(() => {
    fetchApiKeys().then((response) => {
      if(response.data.length > 0) {
        response.data.forEach(item => {
          const index = models.findIndex(model => model.source.toLowerCase() === item.provider.toLowerCase());
          if (index !== -1) {
            const newModels = [...models];
            newModels[index].api_key = item.api_key;
            setModels(newModels);
          }
        });
      }
    })
  },[])

  const saveSettings = () => {
    updatedModels.forEach(model => {
      if (model.api_key === null || model.api_key.replace(/\s/g, '') === '') {
        toast.error("API key is empty", {autoClose: 1800});
        return
      }
      validateLLMApiKey(model.source, model.api_key)
          .then((response) => {
            console.log(response)
            if (response.data.status === "success") {
              storeKey(model.source, model.api_key)
            }
            else {
              toast.error(`Invalid API key for ${model.source}`, {autoClose: 1800});
            }
          });
    });
  };

  const storeKey = (model_provider, api_key) => {
    if(model_provider === 'OpenAi')
      model_provider = 'OpenAI'
    storeApiKey(model_provider,api_key).then((response) => {
      if(response.status === 200)
        toast.success(`Successfully Stored the API Key of ${model_provider}`, {autoClose: 1800})
      else
        toast.error("Error", {autoClose: 1800})
    })
  }

  const handleInputChange = (source, value) => {
    const updatedModel = models.find(model => model.source === source);
    if (updatedModel) {
      updatedModel.api_key = value;
      setUpdatedModels(prevModels => {
        const existingIndex = prevModels.findIndex(model => model.source === source);
        if (existingIndex !== -1) {
          return [
            ...prevModels.slice(0, existingIndex),
            updatedModel,
            ...prevModels.slice(existingIndex + 1)
          ];
        } else {
          return [...prevModels, updatedModel];
        }
      });
    }
  };

  useEffect(() => {
    console.log(updatedModels)
  },[updatedModels])

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
                  <input placeholder={`Enter your ${model.name}`} className="input_medium mt_8" type="password" value={model.api_key}
                      onChange={(event) => handleInputChange(model.source, event.target.value)}/>
                </div>
            ))}
            {updatedModels.length > 0 && <div style={{display: 'flex', justifyContent: 'flex-end', marginTop: '15px'}}>
              <button onClick={() => removeTab(-3, "Settings", "Settings", 0)} className="secondary_button mr_10">Cancel</button>
              <button className="primary_button" onClick={saveSettings}>Update Changes</button>
            </div>}
          </div>
          <div className="col-3"></div>
        </div>
        <ToastContainer/>
      </>
  )
}