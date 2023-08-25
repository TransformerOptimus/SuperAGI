import React, {useState, useEffect} from "react";
import Image from "next/image";
import {openNewTab, modelIcon} from "@/utils/utils";
import {fetchApiKey, storeModel} from "@/pages/api/DashboardService";
import {toast} from "react-toastify";

export default function AddModelMarketPlace(template){
    const [modelTokenLimit, setModelTokenLimit] = useState(4096);
    const [modelVersion, setModelVersion] = useState('');
    const [modelEndpoint, setModelEndpoint] = useState('');
    const [tokenError, setTokenError] = useState(false);
    const [templateData, setTemplateData] = useState(template.template);
    const [isLoading, setIsLoading] = useState(false);
    const [providerId, setProviderId] = useState(1);
    const [disableInstall, setDisableInstall] = useState(false);

    useEffect(() => {
        if(modelVersion === '' && modelEndpoint === '')
            setDisableInstall(true)
        else
            setDisableInstall(false)
    },[modelVersion, modelEndpoint])

    useEffect(()=>{
        console.log(templateData)
        checkModelProvider().then().catch();
    },[])

    const checkModelProvider = async () => {
        const response = await fetchApiKey(templateData.provider);
        console.log(response.data)
        if(response.data.length === 0) {
            setTokenError(true)
            return true
        }
        else {
            setTokenError(false)
            setProviderId(response.data[0].id)
            return false
        }
    }

    const storeModelDetails = () => {
        storeModel(templateData.model_name, templateData.description, modelEndpoint, providerId, modelTokenLimit, "Marketplace", modelVersion).then((response) =>{
            setIsLoading(false)
            console.log(response)
            if (response.data.error) {
                toast.error(response.data.error,{autoClose: 1800});
            } else if (response.data.success) {
                toast.success(response.data.success,{autoClose: 1800});
            }
        }).catch((error) => {
            console.log("SORRY, There was an error storing the model details" + error);
            setIsLoading(false)
        });
    }

    return(
        <div id="add_model_marketplace" className="row text_12 color_gray">
            <div className="col-3" />
            <div className="col-6 col-6-scrollable">
                <div className="vertical_containers">
                    <span className="text_16 color_white">Add Model</span>

                    <div className="vertical_containers tag_container mt_24">
                        <span className="text_14 color_white">{templateData.model_name}</span>
                        <div className="horizontal_container mt_8">
                            <span>By {templateData.provider}&nbsp;·&nbsp;</span>
                            <Image width={18} height={18} src={modelIcon(templateData.provider)} alt="logo-icon" />
                            <span className="ml_4">{templateData.provider}</span>
                        </div>
                    </div>
                    {templateData.provider === 'Hugging Face' && <div className="vertical_containers">
                        <span className="mt_24">{templateData.provider} Model Endpoint</span>
                        <input className="input_medium mt_8" type="text" placeholder="Enter Model Endpoint URL"
                               onChange={(event) => setModelEndpoint(event.target.value)}/>
                    </div>}

                    {templateData.provider === 'Replicate' && <div className="vertical_containers">
                        <span className="mt_24">{templateData.provider} Version</span>
                        <input className="input_medium mt_8" type="text" placeholder="Enter Model Version"
                               onChange={(event) => setModelVersion(event.target.value)}/>
                    </div>}

                    <span className="mt_24">Token Limit</span>
                    <input className="input_medium mt_8" type="number" placeholder="Enter the Token Limit" value={modelTokenLimit}
                           onChange={(event) => setModelTokenLimit(+event.target.value)} />

                    {tokenError && <div className="horizontal_container align_start error_box mt_24 gap_6">
                        <Image width={16} height={16} src="/images/icon_error.svg" alt="error-icon" />
                        <div className="vertical_containers">
                            <span className="text_12 color_white lh_16">The <b>{templateData.provider}</b> auth token is not added to your settings. In order to start using the model, you need to add the auth token to your settings. You can find the auth token in the <b>{templateData.provider}</b> dashboard. </span>
                            <div className="horizontal_container mt_16">
                                <button className="primary_button_small" onClick={() => openNewTab(-3, "Settings", "Settings", false)}>Add auth token</button>
                                <button className="secondary_button_small ml_8">Get auth token</button>
                            </div>
                        </div>
                    </div>}

                    {templateData.provider === 'Hugging Face' && <div className="horizontal_container align_start info_box mt_24 gap_6">
                        <Image width={16} height={16} src="/images/icon_info.svg" alt="error-icon" />
                        <div className="vertical_containers">
                            <span className="text_12 color_white lh_16">In order to get the endpoint for this model, you will need to deploy it on your Replicate dashboard. Once you have deployed your model on Hugging Face, you will be able to access the endpoint through the Hugging Face dashboard. The endpoint is a URL that you can use to send requests to your model.</span>
                            <button className="secondary_button_small w_fit_content mt_16"
                                    onClick={() => window.open("https://ui.endpoints.huggingface.co/", "_blank")}>Deploy<Image src="/images/open_in_new.svg" alt="deploy_icon" width={12} height={12} className="ml_4" /></button>
                        </div>
                    </div>}

                    <button className="primary_button w_fit_content align_self_end mt_24" disabled={tokenError}
                            onClick={() => storeModelDetails()}>Install</button>
                </div>
            </div>
            <div className="col-3" />
        </div>
    )
}