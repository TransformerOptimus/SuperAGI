import React, {useEffect,useState} from "react";
import {removeTab, setLocalStorageValue, setLocalStorageArray, createInternalId} from "@/utils/utils";
import Image from "next/image";
import {ToastContainer, toast} from "react-toastify";
import {addUpdateKnowledge, getValidIndices} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";

export default function ModelForm ({}) {
    const [selectedModel, setSelectedModel] = useState('');
    const models=[{'name':'GPT', 'id':'1'},{'name':'Google','id':'2'},{'name':'Google','id':'3'},{'name':'Google','id':'4'}];

    return(
        <div id="model_form">
            <p className="text_16 mt_8">Choose a model source type</p>
            <div className="model_container mt_24 mb_24">
                {models && models.map((model,index) => (
                    <div className={selectedModel === model.id ? 'model_selected_container' : 'model_selection_container'} onClick={() => setSelectedModel(model.id)}>
                        <Image width={44} height={44} src="/images/gpt.svg" alt="no-image" />
                        <p className="text_16">{model.name}</p>
                    </div>)
                )}
            </div>
            <div className="display_flex w_100 justify_end">
                <button className="secondary_button" onClick={() => removeTab(-8,'new model','Add_Model',)}>Cancel</button>
                <button className="primary_button ml_6">Proceed</button>
            </div>
        </div>
    )
}