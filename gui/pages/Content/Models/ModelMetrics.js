import React, {useState, useEffect} from "react";
import {fetchModelData} from "@/pages/api/DashboardService";
import {formatNumber, returnToolkitIcon} from "@/utils/utils";
import Image from "next/image";

export default function ModelMetrics(modelDetails) {
    const [modelData, setModelData] = useState(modelDetails);
    const [modelMeta, setModelMeta] = useState([])
    const [modelRunData, setModelRunData] = useState([])

    useEffect(()=>{
        setModelData(modelDetails.modelDetails);
    },[modelDetails])

    useEffect(()=>{
        getModelInfo()
    },[modelData, modelDetails])

    const getModelInfo = () =>{
        if(modelData.name !== undefined){
            fetchModelData(modelData.name).then((response)=>{
                console.log(response)
                setModelMeta(response.data)
                setModelRunData(response.data.runs)
            })
        }
    }

    return(
        <div id="model_metrics" className="overflowY_scroll">
            <div className="my_rows">
                <div className="my_col_4 display_column_container">
                    <span className="text_14 mb_8">Total Calls</span>
                    <div className="text_60_bold display_flex justify_center align_center w_100 h_100 mb_24">{modelMeta.total_calls}</div>
                </div>

                <div className="my_col_4 display_column_container">
                    <span className="text_14 mb_8">Total Tokens</span>
                    <div className="text_60_bold display_flex justify_center align_center w_100 h_100 mb_24">{formatNumber(modelMeta.total_tokens)}</div>
                </div>

                <div className="my_col_4 display_column_container">
                    <span className="text_14 mb_8">Total Agents</span>
                    <div className="text_60_bold display_flex justify_center align_center w_100 h_100 mb_24">{modelMeta.total_agents}</div>
                </div>
            </div>
            <div className="my_rows mt_8">
                <div className="my_col_12 display_column_container h_60vh">
                    <span className="text_14 mb_8">Call Logs</span>
                    {modelRunData.length === 0 ?
                        <div className="vertical_container align_center mt_70 w_100">
                            <img src="/images/no_permissions.svg" width={190} height={74} alt="No Data"/>
                            <span className="text_12 color_white mt_6">No Used Tools Found</span>
                        </div> : <div className="scrollable_container">
                            <table className="table_css margin_0 padding_0">
                                <thead>
                                <tr style={{borderTop: 'none'}}>
                                    <th className="table_header w_20">Log Timestamp</th>
                                    <th className="table_header w_20">Agent Name</th>
                                    <th className="table_header w_20">Run Name</th>
                                    <th className="table_header w_20">Tool</th>
                                    <th className="table_header text_align_right w_20">Tokens Used</th>
                                </tr>
                                </thead>
                            </table>

                            <div className="overflow_auto w_100">
                                <table className="table_css margin_0">
                                    <tbody>
                                    {modelRunData.map((data, index) => (
                                        <tr key={index}>
                                            <td className="table_data w_20">{data.created_at.slice(0, 19).replace('T', ' ')}</td>
                                            <td className="table_data w_20">{data.agent_name}</td>
                                            <td className="table_data w_20">{data.agent_execution_name}</td>
                                            <td className="table_data" style={{width: '100%', display: 'flex', alignItems: 'center'}}>
                                                {data.tool_used && <Image className="image_class bg_black" width={20} height={20}
                                                       src={returnToolkitIcon(data.toolkit_name)} alt="tool-icon"/>}
                                                <span>{data.tool_used ? data.tool_used : '-NA-'}</span>
                                            </td>
                                            <td className="table_data text_align_right w_20">{formatNumber(data.tokens_consumed)}</td>
                                        </tr>
                                    ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>}
                </div>
            </div>
        </div>
    )
}