import React, {useState, useEffect} from 'react';
import styles from './Agents.module.css';
import Image from 'next/image';
import {updatePermissions} from '@/pages/api/DashboardService';
import {formatTimeDifference} from '@/utils/utils';

function ActionBox({action, index, denied, reasons, handleDeny, handleSelection, setReasons, isSubmitting}) {
  const isDenied = denied[index];

  return (
    <div className={styles.history_box}
         style={{background: '#272335', padding: '16px', cursor: 'default'}}>
      <div style={{display: 'flex', flexDirection: 'column'}}>
        {action.question && (<div className={styles.feed_title}>{action.question}</div>)}
        {!action.question && (<div>Tool <b>{action.tool_name}</b> is requesting permissions</div>)}

        {isDenied && (
          <div style={{marginTop: '26px'}}>
            <div>Provide Feedback <span style={{color: '#888888'}}>(Optional)</span></div>
            <input style={{marginTop: '6px'}} type="text" value={reasons[index]} placeholder="Enter your input here"
                   className="input_medium"
                   disabled={isSubmitting}
                   onChange={(e) => {
                     const newReasons = [...reasons];
                     newReasons[index] = e.target.value;
                     setReasons(newReasons);
                   }}/>
          </div>
        )}
        {isDenied ? (
          <div style={{display: 'inline-flex', gap: '8px'}}>
            <button onClick={() => handleDeny(index)} className="secondary_button mt_16" style={{paddingLeft: '10px'}}
                    disabled={isSubmitting}>
              <Image width={12} height={12} src="/images/undo.svg" alt="check-icon"/>
              <span className={styles.text_12_n}>Go Back</span>
            </button>
            <button onClick={() => handleSelection(index, false, action.id)} className="secondary_button mt_16"
                    style={{background: 'transparent', border: 'none'}} disabled={isSubmitting}>
              <span className={styles.text_12_n}>{isSubmitting ? 'Denying...' : 'Proceed to Deny'}</span>
            </button>
          </div>
        ) : (
          <div style={{display: 'inline-flex', gap: '8px'}}>
            <button onClick={() => handleSelection(index, true, action.id)} className="secondary_button mt_16"
                    style={{paddingLeft: '10px'}} disabled={isSubmitting}>
              <Image width={12} height={12} src="/images/check.svg" alt="check-icon"/>
              <span className={styles.text_12_n}>{isSubmitting ? 'Approving...' : 'Approve'}</span>
            </button>
            <button onClick={() => handleDeny(index)} className="secondary_button mt_16"
                    style={{background: 'transparent', border: 'none'}} disabled={isSubmitting}>
              <Image width={16} height={16} src="/images/close.svg" alt="close-icon"/>
              <span className={styles.text_12_n}>Deny</span>
            </button>
          </div>
        )}
      </div>
      <div style={{display: 'flex', alignItems: 'center', paddingLeft: '0', paddingBottom: '0'}}
           className={styles.tab_text}>
        <div>
          <Image width={12} height={12} src="/images/schedule.svg" alt="schedule-icon"/>
        </div>
        <div className={styles.history_info}>{formatTimeDifference(action.time_difference)}</div>
      </div>
    </div>
  );
}

function HistoryBox({action}) {
  return (
    <div className={styles.history_box}
         style={{background: '#272335', padding: '16px', cursor: 'default'}}>
      <div style={{display: 'flex', flexDirection: 'column'}}>
        <div>Permission for <b>{action.tool_name}</b> was:</div>
        {action.status && action.status === 'APPROVED' ? (
          <button className="history_permission mt_16">
            <Image width={12} height={12} src="/images/check.svg" alt="check-icon"/>
            <span className={styles.text_12_n}>Approved</span>
          </button>
        ) : (
          <button className="history_permission mt_16">
            <Image width={14} height={14} src="/images/close.svg" alt="close-icon"/>
            <span className={styles.text_12_n}>Denied</span>
          </button>
        )}
        {action.user_feedback != null &&
          <div style={{display: 'flex', flexDirection: 'column'}}>
            <div className="mt_16" style={{color: '#888888'}}>Feedback</div>
            <div className="mt_6 mb_8">{action.user_feedback}</div>
          </div>
        }
        <div style={{display: 'flex', alignItems: 'center', paddingLeft: '0', paddingBottom: '0'}}
             className={styles.tab_text}>
          <div>
            <Image width={12} height={12} src="/images/schedule.svg" alt="schedule-icon"/>
          </div>
          <div className={styles.history_info}>{formatTimeDifference(action.time_difference)}</div>
        </div>
      </div>
    </div>
  )
}

