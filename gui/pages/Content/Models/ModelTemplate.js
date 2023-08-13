import React, {useEffect, useState} from 'react';
import Image from "next/image";
import {EventBus} from "@/utils/eventBus";
import {getFormattedDate} from "@/utils/utils";
import AddModelMarketPlace from "./AddModelMarketPlace";
export default function ModelTemplate({env, template}){
    const [isInstalled, setIsInstalled] = useState(false);

    function handleBackClick() {
        EventBus.emit('goToMarketplace', {});
    }

    return (
        <div id="model_template">
            <div className="back_button mt_16 mb_16" onClick={() => handleBackClick()}>
                <Image src="/images/arrow_back.svg" alt="back_button" width={14} height={12}/>
                <span className="text_12 color_gray fw_500 ml_4">Back</span>
            </div>
            { !isInstalled ? (<div className="gridContainer">
                <div className="col_3 display_column_container padding_16">
                    <span className="text_20 color_white">{template.model_name}</span>
                    <span className="text_12 color_gray mt_4">by {template.model_name}</span>
                    <button className="primary_button w_100 mt_16" onClick={() => setIsInstalled(true)}>{isInstalled ? 'Installed' : 'Install'}</button>

                    <hr className="horizontal_line" />
                    <span className="text_12 color_white lh_18">{template.description}</span>
                    <hr className="horizontal_line" />

                    <span className="text_12 color_gray">Model Provider</span>
                    <span className="text_12 color_white mt_8">{template.source_name}</span>

                    <hr className="horizontal_line" />
                    <span className="text_12 color_gray">Updated At</span>
                    <span className="text_12 color_white mt_8">{getFormattedDate(template.updated_at)}</span>
                </div>
                <div className="col_9 display_column_container padding_16">hello</div>
            </div> ):(
                <AddModelMarketPlace template={template} />
                )}
        </div>
    )
}