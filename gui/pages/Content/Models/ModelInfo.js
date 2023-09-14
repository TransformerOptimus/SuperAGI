import React, {useState, useEffect} from "react";
import Image from "next/image";

export default function ModelInfo({modelDetails, goToTab}){

    return(
        <div id="model_info" className="text_12">
            <hr className="horizontal_line padding_0" />
            <div className="row">
                <div className="col-3" />
                <div className="col-6 col-6-scrollable vertical_containers">
                    <div className="horizontal_container align_start info_box mb_24 gap_6">
                        <Image width={16} height={16} src="/images/icon_info.svg" alt="info-icon" />
                        <div className="vertical_containers">
                            <span className="text_12 color_white lh_16">Please follow the ReadMe provided to setup this model and start using it.</span>
                            <button className="secondary_button_small w_fit_content mt_16" onClick={() => goToTab("readme")}>Go to Readme<Image src="/images/open_in_new.svg" alt="deploy_icon" width={12} height={12} className="ml_4" /></button>
                        </div>
                    </div>

                    <span>Installation Type</span>
                    <div className="horizontal_container mt_8 color_white gap_4">
                        {modelDetails === 'Marketplace' && <Image width={16} height={16} src="/images/marketplace_logo.png" alt="marketplace_logo" />}
                        <span>{modelDetails.type}</span>
                    </div>

                    <span className="mt_24">Model Provider</span>
                    <span className="mt_8 color_white">{modelDetails.model_provider}</span>

                    {modelDetails.end_point && <div className="vertical_containers">
                        <span className="mt_24">Model Endpoint</span>
                        <span className="mt_8 color_white">{modelDetails.end_point}</span>
                    </div>}

                    <span className="mt_24">Token Limit</span>
                    <input className="input_medium mt_8" type="number" placeholder="Enter Model Token Limit" value={modelDetails.token_limit} disabled/>
                </div>
                <div className="col-3" />
            </div>
        </div>
    )
}