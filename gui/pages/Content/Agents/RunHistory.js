import React, {useEffect} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import {formatNumber, formatTimeDifference} from "@/utils/utils";
import {EventBus} from "@/utils/eventBus";

export default function RunHistory({runs, setHistory, selectedRunId, setSelectedRun, setAgentExecutions}) {
  useEffect(() => {
    const resetRunStatus = (eventData) => {
      const updatedExecutions = runs.map((run) => {
        if (run.id === eventData.executionId) {
          return {...run, status: eventData.status};
        }
        return run;
      });

      setAgentExecutions(updatedExecutions);
    };

    EventBus.on('resetRunStatus', resetRunStatus);

    return () => {
      EventBus.off('resetRunStatus', resetRunStatus);
    };
  });

  return (<>
    <div className="w_20 h_100">
      <div className="detail_top mt_8 mb_8">
        <div className="text_12 horizontal_container padding_0 gap_6">
          <Image width={16} height={16} src="/images/update.svg" alt="update-icon"/>
          <div className="color_white lh_16">Run history</div>
        </div>
        <Image className="cursor_pointer" onClick={() => setHistory(false)} width={28} height={28} src="/images/close_history.svg" alt="close-history-icon"/>
      </div>

      <div className="detail_body mb_20">
        {runs && runs.map((run) => (<div key={run.id} onClick={() => setSelectedRun(run)} className={selectedRunId === run.id ? 'history_box_selected' : 'history_box'}>
          <div className="horizontal_container mb_14">
            {run.status === 'RUNNING' && <Image className="mix_blend_mode mr_7" width={14} height={14} src="/images/loading.gif" alt="loading-icon"/>}
            <div className="text_ellipsis">{run.name}</div>
            {/*{run.notification_count > 0 && <div className={styles.notification_bubble}>{run.notification_count}</div>}*/}
          </div>
          <div className="horizontal_container align_center">
            <div className="horizontal_container w_fit_content">
              <Image width={12} height={12} src="/images/calls_made.svg" alt="call-icon"/>
              <div className="text_10 ml_4">{formatNumber(run?.num_of_calls || 0)} Calls</div>
            </div>
            <div className="horizontal_container ml_10 w_fit_content">
              <Image width={12} height={12} src="/images/schedule.svg" alt="schedule-icon"/>
              <div className="text_10 ml_4">
                {formatTimeDifference(run.time_difference)}
              </div>
            </div>
          </div>
        </div>))}
      </div>
    </div>
  </>)
}