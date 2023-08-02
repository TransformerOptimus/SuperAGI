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
    {'name':'Open AI API key','logo':'/images/openai_logo.svg','source':'OpenAi'},
    {'name':'Hugging Face auth token','logo':'/images/huggingface_logo.svg','source':'Hugging Face'},
    {'name':'Replicate auth token','logo':'/images/replicate_logo.svg','source':'Replicate'},
    {'name':'Google AI API key','logo':'/images/google_palm_logo.svg','source':'Google Palm'}]);
  const [updatedModels, setUpdatedModels] = useState([]);
  const [visible, setVisible] = useState(false);

  // function getKey(key) {
  //   getOrganisationConfig(organisationId, key)
  //     .then((response) => {
  //       setKey(response.data.value);
  //     })
  //     .catch((error) => {
  //       console.error('Error fetching project:', error);
  //     });
  // }
  //
  // function getSource(key) {
  //   getOrganisationConfig(organisationId, key)
  //     .then((response) => {
  //       setSource(response.data.value);
  //     })
  //     .catch((error) => {
  //       console.error('Error fetching project:', error);
  //     });
  // }

  // useEffect(() => {
  //   getKey("model_api_key");
  //   getSource("model_source");
  // }, [organisationId]);

  //
  // function updateKey(key, value) {
  //   const configData = {"key": key, "value": value};
  //   updateOrganisationConfig(organisationId, configData)
  //     .then((response) => {
  //       getKey("model_api_key");
  //       EventBus.emit("keySet", {});
  //       toast.success("Settings updated", {autoClose: 1800});
  //     })
  //     .catch((error) => {
  //       console.error('Error fetching project:', error);
  //     });
  // }

  useEffect(() => {
    fetchApiKeys().then((response) => {
      response.data.forEach(item => {
        const index = models.findIndex(model => model.source === item.source_name);
        if(index !== -1) {
          const newModels = [...models];
          newModels[index].api_key = item.api_key;
          setModels(newModels);
        }
      });
    })

    fetchApiKey("Replicate").then((response) => {
      console.log(response)
    })
  },[])

  const saveSettings = () => {
    updatedModels.forEach(model => {
      if (model.api_key === null || model.api_key.replace(/\s/g, '') === '') {
        toast.error("API key is empty", {autoClose: 1800});
        return
      }
      validateLLMApiKey(model.name, model.api_key)
          .then((response) => {
            if (response.data.status === "success") {
              storeKey(model.name, model.api_key)
            }
            else {
              toast.error(`Invalid API key for ${model.name}`, {autoClose: 1800});
            }
          });
    });
  };

  const storeKey = (model_provider, api_key) => {
    storeApiKey(model_provider,api_key).then((response) => {
      console.log(response)
      if(response.status_code === 200)
        toast.success("Successfully Stored", {autoClose: 1800})
      else
        toast.error("Error", {autoClose: 1800})
    })
  }

  const handleInputChange = (source, value) => {
    const updatedModels = models.map(model => {
      if (model.source === source) {
        return { ...model, api_key: value }
      }
      return model
    })
    setModels(updatedModels)
  }

  const toggleVisibility = () => {
    setVisible(!visible);
  }

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