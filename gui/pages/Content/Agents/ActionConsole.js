import React, {useState, useEffect} from 'react';
import styles from './Agents.module.css';
import Image from 'next/image';
import {updatePermissions} from '@/pages/api/DashboardService';
import {formatTimeDifference} from '@/utils/utils';

function ActionBox({
  action,
  deniedById,
  reasonsById,
  errorById,
  processingIds,
  handleDeny,
  handleSelection,
  handleReasonChange,
}) {
  const isDenied = deniedById[action.id];
  const isProcessing = processingIds.includes(action.id);
  const feedbackInputId = `permission-feedback-${action.id}`;

  return (
    
    <div key={action.id} className={styles.history_box}
         style={{background: '#272335', padding: '16px', cursor: 'default'}}>
      <div style={{display: 'flex', flexDirection: 'column'}}>
        {action.question && (<div className={styles.feed_title}>{action.question}</div>)}
        {!action.question && (<div>Tool <b>{action.tool_name}</b> is requesting permissions</div>)}

        {isDenied && (
          <div style={{marginTop: '26px'}}>
            <label htmlFor={feedbackInputId}>Provide Feedback <span style={{color: '#888888'}}>(Optional)</span></label>
            <input id={feedbackInputId} style={{marginTop: '6px'}} type="text" value={reasonsById[action.id] || ''}
                   placeholder="Enter your input here"
                   className="input_medium"
                   onChange={(e) => handleReasonChange(action.id, e.target.value)}/>
          </div>
        )}
        {isDenied ? (
          <div style={{display: 'inline-flex', gap: '8px'}}>
            <button type="button" onClick={() => handleDeny(action.id)} disabled={isProcessing}
                    aria-label="Go back from deny action" className="secondary_button mt_16"
                    style={{paddingLeft: '10px'}}>
              <Image width={12} height={12} src="/images/undo.svg" alt="check-icon"/>
              <span className={styles.text_12_n}>Go Back</span>
            </button>
            <button type="button" onClick={() => handleSelection(action.id, false)} disabled={isProcessing}
                    aria-label="Confirm deny action"
                    className="secondary_button mt_16"
                    style={{background: 'transparent', border: 'none'}}>
              <span className={styles.text_12_n}>{isProcessing ? 'Updating...' : 'Proceed to Deny'}</span>
            </button>
          </div>
        ) : (
          <div style={{display: 'inline-flex', gap: '8px'}}>
            <button type="button" onClick={() => handleSelection(action.id, true)} disabled={isProcessing}
                    aria-label="Approve action"
                    className="secondary_button mt_16"
                    style={{paddingLeft: '10px'}}>
              <Image width={12} height={12} src="/images/check.svg" alt="check-icon"/>
              <span className={styles.text_12_n}>{isProcessing ? 'Updating...' : 'Approve'}</span>
            </button>
            <button type="button" onClick={() => handleDeny(action.id)} disabled={isProcessing}
                    aria-label="Deny action" className="secondary_button mt_16"
                    style={{background: 'transparent', border: 'none'}}>
              <Image width={16} height={16} src="/images/close.svg" alt="close-icon"/>
              <span className={styles.text_12_n}>Deny</span>
            </button>
          </div>
        )}
        {errorById[action.id] && <div style={{color: '#F78166', marginTop: '8px'}}>{errorById[action.id]}</div>}
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
    <div key={action.id} className={styles.history_box}
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
  const [deniedById, setDeniedById] = useState({});
  const [reasonsById, setReasonsById] = useState({});
  const [errorById, setErrorById] = useState({});
  const [processingIds, setProcessingIds] = useState([]);

  useEffect(() => {
    if (!actions || actions.length === 0) {
      return;
    }

    setDeniedById((prevDenied) => {
      const nextDenied = {};
      actions.forEach(({id}) => {
        nextDenied[id] = prevDenied[id] || false;
      });
      return nextDenied;
    });

    setReasonsById((prevReasons) => {
      const nextReasons = {};
      actions.forEach(({id}) => {
        nextReasons[id] = prevReasons[id] || '';
      });
      return nextReasons;
    });

    setErrorById((prevErrors) => {
      const nextErrors = {};
      actions.forEach(({id}) => {
        nextErrors[id] = prevErrors[id] || '';
      });
      return nextErrors;
    });

    setHiddenActions((prevHiddenActions) => prevHiddenActions.filter((id) => actions.some((action) => action.id === id)));
    setProcessingIds((prevProcessingIds) => prevProcessingIds.filter((id) => actions.some((action) => action.id === id)));
  }, [actions]);

  const handleDeny = (actionId) => {
    setDeniedById((prevDenied) => ({...prevDenied, [actionId]: !prevDenied[actionId]}));
  };

  const handleReasonChange = (actionId, value) => {
    setReasonsById((prevReasons) => ({...prevReasons, [actionId]: value}));
  };

  const handleSelection = async (permissionId, status) => {
    if (processingIds.includes(permissionId)) {
      return;
    }

    setProcessingIds((prevProcessingIds) => [...prevProcessingIds, permissionId]);
    setErrorById((prevErrors) => ({...prevErrors, [permissionId]: ''}));

    const data = {
      status: status,
      user_feedback: reasonsById[permissionId],
    };

    try {
      const response = await updatePermissions(permissionId, data);

      if (response.status === 200) {
        setHiddenActions((prevHiddenActions) => [...prevHiddenActions, permissionId]);
        setPendingPermissions((prevPendingPermissions) => Math.max((prevPendingPermissions || 0) - 1, 0));
      } else {
        setErrorById((prevErrors) => ({...prevErrors, [permissionId]: 'Could not update permission. Please retry.'}));
      }
    } catch {
      setErrorById((prevErrors) => ({...prevErrors, [permissionId]: 'Could not update permission. Please retry.'}));
    } finally {
      setProcessingIds((prevProcessingIds) => prevProcessingIds.filter((id) => id !== permissionId));
    }
  };

  return (
    <>
      {actions && actions.length > 0 ? (
        <div className={`${styles.detail_body} ${styles.action_console_body}`}>
          {actions.map((action) => {
            if (action.status === 'PENDING' && !hiddenActions.includes(action.id)) {
              return (<ActionBox key={action.id} action={action} deniedById={deniedById}
                                 reasonsById={reasonsById} errorById={errorById} processingIds={processingIds}
                                 handleReasonChange={handleReasonChange}
                                 handleDeny={handleDeny} handleSelection={handleSelection}/>);
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