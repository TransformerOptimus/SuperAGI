import React, { useState, useEffect } from 'react';
import styles from './Agents.module.css';
import Image from 'next/image';
import { updatePermissions } from '@/pages/api/DashboardService';
import { formatTime } from '@/utils/utils';

function ActionBox({ action, index, denied, reasons, handleDeny, handleSelection, setReasons }) {
    const isDenied = denied[index];

    return (
      <div key={action.id} className={styles.history_box} style={{ background: '#272335', padding: '16px', cursor: 'default' }}>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
              <div>Tool <b>{action.tool_name}</b> is seeking for Permissions</div>
              {isDenied && (
                <div style={{ marginTop: '26px' }}>
                    <div>Provide Feedback <span style={{ color: '#888888' }}>(Optional)</span></div>
                    <input style={{ marginTop: '6px' }} type="text" value={reasons[index]} placeholder="Enter your input here" className="input_medium"
                      onChange={(e) => {
                          const newReasons = [...reasons];
                          newReasons[index] = e.target.value;
                          setReasons(newReasons);
                      }}/>
                </div>
              )}
              {isDenied ? (
                <div style={{ display: 'inline-flex', marginTop: '16px', gap: '8px' }}>
                    <button onClick={() => handleDeny(index)} className="secondary_button" style={{ paddingLeft: '10px', paddingTop: '2px' }}>
                        <Image style={{ marginTop: '2px' }} width={12} height={12} src="/images/undo.svg" alt="check-icon" />
                        <span className={styles.text_12_n}>Go Back</span>
                    </button>
                    <button onClick={() => handleSelection(index, false, action.id)} className="secondary_button" style={{ paddingLeft: '10px', paddingTop: '2px', background: 'transparent', border: 'none' }}>
                        <span className={styles.text_12_n}>Proceed to Deny</span>
                    </button>
                </div>
              ) : (
                <div style={{ display: 'inline-flex', marginTop: '16px', gap: '8px' }}>
                    <button onClick={() => handleSelection(index, true, action.id)} className="secondary_button" style={{ paddingLeft: '10px', paddingTop: '2px' }}>
                        <Image style={{ marginTop: '4px' }} width={12} height={12} src="/images/check.svg" alt="check-icon" />
                        <span className={styles.text_12_n}>Approve</span>
                    </button>
                    <button onClick={() => handleDeny(index)} className="secondary_button" style={{ paddingLeft: '10px', paddingTop: '2px', background: 'transparent', border: 'none' }}>
                        <Image style={{ marginTop: '4px' }} width={16} height={16} src="/images/close.svg" alt="close-icon" />
                        <span className={styles.text_12_n}>Deny</span>
                    </button>
                </div>
              )}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', paddingLeft: '0', paddingBottom: '0' }} className={styles.tab_text}>
              <div>
                  <Image width={12} height={12} src="/images/schedule.svg" alt="schedule-icon" />
              </div>
              <div className={styles.history_info}>{formatTime(action.created_at)}</div>
          </div>
      </div>
    );
}

export default function ActionConsole({ actions }) {
    const [hiddenActions, setHiddenActions] = useState([]);
    const [denied, setDenied] = useState([]);
    const [reasons, setReasons] = useState([]);
    const [localActionIds, setLocalActionIds] = useState([]);

    useEffect(() => {
        const updatedActions = actions?.filter((action) => !localActionIds.includes(action.id));

        if (updatedActions && updatedActions.length > 0) {
            setLocalActionIds((prevIds) => [...prevIds, ...updatedActions.map(({ id }) => id)]);

            setDenied((prevDenied) => prevDenied.map((value, index) => updatedActions[index] ? false : value));
            setReasons((prevReasons) => prevReasons.map((value, index) => updatedActions[index] ? '' : value));
        }
    }, [actions]);

    const handleDeny = (index) => {
        setDenied((prevDenied) => {
            const newDeniedState = [...prevDenied];
            newDeniedState[index] = !newDeniedState[index];
            return newDeniedState;
        });
    };

    const handleSelection = (index, status, permissionId) => {
        setHiddenActions((prevHiddenActions) => [...prevHiddenActions, index]);

        const data = {
            status: status,
            user_feedback: reasons[index],
        };

        updatePermissions(permissionId, data).then((response) => {});
    };

    return (
      <>
          {actions?.some((action) => action.status === 'PENDING') ? (
            <div className={styles.detail_body} style={{ height: 'auto' }}>
                {actions.map((action, index) => {
                    if (action.status === 'PENDING' && !hiddenActions.includes(index)) {
                        return (<ActionBox key={action.id} action={action} index={index} denied={denied} setReasons={setReasons}
                            reasons={reasons} handleDeny={handleDeny} handleSelection={handleSelection}/>);
                    }
                    return null;
                })}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '40px' }}>
                <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions" />
                <span className={styles.feed_title} style={{ marginTop: '8px' }}>No Actions to Display!</span>
            </div>
          )}
      </>
    );
}
