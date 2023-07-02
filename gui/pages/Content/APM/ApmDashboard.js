import React, { useState, useEffect } from 'react';
import Image from "next/image";
import style from "./Apm.module.css";
import 'react-toastify/dist/ReactToastify.css';
import {getAllAgents, getAnalytics, getMetrics} from "@/pages/api/DashboardService";
import {formatNumber} from "@/utils/utils";
import * as echarts from 'echarts';

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
        },
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
        },
        {
            name: 'Banana',
            score: 30
        },
        {
            name: 'Cake',
            score: 26
        },
    ]
    const [totalCalls, setTotalCalls] = useState(0);
    const [totalTokens, setTotalTokens] = useState(0);
    const [totalRuns, setTotalRuns] = useState(0);
    const [totalAgents, setTotalAgents] = useState(0);
    const [allAgents, setAllAgents] = useState([]);
    const [allModels, setAllModels] = useState([]);

    useEffect(() => {
        const chartDom = document.getElementById('barChart');
        const myChart = echarts.init(chartDom);
        let options = {
            yAxis: {
                type: 'category',
                data: allModels.map(item => item.model),
                axisLine: {
                    show: false
                },
                axisLabel: {
                    show: true,
                    fontSize: 14,
                    fontWeight: 400,
                    color: '#FFF',
                },
            },
            xAxis: {
                type: 'value',
                show : false
            },
            series: [{
                data: allModels.map(item => item.agents),
                type: 'bar',
                barWidth: 50,
                label: {
                    show: true,
                    position: 'right',
                    fontSize: 14,
                    fontWeight: 400,
                    color: '#FFF',
                    formatter: function(params) {
                        return params.data;
                    }
                },
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{
                        offset: 0, color: '#7491EA' // color at 0% position
                    }, {
                        offset: 1, color: '#9865D9' // color at 100% position
                    }], false),
                    // No support for border radius in ECharts
                },
                emphasis: {
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{
                            offset: 0, color: '#7491EA' // emphasis color at 0% position
                        }, {
                            offset: 1, color: '#9865D9' // emphasis color at 100% position
                        }], false),
                        shadowBlur: 20,
                        shadowColor: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                animationEasing: 'elasticOut',
                animationDelayUpdate: function (idx) {
                    return idx * 5;
                }
            }],
            grid: {
                show: false,
                height: allModels.length * 60 // 60px = 50px (bar height) + 10px (gap)
            },
            tooltip: {
                show: true,
                trigger: 'axis',
                axisPointer: {
                    type: 'line'
                },
                formatter: function (params) {
                    let data = params[0];
                    return `${data.name}: ${data.value}`;
                }
            },
        };
        options && myChart.setOption(options);
    }, [allModels]);

    useEffect(() => {
        getDetails()
        const interval = setInterval(() => {
            getDetails();
        }, 10000);
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        console.log(allAgents);
        console.log(allModels)
    }, [allAgents]);

    const getDetails = () =>{
        getMetrics().then((response) => {
            const data = response.data
            setTotalCalls(data.total_calls);
            setTotalTokens(data.total_tokens);
            setTotalRuns(data.runs_completed);
        })
        getAllAgents().then((response) => {
            const data = response.data
            setTotalAgents(data.agent_details.length)
            setAllAgents(data.agent_details)
            setAllModels(data.model_info)
            console.log(response)
        })
    }

    return (
        <>
        <div className={style.apm_dashboard_container}>
            <div id="apm_dashboard" className={style.apm_dashboard}>
                <span className="text_14 mt_10">Agent Performance Monitoring</span>
                <div className="my_rows">
                    <div className="my_col_4 display_column_container">
                        <span className="text_14 mb_8">Total tokens consumed</span>
                        <div className="text_60_bold display_flex justify_center w_100 mb_24 mt_24">{formatNumber(totalTokens)}</div>
                    </div>
                    <div className="my_col_4 display_column_container">
                        <span className="text_14 mb_8">Total runs</span>
                        <div className="text_60_bold display_flex justify_center w_100 mb_24 mt_24">{formatNumber(totalRuns)}</div>
                    </div>
                    <div className="my_col_4 display_column_container">
                        <span className="text_14 mb_8">Total calls</span>
                        <div className="text_60_bold display_flex justify_center w_100 mb_24 mt_24">{formatNumber(totalCalls)}</div>
                    </div>
                </div>

                <div className="my_rows mt_8" style={{height:'565px'}}>
                    <div className="my_col_8 display_column_container h_100">
                        <div style={{display:'inline-flex',justifyContent:'space-between',width:'100%'}}>
                            <span className="text_14 mb_8">Agent & Run details</span>
                            <div className="text_14 mb_8">Select an Agent</div>
                        </div>
                    </div>
                    <div className="my_col_4">
                        <div className="display_column_container">
                            <span className="text_14 mb_8">Number of Agents</span>
                            <div className="text_60_bold display_flex justify_center w_100 mb_24 mt_24">{formatNumber(totalAgents)}</div>
                        </div>
                        <div className="display_column_container mt_8">
                            <span className="text_14 mb_8">Average tokens consumed per run</span>
                            <div className="text_60_bold display_flex justify_center w_100 mb_24 mt_24">{formatNumber(totalTokens/totalRuns)}</div>
                        </div>
                        <div className="display_column_container mt_8">
                            <span className="text_14 mb_8">Average calls made per run</span>
                            <div className="text_60_bold display_flex justify_center w_100 mb_24 mt_24">{formatNumber(totalCalls/totalRuns)}</div>
                        </div>
                    </div>
                </div>

                <div className="my_rows mt_8" style={{height:'644px'}}>
                    <div className="my_col_10">
                        <div className="my_rows" style={{height:'318px'}}>
                            <div className="my_col_6 display_column_container h_100">
                                <span className="text_14 mb_8">Most active agents</span>
                                <div className="scrollable_container">
                                    <table className="table_css mt_10">
                                        <thead>
                                        <tr style={{borderTop:'none'}}>
                                            <th className="table_header">Agent</th>
                                            <th className="table_header text_align_right">Runs <img width={14} height={14} src="/images/arrow_downward.svg" alt="arrow_down"/></th>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        {allAgents.sort((a,b) => b.runs_completed - a.runs_completed).map((agent, i) => (
                                            <tr key={i}>
                                                <td className="table_data" style={{width:'20%'}}>{agent.name}</td>
                                                <td className="table_data" style={{width:'100%',display:'inline-flex'}}>
                                                    <div className="progress-bar">
                                                        <div className="filled" style={{width: `${(agent.runs_completed/(allAgents[0].runs_completed+1))*100}%`}}></div>
                                                    </div>
                                                    <span>{agent.runs_completed}</span>
                                                </td>
                                            </tr>))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div className="my_col_6 display_column_container h_100">
                                <span className="text_14 mb_8">Most used tools</span>
                                <div className="scrollable_container">
                                    <table className="table_css mt_10">
                                        <thead>
                                        <tr style={{borderTop:'none'}}>
                                            <th className="table_header">Tool</th>
                                            <th className="table_header text_align_right">Agents <img width={14} height={14} src="/images/arrow_downward.svg" alt="arrow_down"/></th>
                                            <th className="table_header text_align_right">Iterations</th>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        {items.map((item, i) => (
                                            <tr key={i}>
                                                <td className="table_data" style={{width:'50%'}}>{item.name}</td>
                                                <td className="table_data text_align_right" style={{width:'25%'}}>{item.score}</td>
                                                <td className="table_data text_align_right" style={{width:'25%'}}>{item.score}</td>
                                            </tr>
                                        ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                        <div className="my_rows mt_8" style={{height:'318px'}}>
                            <div className="my_col_6 display_column_container h_100">
                                <span className="text_14 mb_8">Calls per run by agent</span>
                                <div className="scrollable_container">
                                    <table className="table_css mt_10">
                                        <thead>
                                        <tr style={{borderTop:'none'}}>
                                            <th className="table_header">Agent</th>
                                            <th className="table_header text_align_right">Average calls per runs <img width={14} height={14} src="/images/arrow_downward.svg" alt="arrow_down"/></th>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        {allAgents.map((agent, i) => (
                                            <tr key={i}>
                                                <td className="table_data" style={{width:'70%'}}>{agent.name}</td>
                                                <td className="table_data text_align_right" style={{width:'30%'}}>{(agent.total_calls/agent.runs_completed).toFixed(1)}</td>
                                            </tr>
                                        ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div className="my_col_6 display_column_container h_100">
                                <span className="text_14 mb_8">Tokens per run by agent</span>
                                <div className="scrollable_container">
                                    <table className="table_css mt_10">
                                        <thead>
                                        <tr style={{borderTop:'none'}}>
                                            <th className="table_header">Agent</th>
                                            <th className="table_header text_align_right">Average Tokens per runs <img width={14} height={14} src="/images/arrow_downward.svg" alt="arrow_down"/></th>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        {allAgents.map((agent, i) => (
                                            <tr key={i}>
                                                <td className="table_data" style={{width:'70%'}}>{agent.name}</td>
                                                <td className="table_data text_align_right" style={{width:'30%'}}>{(agent.total_tokens/agent.runs_completed).toFixed(1)}</td>
                                            </tr>
                                        ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="my_col_2 h_100">
                        <div className="my_col_12 display_column_container h_100">
                            <span className="text_14 mb_8">Active Runs</span>
                            <div className="scrollable_container gap_8">
                                {items.map((item,i) => (
                                    <div className="active_runs">
                                        <span className="text_14">{item.name}</span>
                                        <span className="text_14 mt_6">{item.score} . {item.score}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="my_rows mt_8">
                    {/*<div className="my_col_6 display_column_container">*/}
                    {/*    <span className="text_14 mb_8">Models used by agents</span>*/}
                    {/*    <div className="w_100" style={{display: 'flex', flexDirection: 'column', justifyContent: 'flex-start', padding: '0', alignItems: 'flex-start'}}>*/}
                    {/*        {items.map((item, i) => (*/}
                    {/*            <div className="mb_6 mt_6 w_100" style={{display: 'flex', alignItems: 'center', border: 'none'}} key={i}>*/}
                    {/*                <div style={{width: '20%', whiteSpace: 'normal'}}> /!* Set a fixed width for the name *!/*/}
                    {/*                    <span className="text_14 mb_8">{item.name}</span>*/}
                    {/*                </div>*/}
                    {/*                <div className="bar-chart" style={{flexGrow: 1, height: '50px', marginRight: '10px'}}> /!* Let the bar take up the majority of the space *!/*/}
                    {/*                    <div className="bar" style={{width: `${(item.score/50)*100}%`, height: '100%'}}/>*/}
                    {/*                </div>*/}
                    {/*                <div style={{width: '10%', display: 'flex', justifyContent: 'flex-end'}}> /!* Allocate fixed width for the score and align it to the right *!/*/}
                    {/*                    <span className="text_14">{item.score}</span>*/}
                    {/*                </div>*/}
                    {/*            </div>*/}
                    {/*        ))}*/}
                    {/*    </div>*/}
                    {/*</div>*/}
                    <div className="my_col_6 display_column_container">
                        <span className="text_14 mb_8">Models used by agents</span>
                        <div id="barChart" style={{width: '100%', height: 300}}></div>
                    </div>
                </div>
            </div>
        </div>
        </>
    )
}