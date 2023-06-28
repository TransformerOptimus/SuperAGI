import React, { useState } from 'react';
import Image from "next/image";
import style from "./Apm.module.css";
import 'react-toastify/dist/ReactToastify.css';

export default function ApmDashboard() {
    const items = [
        {
            name: 'Apple',
            score: 40
        },
        {
            name: 'Banana',
            score: 30
        },
        {
            name: 'Cake',
            score: 26
        },
        {
            name: 'Pizza',
            score: 16
        }
    ]
    const headers = ["Agents","Runs"]
    return (
        <>
        <div className={style.apm_dashboard_container}>
            <div id="apm_dashboard" className={style.apm_dashboard}>
                <span className="text_14 mt_10">Agent Performance Monitoring</span>
                <div className="my_rows">
                    <div className="my_col_4 display_column_container">
                        <span className="text_14 mb_8">Total tokens consumed</span>
                        <div className="text_60_bold display_flex justify_center w_100 mb_24 mt_24">9.5K</div>
                    </div>
                    <div className="my_col_4 display_column_container">
                        <span className="text_14 mb_8">Total runs</span>
                        <div className="text_60_bold display_flex justify_center w_100 mb_24 mt_24">78</div>
                    </div>
                    <div className="my_col_4 display_column_container">
                        <span className="text_14 mb_8">Total calls</span>
                        <div className="text_60_bold display_flex justify_center w_100 mb_24 mt_24">78</div>
                    </div>
                </div>

                <div className="my_rows mt_8" style={{height:'565px'}}>
                    <div className="my_col_8 display_column_container h_100">
                        <span className="text_14 mb_8">Agent & Run details</span>
                        <div className="text_60_bold display_flex justify_center w_100 mb_24 mt_24">9.5K</div>
                    </div>
                    <div className="my_col_4">
                        <div className="display_column_container">
                            <span className="text_14 mb_8">Average run time</span>
                            <div className="text_60_bold display_flex justify_center w_100 mb_24 mt_24">2.3min</div>
                        </div>
                        <div className="display_column_container mt_8">
                            <span className="text_14 mb_8">Average tokens consumed per run</span>
                            <div className="text_60_bold display_flex justify_center w_100 mb_24 mt_24">2.2K</div>
                        </div>
                        <div className="display_column_container mt_8">
                            <span className="text_14 mb_8">Average calls made per run</span>
                            <div className="text_60_bold display_flex justify_center w_100 mb_24 mt_24">34</div>
                        </div>
                    </div>
                </div>

                <div className="my_rows mt_8" style={{height:'644px'}}>
                    <div className="my_col_10">
                        <div className="my_rows" style={{height:'318px'}}>
                            <div className="my_col_6 display_column_container h_100">
                                <span className="text_14 mb_8">Most active agents</span>
                                <table className="table_css">
                                    <thead>
                                    <tr>
                                        <th className="table_header">Agent</th>
                                        <th className="table_header">Runs <img width={12} height={12} src="/images/arrow_downward.svg" alt="arrow_down"/></th>
                                    </tr>
                                    </thead>
                                    <tbody>
                                    {items.map((item, i) => (
                                        <tr key={i}>
                                            <td className="table_data">{item.name}</td>
                                            <td className="table_data">{item.score}</td>
                                        </tr>
                                    ))}
                                    </tbody>
                                </table>
                            </div>
                            <div className="my_col_6 display_column_container h_100">
                                <span className="text_14 mb_8">Most active agents</span>
                                <div className="text_60_bold display_flex justify_center w_100 mb_24 mt_24">34</div>
                            </div>
                        </div>
                        <div className="my_rows mt_8" style={{height:'318px'}}>
                            <div className="my_col_6 display_column_container h_100">
                                <span className="text_14 mb_8">Most active agents</span>
                                <div className="text_60_bold display_flex justify_center w_100 mb_24 mt_24">34</div>
                            </div>
                            <div className="my_col_6 display_column_container h_100">
                                <span className="text_14 mb_8">Most active agents</span>
                                <div className="text_60_bold display_flex justify_center w_100 mb_24 mt_24">34</div>
                            </div>
                        </div>
                    </div>
                    <div className="my_col_2 h_100">
                        <div className="my_col_12 display_column_container h_100">
                            <span className="text_14 mb_8">Most active agents</span>
                        </div>
                    </div>
                </div>

                <div className="my_rows mt_8">
                    <div className="my_col_6 display_column_container">
                        <div className="bar-chart w_100">
                            {items.map((item, i) => (
                                <div className="bar" key={i} style={{width: `${(item.score/50)*100}%`}}>
                                    {item.name}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        </>
    )
}