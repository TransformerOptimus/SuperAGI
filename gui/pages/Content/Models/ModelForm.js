import React, {useEffect, useRef, useState} from "react";
import {removeTab, openNewTab} from "@/utils/utils";
import Image from "next/image";
import {fetchApiKey, verifyEndPoint} from "@/pages/api/DashboardService";

export default function ModelForm(){
    const models = ['OpenAI','Replicate','Hugging Face','Google Palm'];
    const [selectedModel, setSelectedModel] = useState('Select a Model');
    const [modelName, setModelName] = useState('');
    const [modelDescription, setModelDescription] = useState('');
    const [modelEndpoint, setModelEndpoint] = useState('');
    const [modelDropdown, setModelDropdown] = useState(false);
    const [tokenError, setTokenError] = useState(false);
    const [lockAddition, setLockAddition] = useState(true);
    const modelRef = useRef(null);

    useEffect(() => {
        function handleClickOutside(event) {
            if (modelRef.current && !modelRef.current.contains(event.target)) {
                setModelDropdown(false)
            }
        }
    },[]);

    useEffect(() => {
        if(selectedModel !== 'Select a Model' && tokenError)
            setLockAddition(false)
        else
            setLockAddition(true)
    },[selectedModel])

    const handleModelSelect = (index) => {
        setSelectedModel(models[index])
        setModelDropdown(false);
        checkModelProvider(models[index])
    }

    const checkModelProvider = (model_provider) => {
        fetchApiKey(model_provider).then((response) => {
            if(response.data.length <= 0)
                setTokenError(true)
            else
                setTokenError(false)
        })
    }

    const handleAddModel = () =>{
        console.log(modelName)
        console.log(modelDescription)
        console.log(modelEndpoint)
        fetchApiKey(selectedModel).then((response) =>{
            if(response.data.length > 0)
            {
                verifyEndPoint(response.data[0].api_key, modelEndpoint).then((response) =>{
                    console.log(response)
                })
            }
        })
    }

    return(
        <div id="model_form" className="vertical_containers text_12">
            <div className="page_title mt_10">Add new model</div>

            <span className="mt_4">Name</span>
            <input className="input_medium mt_8" type="text" placeholder="Enter Model Name"
                   onChange={(event) => setModelName(event.target.value)}/>

            <span className="mt_24">Description</span>
            <textarea className="textarea_medium mt_8" placeholder="Write a Description"
                      onChange={(event) => setModelDescription(event.target.value)}/>

            <span className="mt_24">Model Provider</span>
            <div className="dropdown_container_search mt_8 w_100">
                <div className="custom_select_container w_100" onClick={() => setModelDropdown(!modelDropdown)}>
                    {selectedModel}
                    <Image width={20} height={21} src={!modelDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'} alt="expand-icon"/>
                </div>
                <div>
                    {modelDropdown && <div className="custom_select_options w_100" ref={modelRef}>
                        {models.map((model, index) => (
                            <div key={index} className="custom_select_option" onClick={() => handleModelSelect(index)} style={{padding: '12px 14px', maxWidth: '100%'}}>
                                {model}
                            </div>))}
                    </div>}
                </div>
            </div>

            {tokenError && <div className="horizontal_container align_start error_box mt_24 gap_6">
                <Image width={16} height={16} src="/images/icon_error.svg" alt="error-icon" />
                <div className="vertical_containers">
                    <span className="text_12 color_white lh_16">The <b>{selectedModel}</b> auth token is not added to your settings. In order to start using the model, you need to add the auth token to your settings. You can find the auth token in the <b>{selectedModel}</b> dashboard. </span>
                    <div className="horizontal_container mt_16">
                        <button className="primary_button_small" onClick={() => openNewTab(-3, "Settings", "Settings", false)}>Add auth token</button>
                        <button className="secondary_button_small ml_8">Get auth token</button>
                    </div>
                </div>
            </div>}

            {(selectedModel === 'Hugging Face' || selectedModel === 'Replicate') && <div className="mt_24">
                <span>Model Endpoint URL</span>
                <input className="input_medium mt_8" type="text" placeholder="Enter Model Endpoint URL"
                       onChange={(event) => setModelEndpoint(event.target.value)}/>
            </div>}

            <div className="horizontal_container justify_end mt_24">
                <button className="secondary_button mr_7"
                        onClick={() => removeTab(-5, "new model", "Add_Model", internalId)}>Cancel</button>
                <button className="primary_button" onClick={() => handleAddModel()} disabled={lockAddition}>Add Model</button>
            </div>
        </div>
    )
}