export default function ActionConsole({actions, setPendingPermissions}) {
  const [hiddenActions, setHiddenActions] = useState([]);
  const [denied, setDenied] = useState([]);
  const [reasons, setReasons] = useState([]);
  const [submittingActionIds, setSubmittingActionIds] = useState([]);

  useEffect(() => {
    if (!actions || actions.length === 0) {
      setHiddenActions([]);
      setSubmittingActionIds([]);
      setDenied([]);
      setReasons([]);
      return;
    }

    const actionIds = new Set(actions.map((action) => action.id));
    setHiddenActions((prevHiddenActions) => prevHiddenActions.filter((id) => actionIds.has(id)));
    setSubmittingActionIds((prevSubmitting) => prevSubmitting.filter((id) => actionIds.has(id)));

    // Keep local state aligned to action list length while preserving existing user input.
    setDenied((prevDenied) => actions.map((_, index) => prevDenied[index] ?? false));
    setReasons((prevReasons) => actions.map((_, index) => prevReasons[index] ?? ''));
  }, [actions]);

  const handleDeny = (index) => {
    setDenied((prevDenied) => {
      const newDeniedState = [...prevDenied];
      newDeniedState[index] = !newDeniedState[index];
      return newDeniedState;
    });
  };

  const handleSelection = (index, status, permissionId) => {
    if (submittingActionIds.includes(permissionId)) {
      return;
    }

    setSubmittingActionIds((prevSubmitting) => [...prevSubmitting, permissionId]);

    setHiddenActions((prevHiddenActions) => (
      prevHiddenActions.includes(permissionId)
        ? prevHiddenActions
        : [...prevHiddenActions, permissionId]
    ));

    const normalizedFeedback = (reasons[index] || '').trim();

    const data = {
      status: status,
      user_feedback: normalizedFeedback.length > 0 ? normalizedFeedback : null,
    };

    updatePermissions(permissionId, data).then((response) => {
      if (response.status === 200) {
        setPendingPermissions((prev) => Math.max((prev || 0) - 1, 0));
      } else {
        setHiddenActions((prevHiddenActions) => prevHiddenActions.filter((id) => id !== permissionId));
      }
      setSubmittingActionIds((prevSubmitting) => prevSubmitting.filter((id) => id !== permissionId));
    }).catch(() => {
      setHiddenActions((prevHiddenActions) => prevHiddenActions.filter((id) => id !== permissionId));
      setSubmittingActionIds((prevSubmitting) => prevSubmitting.filter((id) => id !== permissionId));
    });
  };

  return (
    <>
      {actions && actions.length > 0 ? (
        <div className={styles.detail_body} style={{height: 'auto'}}>
          {actions.map((action, index) => {
            if (action.status === 'PENDING' && !hiddenActions.includes(action.id)) {
              const isSubmitting = submittingActionIds.includes(action.id);
              return (<ActionBox key={action.id} action={action} index={index} denied={denied} setReasons={setReasons}
                                 reasons={reasons} handleDeny={handleDeny} handleSelection={handleSelection}
                                 isSubmitting={isSubmitting}/>);
            } else if (action.status === 'APPROVED' || action.status === 'REJECTED') {
              return (<HistoryBox key={action.id} action={action}/>);
            }
            return null;
          })}
        </div>
      ) : (
        <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '40px'}}>
          <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions"/>
          <span className={styles.feed_title} style={{marginTop: '8px'}}>No Actions to Display!</span>
        </div>
      )}
    </>
  );
}