import React, {useState, useEffect} from "react";
import Image from "next/image";

export default function ModelInfo(modelDetails){
    const [modelData, setModelData] = useState(modelDetails?.modelDetails)
    return(
        <div id="model_info" className="text_12">
            <hr className="horizontal_line padding_0" />
            <div className="row">
                <div className="col-3" />
                <div className="col-6 col-6-scrollable vertical_containers">
                    <span>Installation Type</span>
                    <div className="horizontal_container mt_8 color_white gap_4">
                        {modelData === 'Marketplace' && <Image width={16} height={16} src="/images/marketplace_logo.png" alt="marketplace_logo" />}
                        <span>{modelData.type}</span>
                    </div>

                    <span className="mt_24">Model Provider</span>
                    <span className="mt_8 color_white">{modelData.model_provider}</span>

                    {modelData.end_point && <div className="vertical_containers">
                        <span className="mt_24">Model Endpoint</span>
                        <span className="mt_8 color_white">{modelData.end_point}</span>
                    </div>}

                    <span className="mt_24">Token Limit</span>
                    <input className="input_medium mt_8" type="number" placeholder="Enter Model Token Limit" value={modelData.token_limit} disabled/>
                </div>
                <div className="col-3" />
            </div>
        </div>
    )
}