import React, {useState, useEffect, useMemo, useRef} from 'react';
import styles from './Agents.module.css';
import Image from 'next/image';
import {updatePermissions} from '@/pages/api/DashboardService';
import {formatTimeDifference} from '@/utils/utils';

const removeIdFromList = (items, targetId) => items.filter((id) => id !== targetId);

const removeKeyFromObject = (source, keyToRemove) => {
  const nextObject = {...source};
  delete nextObject[keyToRemove];
  return nextObject;
};

function ActionBox({action, denied, reasons, handleDeny, handleSelection, setReasons, isSubmitting}) {
  const isDenied = denied[action.id] ?? false;

  return (
    <div className={styles.action_card}>
      <div className={styles.action_card_content}>
        {action.question && (<div className={styles.feed_title}>{action.question}</div>)}
        {!action.question && (<div>Tool <b>{action.tool_name}</b> is requesting permissions</div>)}

        {isDenied && (
          <div className={styles.action_feedback}>
            <div>Provide Feedback <span style={{color: '#888888'}}>(Optional)</span></div>
            <input type="text" value={reasons[action.id] ?? ''} placeholder="Enter your input here"
                   className={`input_medium ${styles.action_feedback_input}`}
                   disabled={isSubmitting}
                   onChange={(e) => {
                     const newReasons = {...reasons};
                     newReasons[action.id] = e.target.value;
                     setReasons(newReasons);
                   }}/>
          </div>
        )}
        {isDenied ? (
          <div className={styles.action_button_row}>
            <button type="button" onClick={() => handleDeny(action.id)} className="secondary_button mt_16" style={{paddingLeft: '10px'}}
                    disabled={isSubmitting}>
              <Image width={12} height={12} src="/images/undo.svg" alt="check-icon"/>
              <span className={styles.text_12_n}>Go Back</span>
            </button>
            <button type="button" onClick={() => handleSelection(false, action.id)} className="secondary_button mt_16"
                    style={{background: 'transparent', border: 'none'}} disabled={isSubmitting}>
              <span className={styles.text_12_n}>{isSubmitting ? 'Denying...' : 'Submit Denial'}</span>
            </button>
          </div>
        ) : (
          <div className={styles.action_button_row}>
            <button type="button" onClick={() => handleSelection(true, action.id)} className="secondary_button mt_16"
                    style={{paddingLeft: '10px'}} disabled={isSubmitting}>
              <Image width={12} height={12} src="/images/check.svg" alt="check-icon"/>
              <span className={styles.text_12_n}>{isSubmitting ? 'Approving...' : 'Approve'}</span>
            </button>
            <button type="button" onClick={() => handleDeny(action.id)} className="secondary_button mt_16"
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
    <div className={styles.action_card}>
      <div className={styles.action_card_content}>
        <div>Permission for <b>{action.tool_name}</b> was:</div>
        {action.status && action.status === 'APPROVED' ? (
          <button type="button" className="history_permission mt_16">
            <Image width={12} height={12} src="/images/check.svg" alt="check-icon"/>
            <span className={styles.text_12_n}>Approved</span>
          </button>
        ) : (
          <button type="button" className="history_permission mt_16">
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
  const [denied, setDenied] = useState({});
  const [reasons, setReasons] = useState({});
  const [submittingActionIds, setSubmittingActionIds] = useState([]);
  const submittingActionRef = useRef(new Set());
  const hiddenActionIdSet = useMemo(() => new Set(hiddenActions), [hiddenActions]);
  const submittingActionIdSet = useMemo(() => new Set(submittingActionIds), [submittingActionIds]);

  useEffect(() => {
    if (!actions || actions.length === 0) {
      setHiddenActions([]);
      setSubmittingActionIds([]);
      submittingActionRef.current = new Set();
      setDenied({});
      setReasons({});
      return;
    }

    const actionIds = new Set(actions.map((action) => action.id));
    setHiddenActions((prevHiddenActions) => prevHiddenActions.filter((id) => actionIds.has(id)));
    setSubmittingActionIds((prevSubmitting) => prevSubmitting.filter((id) => actionIds.has(id)));
    submittingActionRef.current = new Set(
      [...submittingActionRef.current].filter((id) => actionIds.has(id))
    );

    // Keep local state aligned to action ids while preserving existing user input.
    setDenied((prevDenied) => {
      const nextDenied = {};
      actions.forEach((action) => {
        nextDenied[action.id] = prevDenied[action.id] ?? false;
      });
      return nextDenied;
    });
    setReasons((prevReasons) => {
      const nextReasons = {};
      actions.forEach((action) => {
        nextReasons[action.id] = prevReasons[action.id] ?? '';
      });
      return nextReasons;
    });
  }, [actions]);

  const handleDeny = (actionId) => {
    setDenied((prevDenied) => ({
      ...prevDenied,
      [actionId]: !(prevDenied[actionId] ?? false),
    }));
  };

  const handleSelection = async (status, permissionId) => {
    if (submittingActionRef.current.has(permissionId) || submittingActionIdSet.has(permissionId)) {
      return;
    }

    submittingActionRef.current.add(permissionId);

    setSubmittingActionIds((prevSubmitting) => (
      prevSubmitting.includes(permissionId) ? prevSubmitting : [...prevSubmitting, permissionId]
    ));

    setHiddenActions((prevHiddenActions) => (
      prevHiddenActions.includes(permissionId)
        ? prevHiddenActions
        : [...prevHiddenActions, permissionId]
    ));

    const normalizedFeedback = (reasons[permissionId] || '').trim();

    const data = {
      status: status,
      user_feedback: normalizedFeedback.length > 0 ? normalizedFeedback : null,
    };

    try {
      const response = await updatePermissions(permissionId, data);
      if (response.status === 200) {
        setPendingPermissions((prev) => Math.max((prev || 0) - 1, 0));
      } else {
        setHiddenActions((prevHiddenActions) => removeIdFromList(prevHiddenActions, permissionId));
      }
    } catch {
      setHiddenActions((prevHiddenActions) => removeIdFromList(prevHiddenActions, permissionId));
    } finally {
      submittingActionRef.current.delete(permissionId);
      setSubmittingActionIds((prevSubmitting) => removeIdFromList(prevSubmitting, permissionId));
      setDenied((prevDenied) => removeKeyFromObject(prevDenied, permissionId));
      setReasons((prevReasons) => removeKeyFromObject(prevReasons, permissionId));
    }
  };

  return (
    <>
      {actions && actions.length > 0 ? (
        <div className={styles.detail_body} style={{height: 'auto'}}>
          {actions.map((action) => {
            if (action.status === 'PENDING' && !hiddenActionIdSet.has(action.id)) {
              const isSubmitting = submittingActionIdSet.has(action.id);
              return (<ActionBox key={action.id} action={action} denied={denied} setReasons={setReasons}
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