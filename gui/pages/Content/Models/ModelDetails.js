import React, {useState, useEffect} from "react";
import Image from "next/image";
import ModelMetrics from "./ModelMetrics";

export default function ModelDetails({modelId, modelName}){

    return(
        <div id="model_details" className="vertical_containers">
            <span className="text_16">{modelName}</span>
            <span className="text_12 color_gray">{modelName}</span>
            <ModelMetrics />
        </div>
    )
}