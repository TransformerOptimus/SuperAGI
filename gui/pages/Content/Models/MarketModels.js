import React, {useState, useEffect} from "react";
import styles from "@/pages/Content/Marketplace/Market.module.css";
import Image from "next/image";
import {loadingTextEffect, returnToolkitIcon} from "@/utils/utils";
import {EventBus} from "@/utils/eventBus";
// import {getModels} from "@/pages/api/DashboardService";

export default function MarketModels(){
    const [showMarketplace, setShowMarketplace] = useState(false);
    const [isLoading, setIsLoading] = useState(false)
    const [loadingText, setLoadingText] = useState("Loading Models");
    const modelTemplates = [{'name':'model 1','description':'shifting timeline across multiple time strings. Regard shifting multiple time string is the agents to be.','provider':'Replicate'},
        {'name':'model 1','description':'shifting timeline across multiple time strings. Regard shifting multiple time string is the agents to be.','provider':'Replicate'},
        {'name':'model 1','description':'shifting timeline across multiple time strings. Regard shifting multiple time string is the agents to be.','provider':'Replicate'},{'name':'model 1','description':'shifting timeline across multiple time strings. Regard shifting multiple time string is the agents to be.','provider':'Replicate'},
        {'name':'model 1','description':'shifting timeline across multiple time strings. Regard shifting multiple time string is the agents to be.','provider':'Replicate'},]

    useEffect(() => {
        loadingTextEffect('Loading Models', setLoadingText, 500);
    },[]);

    function handleTemplateClick(item) {
        const contentType = 'agent_template';
        EventBus.emit('openTemplateDetails', {item, contentType});
    }

    return(
        <div id="market_models" className={showMarketplace ? 'ml_8' : 'ml_3'}>
            <div className="w_100 overflowY_auto mxh_78vh">
                {!isLoading ? <div>
                    {modelTemplates.length > 0 ? <div className="marketplaceGrid">{modelTemplates.map((item) => (
                        <div className="market_containers cursor_pointer" key={item.id}>
                            <div>{item.name}</div>
                            <div className="color_gray lh_16 mb_8">by SuperAgi&nbsp;<Image width={14} height={14} src="/images/is_verified.svg" alt="is_verified"/></div>
                            <div className="text_ellipsis mt_6 color_gray">{item.description}</div>
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