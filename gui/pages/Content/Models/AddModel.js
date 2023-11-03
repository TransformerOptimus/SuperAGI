import React, {useEffect, useState} from "react";
import ModelForm from "./ModelForm";

export default function AddModel({internalId, getModels, sendModelData, env}){

    return(
        <div id="add_model">
            <div className="row">
                <div className="col-3" />
                <div className="col-6 col-6-scrollable">
                    <ModelForm internalId={internalId} getModels={getModels} sendModelData={sendModelData} env={env}/>
                </div>
                <div className="col-3" />
            </div>
        </div>
    )
}