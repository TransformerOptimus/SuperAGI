import React, {useState, useEffect} from "react";

export default function ModelInfo(modelDetails){
    return(
        <div id="model_info">
            <div className="row">
                <div className="col-3" />
                <div className="col-6 col-6-scrollable">
                    <span>{modelDetails.name}</span>
                </div>
                <div className="col-3" />
            </div>
        </div>
    )
}