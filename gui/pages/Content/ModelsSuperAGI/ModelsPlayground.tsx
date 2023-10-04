import React, {useState, useContext, useEffect} from "react";
import ModelsInputPlayground from "@/app/pages/Models/ModelsInputPlayground";
import ModelsOutputPlayground from "@/app/pages/Models/ModelsOutputPlayground";
import {getAllModels} from "@/app/api/DashboardService";
import {ModelDetail} from "@/app/pages/Types/ModelsTypes";
import {ModelLog} from "@/app/pages/Types/LogsTypes";

export default function ModelsPlayground({modelDetails}: {modelDetails: ModelDetail}) {
    const [modelResult, setModelResult] = useState('');
    const [modelLogs, setModelLogs] = useState<ModelLog[]>([]);

    return (
        <div id="models_playground" className="horizontal_container_responsiveness w-full">
            <div id="input_part" className="flex-1 pr-4 border_right">
                <span className="text_20 fw_500 text_color">Input</span>
                <ModelsInputPlayground // @ts-ignore
                    data={modelDetails.config} model_id={modelDetails._id} setModelResult={setModelResult} setModelLogs={setModelLogs}/>
            </div>
            <div id="output_part" className="flex-1 ml-4">
                <span className="text_20 fw_500 text_color">Output</span>
                <ModelsOutputPlayground result={modelResult} // @ts-ignore
                                        logs={modelLogs}/>
            </div>
        </div>
    )
}
