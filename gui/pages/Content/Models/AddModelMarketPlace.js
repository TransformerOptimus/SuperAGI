import React, {useState, useEffect} from "react";
import Image from "next/image";
import {openNewTab} from "@/utils/utils";
import {fetchApiKey} from "@/pages/api/DashboardService";

export default function AddModelMarketPlace(template){
    const [modelTokenLimit, setModelTokenLimit] = useState(4096);
    const [modelDetail, setModelDetail] = useState('');
    const [tokenError, setTokenError] = useState(false);

    useEffect(()=>{
        checkModelProvider()
    },[])
    const checkModelProvider = async () => {
        const response = await fetchApiKey('Google Palm');
        if(response && response.data && response.data.length <= 0) {
            setTokenError(true)
            return true
        }
        else {
            setTokenError(false)
            return false
        }
    }
    return(
        <div id="add_model_marketplace" className="row text_12 color_gray">
            <div className="col-3" />
            <div className="col-6 col-6-scrollable">
                <div className="vertical_containers">
                    <span className="text_16 color_white">Add Model</span>

                    <span className="mt_24">{template.source_name} Model Endpoint</span>
                    <input className="input_medium mt_8" type="text" placeholder="Enter Model Endpoint URL"
                           onChange={(event) => setModelDetail(event.target.value)}/>

                    <span className="mt_24">{template.source_name} Version</span>
                    <input className="input_medium mt_8" type="text" placeholder="Enter Model Version"
                           onChange={(event) => setModelDetail(event.target.value)}/>

                    <span className="mt_24">Token Limit</span>
                    <input className="input_medium mt_8" type="number" placeholder="Enter the Token Limit" value={modelTokenLimit}
                           onChange={(event) => setModelTokenLimit(+event.target.value)} />

                    {tokenError && <div className="horizontal_container align_start error_box mt_24 gap_6">
                        <Image width={16} height={16} src="/images/icon_error.svg" alt="error-icon" />
                        <div className="vertical_containers">
                            <span className="text_12 color_white lh_16">The <b>{template.source_name}</b> auth token is not added to your settings. In order to start using the model, you need to add the auth token to your settings. You can find the auth token in the <b>{template.source_name}</b> dashboard. </span>
                            <div className="horizontal_container mt_16">
                                <button className="primary_button_small" onClick={() => openNewTab(-3, "Settings", "Settings", false)}>Add auth token</button>
                                <button className="secondary_button_small ml_8">Get auth token</button>
                            </div>
                        </div>
                    </div>}

                    <div className="horizontal_container align_start info_box mt_24 gap_6">
                        <Image width={16} height={16} src="/images/icon_info.svg" alt="error-icon" />
                        <div className="vertical_containers">
                            <span className="text_12 color_white lh_16">In order to get the endpoint for this model, you will need to deploy it on your Replicate dashboard. Once you have deployed your model on Hugging Face, you will be able to access the endpoint through the Hugging Face dashboard. The endpoint is a URL that you can use to send requests to your model.</span>
                            <button className="secondary_button_small w_fit_content mt_16" onClick={() => openNewTab(-3, "Settings", "Settings", false)}>Deploy</button>
                        </div>
                    </div>

                    <button className="primary_button w_fit_content align_self_end mt_24">Install</button>
                </div>
            </div>
            <div className="col-3" />
        </div>
    )
}