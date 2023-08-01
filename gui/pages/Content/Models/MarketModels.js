import React, {useState, useEffect} from "react";
import styles from "@/pages/Content/Marketplace/Market.module.css";
import Image from "next/image";
import {returnToolkitIcon} from "@/utils/utils";

export default function MarketModels(){
    const [showMarketplace, setShowMarketplace] = useState(false);
    const [isLoading, setIsLoading] = useState(true)
    const [loadingText, setLoadingText] = useState("Loading Models");
    const modelTemplates = [{'name':'model 1'}]

    return(
        <div id="market_models" className={showMarketplace ? 'ml_8' : 'ml_3'}>
            <div className="w_100 overflowY_auto mxh_78vh">
                {!isLoading ? <div>
                    {toolTemplates.length > 0 ? <div className={styles.resources}>{toolTemplates.map((item) => (
                        <div className="market_tool cursor_pointer" key={item.id} onClick={() => handleTemplateClick(item)}>
                            <div className="horizontal_container overflow_auto">
                                <Image className="tool_icon" width={40} height={40} src={returnToolkitIcon(item.name)} alt="tool-icon"/>
                                <div className="ml_12 mb_8">
                                    <div>{item.name}</div>
                                    <div className="color_gray lh_16">by SuperAgi&nbsp;<Image width={14} height={14} src="/images/is_verified.svg" alt="is_verified"/></div>
                                </div>
                            </div>
                            <div className="text_ellipsis mt_6 color_gray">{item.description}</div>
                        </div>
                    ))}</div> : <div className="center_container mt_40">
                        <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions"/>
                        <span className="feed_title mt_8">No Tools found!</span>
                    </div>}
                </div> : <div className="horizontal_container_center h_75vh">
                    <div className="signInInfo text_16 ff_sourceCode">{loadingText}</div>
                </div>}
            </div>
        </div>
    )
}