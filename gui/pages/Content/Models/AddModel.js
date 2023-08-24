import React, {useEffect, useState} from "react";
import ModelForm from "./ModelForm";

export default function AddModel(internalId){
    return(
        <div id="add_model">
            <div className="row">
                <div className="col-3" />
                <div className="col-6 col-6-scrollable">
                    <ModelForm internalId={internalId}/>
                </div>
                <div className="col-3" />
            </div>
        </div>
    )
}