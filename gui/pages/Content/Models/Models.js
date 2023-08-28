import React from "react";
import 'react-toastify/dist/ReactToastify.css';
import {createInternalId} from "@/utils/utils";

export default function Models({sendModelData, models}){

    const handleModelSelect = (model) => {
        model.contentType = 'Model'
        sendModelData(model)
    }

    return(
        <div id="models">
            <div className="container">
                <p className="text_14 mt_8 mb_12 ml_8">Models</p>
                <div className="w_100 mb_10">
                    <button className="secondary_button w_100"
                            onClick={() => sendModelData({id: -5, name: "new model", contentType: "Add_Model", internalId: createInternalId()})}>
                        + Add Model
                    </button>
                </div>

                {models && models.length > 0 ? <div className="vertical_selection_scroll w_100">
                    {models.map((model, index) => (
                        <div key={index}>
                            <div className="sidebar_box flex_dir_col align_start w_100" onClick={() => handleModelSelect(model)}>
                                <div className="text_ellipsis"><span className="text_13 lh_18 color_white text_ellipsis">{model.name.split('/')[1] || model.name}</span></div>
                                <div className="text_12 color_gray mt_4">by {model.name.includes('/') ? model.name.split('/')[0] : model.model_provider} · {model.model_provider}</div>
                            </div>
                        </div>
                    ))}
                </div> : <div className="form_label mt_20 horizontal_container justify_center">No Models found</div>}
            </div>
        </div>
    )
}