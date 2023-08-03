import React, {useState, useEffect} from "react";
import {WidthProvider, Responsive} from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const ResponsiveGridLayout = WidthProvider(Responsive);

export default function ModelMetrics(){
    const initialLayout = [
        {i: 'total_calls', x: 0, y: 0, w: 3, h: 1},
        {i: 'total_tokens', x: 3, y: 0, w: 3, h: 1},
        {i: 'total_agents', x: 6, y: 0, w: 3, h: 1},
        {i: 'average_latency', x: 9, y: 0, w: 3, h: 1},
        {i: 'call_logs', x: 0, y: 2, w: 12, h: 8}]

    return(
        <div id="model_metrics" className="overflowY_scroll">
            <ResponsiveGridLayout
                className="layout"
                layouts={{lg: initialLayout}}
                breakpoints={{lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0}}
                cols={{lg: 12, md: 12, sm: 12, xs: 12, xxs: 12}}>
                <div key="total_calls" className="display_column_container">
                    <span className="text_14 mb_8">Total Calls</span>
                    <div className="text_60_bold display_flex justify_center align_center w_100 h_100 mb_24">0</div>
                </div>

                <div key="total_tokens" className="display_column_container">
                    <span className="text_14 mb_8">Total Tokens</span>
                    <div className="text_60_bold display_flex justify_center align_center w_100 h_100 mb_24">0</div>
                </div>

                <div key="total_agents" className="display_column_container">
                    <span className="text_14 mb_8">Total Agents</span>
                    <div className="text_60_bold display_flex justify_center align_center w_100 h_100 mb_24">0</div>
                </div>

                <div key="average_latency" className="display_column_container">
                    <span className="text_14 mb_8">Average Latency</span>
                    <div className="text_60_bold display_flex justify_center align_center w_100 h_100 mb_24">0</div>
                </div>

                <div key="call_logs" className="display_column_container">
                    <span className="text_14 mb_8">Call Logs</span>
                </div>
            </ResponsiveGridLayout>
        </div>
    )
}