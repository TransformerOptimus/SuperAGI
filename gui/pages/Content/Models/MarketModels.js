import React, {useState, useEffect} from "react";
import styles from "@/pages/Content/Marketplace/Market.module.css";
import Image from "next/image";
import {loadingTextEffect, modelIcon, returnToolkitIcon} from "@/utils/utils";
import {EventBus} from "@/utils/eventBus";
import {fetchMarketPlaceModel} from "@/pages/api/DashboardService";
import axios from "axios";

export default function MarketModels(){
    const [showMarketplace, setShowMarketplace] = useState(false);
    const [isLoading, setIsLoading] = useState(false)
    const [loadingText, setLoadingText] = useState("Loading Models");
    const [modelTemplates, setModelTemplates] = useState([]);

    useEffect(() => {
        loadingTextEffect('Loading Models', setLoadingText, 500);

        if (window.location.href.toLowerCase().includes('marketplace')) {
            axios.get('https://app.superagi.com/api/models_controller/get/models_details')
                .then((response) => {
                    setModelTemplates(response.data)
                })
        }
        else {
            fetchMarketPlaceModel().then((response) => {
                setModelTemplates(response.data)
            })
        }
    },[])

    useEffect(() => {
        if(modelTemplates.length > 0)
            setIsLoading(true)
        else
            setIsLoading(false)
    }, [modelTemplates])

    function handleTemplateClick(item) {
        const contentType = 'model_template';
        EventBus.emit('openTemplateDetails', {item, contentType});
    }

    return(
        <div id="market_models" className={showMarketplace ? 'ml_8' : 'ml_3'}>
            <div className="w_100 overflowY_auto mxh_78vh">
                {isLoading ? <div>
                    {modelTemplates.length > 0 ? <div className="marketplaceGrid">{modelTemplates.map((item) => (
                        <div className="market_containers cursor_pointer" key={item.id} onClick={() => handleTemplateClick(item)}>
                            <div>{item.model_name && item.model_name.includes('/') ? item.model_name.split('/')[1] : item.model_name}</div>
                            <div className="horizontal_container color_gray">
                                <span>by { item.model_name && item.model_name.includes('/') ? item.model_name.split('/')[0] : item.provider }</span>
                                <Image className="mr_8 ml_4" width={14} height={14} src="/images/is_verified.svg" alt="is_verified" />·
                                <Image className="ml_8 mr_4" width={16} height={16} src={modelIcon(item.provider)} alt="source-icon" />
                                <span className="mr_8">{item.provider}</span>·
                                <Image className="ml_8 mr_4" width={15} height={15} src="/images/upload_icon.svg" alt="download-icon" />
                                <span>{item.installs}</span>
                            </div>
                            <div className="text_ellipsis mt_14 color_gray">{item.description}</div>
                        </div>
                    ))}</div> : <div className="center_container mt_40">
                        <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions"/>
                        <span className="feed_title mt_8">No Models found!</span>
                    </div>}
                </div> : <div className="horizontal_container_center h_75vh">
                    <div className="signInInfo text_16 ff_sourceCode">{loadingText}</div>
                </div>}
            </div>
        </div>
    )
}