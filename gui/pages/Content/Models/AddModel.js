import React, {useState, useEffect} from "react";
import ModelForm from "./ModelForm";

export default function AddModel({}) {
    return (
        <div id="add_model">
            <div className="row">
                <div className="col-3" />
                <div className="col-6" style={{overflowY: 'scroll', height: 'calc(100vh - 92px)', padding: '25px 20px'}}>
                    <ModelForm />
                </div>
                <div className="col-3" />
            </div>
        </div>
    )
}