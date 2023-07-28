import React from 'react';
import Image from 'next/image';
import {createInternalId, returnToolkitIcon, excludedToolkits} from "@/utils/utils";

export default function Models ({sendModelData, models}) {
    return (
        <div id="models_sidebar">
            <div className="container">
                <p className="text_14 lh_16 mt_8 mb_13 ml_8">Models</p>
                <div className="w_100 mb_10">
                    <button className="secondary_button w_100" onClick={() => sendModelData({
                        id: -8,
                        name: "new model",
                        contentType: "Add_Model",
                        internalId: createInternalId()
                    })}>
                        + Add Model
                    </button>
                </div>
                {models && models.length > 0 ? (
                    <div style={{overflowY:'scroll', height:'100%'}}>
                        {models.map((model, index) =>
                            model.name !== null && (
                                <div key={index} className="item_box mb_10" onClick={() => sendModelData(model)}>
                                    <div className="row">
                                        <div className="col-12">
                                            <div style={{display: 'flex', alignItems: 'center', justifyContent: 'flex-start', padding: '5px'}}>
                                                <div style={{marginLeft: '8px'}}>
                                                    <div className="item_name">{model.name}</div>
                                                    <div className="item_publisher">by SuperAGI</div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                    </div>
                ) : (
                    <div className="form_label mt_20 horizontal_container justify_center">
                        No Models found
                    </div>
                )}
            </div>
        </div>
    )
}
