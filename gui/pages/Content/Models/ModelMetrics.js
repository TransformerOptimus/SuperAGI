import React, {useState, useEffect} from "react";

export default function ModelMetrics(){

    return(
        <div id="model_metrics" className="overflowY_scroll">
            <div className="my_rows">
                <div className="my_col_3 display_column_container">
                    <span className="text_14 mb_8">Total Calls</span>
                    <div className="text_60_bold display_flex justify_center align_center w_100 h_100 mb_24">0</div>
                </div>

                <div className="my_col_3 display_column_container">
                    <span className="text_14 mb_8">Total Tokens</span>
                    <div className="text_60_bold display_flex justify_center align_center w_100 h_100 mb_24">0</div>
                </div>

                <div className="my_col_3 display_column_container">
                    <span className="text_14 mb_8">Total Agents</span>
                    <div className="text_60_bold display_flex justify_center align_center w_100 h_100 mb_24">0</div>
                </div>

                <div className="my_col_3 display_column_container">
                    <span className="text_14 mb_8">Average Latency</span>
                    <div className="text_60_bold display_flex justify_center align_center w_100 h_100 mb_24">0</div>
                </div>
            </div>
            <div className="my_rows mt_8">
                <div className="my_col_12 display_column_container h_60vh">
                    <span className="text_14 mb_8">Call Logs</span>
                </div>
            </div>
        </div>
    )
}