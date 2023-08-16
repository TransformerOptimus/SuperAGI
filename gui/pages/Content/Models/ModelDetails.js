import React, {useState, useEffect} from "react";
import Image from "next/image";
import ModelMetrics from "./ModelMetrics";
import ModelInfo from "./ModelInfo";
import {fetchModel} from "@/pages/api/DashboardService";

export default function ModelDetails({modelId, modelName}){
    const [modelDetails, setModelDetails] = useState([])
    const [selectedOption, setSelectedOption] = useState('metrics')

    useEffect(() => {
        const fetchModelDetails = async () => {
            try {
                const response = await fetchModel(modelId);
                console.log(response.data)
                setModelDetails(response.data)
            } catch(error) {
                console.log(`Error Fetching the Details of the Model ${modelName}`, error)
            }
        };

        fetchModelDetails().then().catch();
    },[])

    return(
        <div id="model_details" className="ml_3 mr_3">
            <div className="vertical_containers padding_16_8">
                <span className="text_16">{ modelDetails.name ? (modelDetails.name.split('/')[1] || modelDetails.name) : ""}</span>
                <span className="text_12 color_gray mt_8 lh_18">{modelDetails.description}</span>
                <div className="horizontal_container gap_4 mt_16 mb_2">
                    <button className={selectedOption === 'metrics' ? 'tab_button_selected' : 'tab_button'}
                            onClick={() => setSelectedOption('metrics')}>Metrics</button>
                    <button className={selectedOption === 'details' ? 'tab_button_selected' : 'tab_button'}
                            onClick={() => setSelectedOption('details')}>Details</button>
                </div>
            </div>
            {selectedOption === 'metrics' && <ModelMetrics modelDetails={modelDetails} />}
            {selectedOption === 'details' && <ModelInfo modelDetails={modelDetails} />}
        </div>
    )
}