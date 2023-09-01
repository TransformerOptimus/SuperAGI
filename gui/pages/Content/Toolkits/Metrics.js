import React, {useState, useEffect, useRef} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {
  getApiKeys, getToolMetrics, getToolLogs, getKnowledgeMetrics, getKnowledgeLogs
} from "@/pages/api/DashboardService";
import {
  loadingTextEffect,
} from "@/utils/utils";

export default function Metrics({toolName, knowledgeName}) {
  const [apiKeys, setApiKeys] = useState([]);
  const [totalTokens, setTotalTokens] = useState(0)
  const [totalAgentsUsing, setTotalAgentsUsing] = useState(0)
  const [totalCalls, setTotalCalls] = useState(0)
  const [callLogs, setCallLogs] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [loadingText, setLoadingText] = useState("Loading Metrics");
  const metricsData = [
    { label: 'Total Calls', value: totalCalls },
    { label: 'Total Agents Using', value: totalAgentsUsing }
  ];

  useEffect(() => {
    loadingTextEffect('Loading Metrics', setLoadingText, 500);
  }, []);

  useEffect(() => {
    if(toolName && !knowledgeName){
      fetchToolMetrics()
      fetchToolLogs()
      return;
    }
    if(!toolName && knowledgeName){
      fetchKnowledgeMetrics()
      fetchKnowledgeLogs()
      return;
    }
  }, [toolName, knowledgeName]);

  const fetchToolMetrics = () => {
    getToolMetrics(toolName)
      .then((response) => {
        setTotalAgentsUsing(response.data.tool_unique_agents ? response.data.tool_unique_agents : 0)
        setTotalCalls(response.data.tool_calls ? response.data.tool_calls : 0)
        setIsLoading(false)
      })
      .catch((error) => {
        console.error('Error fetching Metrics', error);
      });
  }

  const fetchToolLogs = () => {
    getToolLogs(toolName)
      .then((response) => {
        setCallLogs(response.data ? response.data : [])
        setIsLoading(false)
      })
      .catch((error) => {
        console.error('Error fetching Metrics', error);
      });
  }

  const fetchKnowledgeMetrics = () => {
    getKnowledgeMetrics(knowledgeName)
      .then((response) => {
        setTotalAgentsUsing(response.data.knowledge_unique_agents ? response.data.knowledge_unique_agents : 0)
        setTotalCalls(response.data.knowledge_calls ? response.data.knowledge_calls : 0)
        setIsLoading(false)
      })
      .catch((error) => {
        console.error('Error fetching Metrics', error);
      });
  }

  const fetchKnowledgeLogs = () => {
    getKnowledgeLogs(knowledgeName)
      .then((response) => {
        setCallLogs(response.data ? response.data : [])
        setIsLoading(false)
      })
      .catch((error) => {
        console.error('Error fetching Metrics', error);
      });
  }

  return (<>
    <div className="row">
      <div className="col-12 padding_5 ">
        {!isLoading ?
          <div>
            <div className="display_flex_container gap_5">
            {metricsData.map((metric, index) => (
              <div className="display_column_container" key={index}>
                <span className="text_14">{metric.label}</span>
                <div className="text_60_bold display_flex justify_center align_center w_100 h_100 mb_24">
                  {metric.value}
                </div>
              </div>
            ))}
            </div>
              <div className="display_column_container mt_5">
                <span className="text_14">Call Logs</span>
                {callLogs.length > 0 ? <div className="scrollable_container pd_bottom_5 border_radius_8 bg_none">
                  <table className="w_100 margin_0 padding_0">
                    <thead>
                    <tr className="border_top_none text_align_left border_bottom_none">
                      <th className="table_header w_15">Log Timestamp</th>
                      <th className="table_header w_15">Agent Name</th>
                      <th className="table_header w_40">Run Name</th>
                      <th className="table_header w_15">Model</th>
                      <th className="table_header w_15">Tokens Used</th>
                    </tr>
                    </thead>
                  </table>
                  <div className="overflow_auto w_100">
                    <table className="table_css margin_0">
                      <tbody>
                      {callLogs.map((item, index) => (
                        <tr key={index} className="text_align_left">
                          <td className="table_data w_15 border_gray border_left_none">{item.created_at}</td>
                          <td className="table_data w_15 border_gray">{item.agent_name}</td>
                          <td className="table_data w_40 border_gray">{item.agent_execution_name}</td>
                          <td className="table_data w_15 border_gray">{item.model}</td>
                          <td className="table_data w_15 border_gray">{item.tokens_consumed}</td>
                        </tr>
                      ))}
                      </tbody>
                    </table>
                  </div>
                </div> :
                  <div className="vertical_container align_center mt_90 w_100 mb_90">
                    <img src="/images/no_permissions.svg" width={190} height={74} alt="No Data"/>
                    <span className="text_12 color_white mt_6">No logs to show!</span>
                  </div>}
          </div>
          </div>
          :  <div className="loading_container">
          <div className="signInInfo loading_text">{loadingText}</div>
        </div>}
      </div>
    </div>
    <ToastContainer/>
  </>)
}