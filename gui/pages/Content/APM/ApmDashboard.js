import React, {useState, useEffect, useCallback, useRef} from 'react';
import Image from "next/image";
import style from "./Apm.module.css";
import 'react-toastify/dist/ReactToastify.css';
import {getActiveRuns, getAgentRuns, getAllAgents, getToolsUsage, getMetrics} from "@/pages/api/DashboardService";
import {formatNumber, formatTime, returnToolkitIcon} from "@/utils/utils";
import {BarGraph} from "./BarGraph.js";
import {WidthProvider, Responsive} from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const ResponsiveGridLayout = WidthProvider(Responsive);

export default function ApmDashboard() {
  const [agentDetails, setAgentDetails] = useState([]);
  const [tokenDetails, setTokenDetails] = useState([]);
  const [runDetails, setRunDetails] = useState(0);
  const [allAgents, setAllAgents] = useState([]);
  const [dropdown1, setDropDown1] = useState(false);
  const [dropdown2, setDropDown2] = useState(false);
  const [dropdown3, setDropDown3] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('Select an Agent');
  const [selectedAgentIndex, setSelectedAgentIndex] = useState(-1);
  const [selectedAgentRun, setSelectedAgentRun] = useState([]);
  const [activeRuns, setActiveRuns] = useState([]);
  const [selectedAgentDetails, setSelectedAgentDetails] = useState(null);
  const [toolsUsed, setToolsUsed] = useState([]);
  const [showToolTip, setShowToolTip] = useState(false);
  const [toolTipIndex, setToolTipIndex] = useState(-1);
  const initialLayout = [
    {i: 'total_agents', x: 0, y: 0, w: 3, h: 1.5},
    {i: 'total_tokens', x: 3, y: 0, w: 3, h: 1.5},
    {i: 'total_runs', x: 6, y: 0, w: 3, h: 1.5},
    {i: 'active_runs', x: 9, y: 0, w: 3, h: 2},
    {i: 'most_used_tools', x: 9, y: 1, w: 3, h: 2},
    {i: 'models_by_agents', x: 0, y: 1, w: 3, h: 2.5},
    {i: 'runs_by_model', x: 3, y: 1, w: 3, h: 2.5},
    {i: 'tokens_by_model', x: 6, y: 1, w: 3, h: 2.5},
    {i: 'agent_details', x: 0, y: 2, w: 12, h: 2.5},
    {i: 'total_tokens_consumed', x: 0, y: 3, w: 4, h: 2},
    {i: 'total_calls_made', x: 4, y: 3, w: 4, h: 2},
    {i: 'tokens_consumed_per_call', x: 8, y: 3, w: 4, h: 2},
  ];
  const storedLayout = localStorage.getItem('myLayoutKey');
  const [layout, setLayout] = useState(storedLayout !== null ? JSON.parse(storedLayout) : initialLayout);
  const firstUpdate = useRef(true);

  const onLayoutChange = (currentLayout) => {
    setLayout(currentLayout);
  };

  const onClickLayoutChange = () => {
    localStorage.setItem('myLayoutKey', JSON.stringify(initialLayout));
    setLayout(initialLayout);
  }

  useEffect(() => {
    if (!firstUpdate.current) {
      localStorage.setItem('myLayoutKey', JSON.stringify(layout));
    } else {
      firstUpdate.current = false;
    }
  }, [layout]);

  const assignDefaultDataPerModel = (data, modelList) => {
    const modelsInData = data.map(item => item.name);
    modelList.forEach((model) => {
      if (!modelsInData.includes(model)) {
        data.push({name: model, value: 0});
      }
    });
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsResponse, agentsResponse, activeRunsResponse, toolsUsageResponse] = await Promise.all([getMetrics(), getAllAgents(), getActiveRuns(), getToolsUsage()]);
        const models = ['gpt-4', 'gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-4-32k', 'google-palm-bison-001'];

        assignDefaultDataPerModel(metricsResponse.data.agent_details.model_metrics, models);
        assignDefaultDataPerModel(metricsResponse.data.tokens_details.model_metrics, models);
        assignDefaultDataPerModel(metricsResponse.data.run_details.model_metrics, models);

        setAgentDetails(metricsResponse.data.agent_details);
        setTokenDetails(metricsResponse.data.tokens_details);
        setRunDetails(metricsResponse.data.run_details);
        setAllAgents(agentsResponse.data.agent_details);
        setActiveRuns(activeRunsResponse.data);
        setToolsUsed(toolsUsageResponse.data);
      } catch (error) {
        console.log(`Error in fetching data: ${error}`);
      }
    }

    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectedAgent = useCallback((index, name) => {
    setDropDown1(false)
    setDropDown2(false)
    setDropDown3(false)
    setSelectedAgent(name)
    setSelectedAgentIndex(index)
    const agentDetails = allAgents.find(agent => agent.agent_id === index);
    setSelectedAgentDetails(agentDetails);

    getAgentRuns(index).then((response) => {
      const data = response.data;
      setSelectedAgentRun(data);
    }).catch((error) => console.error(`Error in fetching agent runs: ${error}`));
  }, [allAgents]);

  useEffect(() => handleSelectedAgent(selectedAgentIndex, selectedAgent), [allAgents]);

  useEffect(() => {
    if (allAgents.length > 0 && selectedAgent === 'Select an Agent') {
      const lastAgent = allAgents[allAgents.length - 1];
      handleSelectedAgent(lastAgent.agent_id, lastAgent.name);
    }
  }, [allAgents, selectedAgent, handleSelectedAgent]);

  const setToolTipState = (state, index) => {
    setShowToolTip(state)
    setToolTipIndex(index)
  }

  return (
    <div className={style.apm_dashboard_container}>
      <div id="apm_dashboard" className={style.apm_dashboard}>
        <div className="horizontal_space_between w_100 align_center padding_0_8">
          <span className="text_14 mt_6 ml_6">Agent Performance Monitoring</span>
          {/*<button onClick={onClickLayoutChange} className="primary_button">Reset</button>*/}
        </div>
        <ResponsiveGridLayout
          className="layout"
          layouts={{lg: layout}}
          onLayoutChange={onLayoutChange}
          breakpoints={{lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0}}
          cols={{lg: 12, md: 12, sm: 12, xs: 12, xxs: 12}}>
          <div key="total_agents" className="display_column_container">
            <span className="text_14 mb_8">Total Agents</span>
            <div
              className="text_60_bold display_flex justify_center align_center w_100 h_100 mb_24 mt_24">{formatNumber(agentDetails.total_agents)}</div>
          </div>
          <div key="total_tokens" className="display_column_container">
            <span className="text_14 mb_8">Total tokens consumed</span>
            <div
              className="text_60_bold display_flex justify_center align_center w_100 h_100 mb_24 mt_24">{formatNumber(tokenDetails.total_tokens)}</div>
          </div>
          <div key="total_runs" className="display_column_container">
            <span className="text_14 mb_8">Total runs</span>
            <div
              className="text_60_bold display_flex justify_center align_center w_100 h_100 mb_24 mt_24">{formatNumber(runDetails.total_runs)}</div>
          </div>

          <div key="models_by_agents" className="display_column_container">
            <span className="text_14 mb_8">Number of Agents per model</span>
            {agentDetails.model_metrics && agentDetails.model_metrics.length > 0
              ? <><BarGraph data={agentDetails.model_metrics} type="value" color="#3C7EFF"/>
                <div className="horizontal_container mt_10">
                  <span className="bar_label_dot" style={{backgroundColor: '#3C7EFF'}}></span>
                  <span className="bar_label_text">Models</span>
                </div>
              </>
              : <div className="vertical_container align_center mt_80 w_100">
                <img src="/images/no_permissions.svg" width={190} height={74} alt="No Data"/>
                <span className="text_12 color_white mt_6">No Agents Found</span>
              </div>}
          </div>

          <div key="runs_by_model" className="display_column_container">
            <span className="text_14 mb_8">Number of Runs per Model</span>
            {runDetails.model_metrics && runDetails.model_metrics.length > 0
              ? <><BarGraph data={runDetails.model_metrics} type="value" color="#3C7EFF"/>
                <div className="horizontal_container mt_10">
                  <span className="bar_label_dot" style={{backgroundColor: '#3C7EFF'}}></span>
                  <span className="bar_label_text">Models</span>
                </div>
              </>
              : <div className="vertical_container align_center mt_80 w_100">
                <img src="/images/no_permissions.svg" width={190} height={74} alt="No Data"/>
                <span className="text_12 color_white mt_6">No Agents Found</span>
              </div>}
          </div>

          <div key="tokens_by_model" className="display_column_container">
            <span className="text_14 mb_8">Total Tokens consumed by models</span>
            {tokenDetails.model_metrics && tokenDetails.model_metrics.length > 0
              ? <><BarGraph data={tokenDetails.model_metrics} type="value" color="#3C7EFF"/>
                <div className="horizontal_container mt_10">
                  <span className="bar_label_dot" style={{backgroundColor: '#3C7EFF'}}></span>
                  <span className="bar_label_text">Models</span>
                </div>
              </>
              : <div className="vertical_container align_center mt_80 w_100">
                <img src="/images/no_permissions.svg" width={190} height={74} alt="No Data"/>
                <span className="text_12 color_white mt_6">No Agents Found</span>
              </div>}
          </div>

          <div key="most_used_tools" className="display_column_container">
            <span className="text_14 mb_8">Most used tools</span>
            {toolsUsed.length === 0 ?
              <div className="vertical_container align_center mt_70 w_100">
                <img src="/images/no_permissions.svg" width={190} height={74} alt="No Data"/>
                <span className="text_12 color_white mt_6">No Used Tools Found</span>
              </div> : <div className="scrollable_container">
                <table className="table_css margin_0 padding_0">
                  <thead>
                  <tr style={{borderTop: 'none'}}>
                    <th className="table_header w_56">Tool</th>
                    <th className="table_header text_align_right w_22">Agents</th>
                    <th className="table_header text_align_right w_22">Calls</th>
                  </tr>
                  </thead>
                </table>

                <div className="overflow_auto w_100">
                  <table className="table_css margin_0">
                    <tbody>
                    {toolsUsed.map((tool, index) => (
                      <tr key={index}>
                        <td className="table_data" style={{width: '100%', display: 'flex', alignItems: 'center'}}>
                          <Image className="image_class bg_black" width={20} height={20}
                                 src={returnToolkitIcon(tool.toolkit)} alt="tool-icon"/>
                          <span>{tool.tool_name}</span>
                        </td>
                        <td className="table_data text_align_right w_22">{tool.unique_agents}</td>
                        <td className="table_data text_align_right w_22">{tool.total_usage}</td>
                      </tr>
                    ))}
                    </tbody>
                  </table>
                </div>
              </div>}
          </div>

          <div key="agent_details" className="display_column_container">
            <span className="text_14 mb_8">Agent Overview</span>
            {allAgents.length === 0 ?
              <div className="vertical_container align_center mt_50 w_100">
                <img src="/images/no_permissions.svg" width={300} height={120} alt="No Data"/>
                <span
                  className="text_12 color_white mt_6">{selectedAgent === 'Select an Agent' ? 'Please Select an Agent' :
                  <React.Fragment>No Runs found for <b>{selectedAgent}</b></React.Fragment>}</span>
              </div> : <div className="scrollable_container mt_16">
                <table className="table_css margin_0 padding_0">
                  <thead>
                  <tr style={{borderTop: 'none'}}>
                    <th className="table_header w_20">Agent Name</th>
                    <th className="table_header text_align_right w_10">Model <img width={14} height={14} src="/images/arrow_downward.svg"
                                                                                                    alt="arrow_down"/>
                    </th>
                    <th className="table_header text_align_right w_12">Tokens Consumed <img width={14} height={14} src="/images/arrow_downward.svg"
                                                                                                              alt="arrow_down"/>
                    </th>
                    <th className="table_header text_align_right w_6">Runs <img width={14} height={14} src="/images/arrow_downward.svg"
                                                                                                  alt="arrow_down"/>
                    </th>
                    <th className="table_header text_align_right w_12">Avg tokens per run <img
                      width={14} height={14} src="/images/arrow_downward.svg" alt="arrow_down"/></th>
                    <th className="table_header text_align_right w_20">Tools <img width={14} height={14} src="/images/arrow_downward.svg"
                                                                                                    alt="arrow_down"/>
                    </th>
                    <th className="table_header text_align_right w_10">Calls <img width={14} height={14} src="/images/arrow_downward.svg"
                                                                                                    alt="arrow_down"/>
                    </th>
                    <th className="table_header text_align_right w_10">Avg Run Time <img width={14} height={14} src="/images/arrow_downward.svg"
                                                                                                           alt="arrow_down"/>
                    </th>
                  </tr>
                  </thead>
                </table>

                <div className="overflow_auto w_100">
                  <table className="table_css margin_0">
                    <tbody>
                    {allAgents.map((run, i) => (
                      <tr key={i}>
                        <td className="table_data w_20">{run.name}</td>
                        <td className="table_data text_align_right w_10">{run.model_name}</td>
                        <td className="table_data text_align_right w_12">{formatNumber(run.total_tokens)}</td>
                        <td className="table_data text_align_right w_6">{run.runs_completed}</td>
                        <td className="table_data text_align_right w_12">
                          {run.runs_completed ? (run.total_tokens / run.runs_completed).toFixed(1) : '-'}
                        </td>
                        <td className="table_data text_align_right" style={{width: '20%'}}>
                          {run.tools_used && run.tools_used.slice(0, 3).map((tool, index) => (
                              <div key={index} className="tools_used">{tool}</div>
                          ))}
                          {run.tools_used && run.tools_used.length > 3 &&
                              <div style={{display:'inline-flex'}}>
                                {(showToolTip && toolTipIndex === i) && <div className="tools_used_tooltip">
                                  {run.tools_used.slice(3).map((tool,index) =>
                                      <div className="tools_used" key={index}>{tool}</div>
                                  )}
                                </div>}
                                <div className="tools_used cursor_pointer" onMouseEnter={() => setToolTipState(true,i)} onMouseLeave={() => setToolTipState(false,i)}>
                                  +{run.tools_used.length - 3}
                                </div>
                              </div>
                          }
                        </td>
                        <td className="table_data text_align_right w_10">{run.total_calls}</td>
                        <td className="table_data text_align_right w_10">
                          {run.avg_run_time === 0 ? '-' : `${parseFloat((run.avg_run_time / 60).toFixed(1))} mins`}
                        </td>
                      </tr>))}
                    </tbody>
                  </table>
                </div>
              </div>}
          </div>
          <div key="active_runs" className="display_column_container">
            <span className="text_14 mb_8">Active Runs</span>
            <div className="scrollable_container gap_8">
              {activeRuns.length === 0 ?
                <div className="vertical_container align_center mt_24">
                  <img src="/images/no_permissions.svg" width={190} height={74} alt="No Data"/>
                  <span className="text_12 color_white mt_6">No active runs found</span>
                </div> : activeRuns.map((run, index) => (
                  <div key={index} className="active_runs">
                    <span className="text_14">{run.name}</span>
                    <div style={{display: 'inline-flex', alignItems: 'center'}}>
                      <span className="text_12 mt_6">{run.agent_name} ·  <Image width={12} height={12} src="/images/schedule.svg" alt="schedule-icon"/>
                        {formatTime(run.created_at)}</span>
                    </div>
                  </div>
                ))}
            </div>
          </div>
          <div key="total_tokens_consumed" className="display_column_container">
            <div className="horizontal_space_between w_100">
              <span className="text_14 mb_8">Tokens Consumed by Runs</span>
              <div style={{position: 'relative', display: 'flex', flexDirection: 'column'}}>
                {allAgents.length > 0 && <div>
                  <div className="text_14 mb_8 cursor_pointer" onClick={() => setDropDown2(!dropdown2)}>{selectedAgent}<img width={18} height={16}
                                                                                    src="/images/expand_more.svg"/></div>
                  {dropdown2 &&
                    <div className="custom_select_options padding_8 position_absolute r_0">
                      {allAgents.map((agent, index) => (
                        <div key={index} className="custom_select_option padding_8" onClick={() => handleSelectedAgent(agent.agent_id, agent.name)}>{agent.name}</div>))}
                    </div>}
                </div>}
              </div>
            </div>
            {selectedAgentRun.length > 0
              ? <><BarGraph data={selectedAgentRun} type="tokens_consumed" color="#3DFF7F"/>
                <div className="horizontal_container mt_10">
                  <span className="bar_label_dot" style={{backgroundColor: '#3DFF7F'}}></span>
                  <span className="bar_label_text">Runs</span>
                </div>
              </>
              : <div className="vertical_container align_center mt_80 w_100">
                <img src="/images/no_permissions.svg" width={190} height={74} alt="No Data"/>
                <span className="text_12 color_white mt_6">No Runs Found</span>
              </div>}
          </div>

          <div key="total_calls_made" className="display_column_container">
            <div className="horizontal_space_between w_100">
              <span className="text_14 mb_8">Calls Made by Runs</span>
              <div className="vertical_containers position_relative">
                {allAgents.length > 0 && <div>
                  <div className="text_14 mb_8 cursor_pointer"
                       onClick={() => setDropDown1(!dropdown1)}>{selectedAgent}<img width={18} height={16} src="/images/expand_more.svg"/>
                  </div>
                  {dropdown1 &&
                    <div className="custom_select_options padding_8 position_absolute r_0">
                      {allAgents.map((agent, index) => (
                        <div key={index} className="custom_select_option padding_8" onClick={() => handleSelectedAgent(agent.agent_id, agent.name)}>{agent.name}</div>))}
                    </div>}
                </div>}
              </div>
            </div>
            {selectedAgentRun.length > 0
              ? <><BarGraph data={selectedAgentRun} type="calls" color="#3DFF7F"/>
                <div className="horizontal_container mt_10">
                  <span className="bar_label_dot" style={{backgroundColor: '#3DFF7F'}}></span>
                  <span className="bar_label_text">Runs</span>
                </div>
              </>
              : <div className="vertical_container align_center mt_80 w_100">
                <img src="/images/no_permissions.svg" width={190} height={74} alt="No Data"/>
                <span className="text_12 color_white mt_6">No Runs Found</span>
              </div>}
          </div>
          <div key="tokens_consumed_per_call" className="display_column_container">
            <div className="horizontal_space_between w_100">
              <span className="text_14 mb_8">Average Tokens consumed in all calls per run </span>
              <div className="vertical_containers position_relative">
                {allAgents.length > 0 && <div>
                  <div className="text_14 mb_8 cursor_pointer"
                       onClick={() => setDropDown3(!dropdown3)}>{selectedAgent}<img width={18} height={16} src="/images/expand_more.svg"/>
                  </div>
                  {dropdown3 &&
                    <div className="custom_select_options padding_8 position_absolute r_0">
                      {allAgents.map((agent, index) => (
                        <div key={index} className="custom_select_option padding_8"
                             onClick={() => handleSelectedAgent(agent.agent_id, agent.name)}>{agent.name}</div>))}
                    </div>}
                </div>}
              </div>
            </div>
            {selectedAgentRun.length > 0
              ? <><BarGraph data={selectedAgentRun} type="tokens_per_call" color="#3DFF7F"/>
                <div className="horizontal_container mt_10">
                  <span className="bar_label_dot" style={{backgroundColor: '#3DFF7F'}}></span>
                  <span className="bar_label_text">Runs</span>
                </div>
              </>
              : <div className="vertical_container align_center mt_80 w_100">
                <img src="/images/no_permissions.svg" width={190} height={74} alt="No Data"/>
                <span className="text_12 color_white mt_6">No Runs Found</span>
              </div>}
          </div>
        </ResponsiveGridLayout>
      </div>
    </div>
  );
}
