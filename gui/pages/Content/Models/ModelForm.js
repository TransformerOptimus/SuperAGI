import React, {useEffect, useRef, useState} from "react";
import {removeTab, setLocalStorageValue} from "@/utils/utils";
import Image from "next/image";

export default function ModelForm(){
    const models = ['OpenAI','Replicate','HummingFace'];
    const [selectedModel, setSelectedModel] = useState(models[0]);
    const [modelDropdown, setModelDropdown] = useState(false);
    const modelRef = useRef(null);

    useEffect(() => {
        function handleClickOutside(event) {
            if (modelRef.current && !modelRef.current.contains(event.target)) {
                setModelDropdown(false)
            }
        }
    },[]);

    const handleModelSelect = (index) => {
        setSelectedModel(models[index])
        setModelDropdown(false);
    }


    return(
        <div id="model_form" className="vertical_containers text_12">
            <div className="page_title mt_10">Add new model</div>

            <span className="mt_4">Name</span>
            <input className="input_medium mt_8" type="text" placeholder="Enter Model Name" />

            <span className="mt_24">Description</span>
            <textarea className="textarea_medium mt_8" placeholder="Write a Description" />

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

            {(selectedModel === 'HummingFace' || selectedModel === 'Replicate') &&
                <div className="mt_24">
                    <span>Model Endpoint URL</span>
                    <input className="input_medium mt_8" type="text" placeholder="Enter Model Endpoint URL"/>
                </div>}

            <div className="horizontal_container justify_end mt_24">
                <button className="secondary_button mr_7"
                        onClick={() => removeTab(-5, "new model", "Add_Model", internalId)}>Cancel</button>
                <button className="primary_button">Add Model</button>
            </div>
        </div>
    )
}