import React, {useEffect, useState} from 'react';
import Image from "next/image";
import {EventBus} from "@/utils/eventBus";
import {getFormattedDate, modelIcon} from "@/utils/utils";
import AddModelMarketPlace from "./AddModelMarketPlace";
export default function ModelTemplate({env, template}){
    const [isInstalled, setIsInstalled] = useState(false);

    function handleBackClick() {
        EventBus.emit('goToMarketplace', {});
    }

    function handleInstallClick() {
        if (window.location.href.toLowerCase().includes('marketplace')) {
            if (env === 'PROD') {
                window.open(`https://app.superagi.com/`, '_self');
            } else {
                window.location.href = '/';
            }
        }
        else {
            setIsInstalled(true)
        }
    }

    return (
        <div id="model_template">
            <div className="back_button mt_16 mb_16" onClick={() => isInstalled ? setIsInstalled(false) : handleBackClick()}>
                <Image src="/images/arrow_back.svg" alt="back_button" width={14} height={12}/>
                <span className="text_12 color_gray fw_500 ml_4">Back</span>
            </div>
            { !isInstalled ? (<div className="gridContainer">
                <div className="col_3 display_column_container padding_16">
                    <span className="text_20 color_white">{template.model_name}</span>
                    <span className="text_12 color_gray mt_4">by {template.model_name.includes('/') ? template.model_name.split('/')[0] : template.provider}</span>
                    <button className="primary_button w_100 mt_16" disabled={template.is_installed} onClick={() => handleInstallClick()}>
                        <Image width={16} height={16} src={template.is_installed ? '/images/tick.svg' : '/images/marketplace_download.svg'} alt="download-icon" />
                        <span className="ml_8">{template.is_installed ? 'Installed' : 'Install'}</span>
                    </button>

                    <hr className="horizontal_line" />
                    <span className="text_12 color_white lh_18">{template.description}</span>
                    <hr className="horizontal_line" />

                    <span className="text_12 color_gray">Model Provider</span>
                    <div className="tags mt_8">
                        <Image width={18} height={18} src={modelIcon(template.provider)} alt="logo-icon" />
                        <span className="text_12 color_white ml_4">{template.provider}</span>
                    </div>

                    <hr className="horizontal_line" />
                    <span className="text_12 color_gray">Updated At</span>
                    <span className="text_12 color_white mt_8">{getFormattedDate(template.updated_at)}</span>
                </div>
                <div className="col_9 display_column_container padding_16 color_white text_12 lh_18" dangerouslySetInnerHTML={{ __html: template.model_features }} />
            </div> ):(
                <AddModelMarketPlace template={template} />
                )}
        </div>
    )
}