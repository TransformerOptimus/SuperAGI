import React, {useEffect, useRef, useState} from "react";
import {removeTab, openNewTab, createInternalId} from "@/utils/utils";
import Image from "next/image";
import {fetchApiKey, storeModel, verifyEndPoint} from "@/pages/api/DashboardService";
import {BeatLoader, ClipLoader} from "react-spinners";
import {ToastContainer, toast} from 'react-toastify';

export default function ModelForm({internalId, getModels, sendModelData}){
    const models = [{'provider':'OpenAI','link':'https://platform.openai.com/account/api-keys'},
        {'provider':'Replicate','link':'https://replicate.com/account/api-tokens'},
        {'provider':'Hugging Face','link':'https://huggingface.co/settings/tokens'},
        {'provider':'Google Palm','link':'https://developers.generativeai.google/products/palm'}];
    const [selectedModel, setSelectedModel] = useState('Select a Model');
    const [selectedLink, setSelectedLink] = useState('');
    const [modelName, setModelName] = useState('');
    const [modelDescription, setModelDescription] = useState('');
    const [modelTokenLimit, setModelTokenLimit] = useState(4096);
    const [modelEndpoint, setModelEndpoint] = useState('');
    const [modelDropdown, setModelDropdown] = useState(false);
    const [modelVersion, setModelVersion] = useState('');
    const [tokenError, setTokenError] = useState(false);
    const [lockAddition, setLockAddition] = useState(true);
    const [isLoading, setIsLoading] = useState(false)
    const modelRef = useRef(null);

    useEffect(() => {
        function handleClickOutside(event) {
            if (modelRef.current && !modelRef.current.contains(event.target)) {
                setModelDropdown(false)
            }
        }
    },[]);

    useEffect(() => {
        const fetchMyAPI = async () => {
            const error = await checkModelProvider(selectedModel)
            if(selectedModel !== 'Select a Model' && !error)
                setLockAddition(false)
            else
                setLockAddition(true)
        }

        fetchMyAPI();
    },[selectedModel])

    const handleModelSelect = async (index) => {
        setSelectedModel(models[index].provider)
        setSelectedLink(models[index].link)
        setModelDropdown(false);
    }

    const checkModelProvider = async (model_provider) => {
        const response = await fetchApiKey(model_provider);
        console.log(response.data)
        if(selectedModel !== 'Select a Model'){
            if(response.data.length === 0) {
                setTokenError(true)
                return true
            }
            else {
                setTokenError(false)
                return false
            }
        }
    }

    const handleAddModel = () =>{
        setIsLoading(true)
        fetchApiKey(selectedModel).then((response) =>{
            if(response.data.length > 0)
            {
                const modelProviderId = response.data[0].id
                verifyEndPoint(response.data[0].api_key, modelEndpoint, selectedModel).then((response) =>{
                    if(response.data.success)
                        storeModelDetails(modelProviderId)
                    else{
                        toast.error("The Endpoint is not Valid",{autoClose: 1800});
                        setIsLoading(false);
                    }
                }).catch((error) => {
                    console.log("Error Message:: " + error)
                })
            }
        })
    }

    const handleModelSuccess = (model) => {
        model.contentType = 'Model'
        sendModelData(model)
    }

    const storeModelDetails = (modelProviderId) => {
        storeModel(modelName,modelDescription, modelEndpoint, modelProviderId, modelTokenLimit, "Custom", modelVersion).then((response) =>{
            setIsLoading(false)
            let data = response.data
            if (data.error) {
                toast.error(data.error,{autoClose: 1800});
            } else if (data.success) {
                toast.success(data.success,{autoClose: 1800});
                getModels()
                handleModelSuccess({id: data.model_id, name: modelName})
            }
        }).catch((error) => {
            console.log("SORRY, There was an error storing the model details:", error);
            setIsLoading(false)
        });
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
                                {model.provider}
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
                        <button className="secondary_button_small ml_8"
                                onClick={() => window.open(selectedLink, "_blank")}>Get auth token<Image src="/images/open_in_new.svg" alt="deploy_icon" width={12} height={12} className="ml_4" /></button>
                    </div>
                </div>
            </div>}

            {(selectedModel === 'Hugging Face') && <div className="mt_24">
                <span>Model Endpoint URL</span>
                <input className="input_medium mt_8" type="text" placeholder="Enter Model Endpoint URL"
                       onChange={(event) => setModelEndpoint(event.target.value)}/>
            </div>}

            {(selectedModel === 'Replicate') && <div className="mt_24">
                <span>Model Version</span>
                <input className="input_medium mt_8" type="text" placeholder="Enter Model Version"
                       onChange={(event) => setModelVersion(event.target.value)}/>
            </div>}

            <div className="mt_24">
                <span>Token Limit</span>
                <input className="input_medium mt_8" type="number" placeholder="Enter Model Token Limit" value={modelTokenLimit}
                       onChange={(event) => setModelTokenLimit(parseInt(event.target.value, 10))}/>
            </div>

            <div className="horizontal_container justify_end mt_24">
                <button className="secondary_button mr_7"
                        onClick={() => removeTab(-5, "new model", "Add_Model", internalId)}>Cancel</button>
                <button className='primary_button' onClick={handleAddModel} disabled={lockAddition || isLoading}>
                    {isLoading ? <><span>Adding Model &nbsp;</span><ClipLoader size={16} color={"#000000"} /></> : 'Add Model'}
                </button>
            </div>
            <ToastContainer className="text_16"/>
        </div>
    )
}