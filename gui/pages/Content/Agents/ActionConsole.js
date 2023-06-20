import React, { useState, useEffect } from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import { updatePermissions } from '@/pages/api/DashboardService';

export default function ActionConsole({ actions }) {
    const [hiddenActions, setHiddenActions] = useState([]);
    const [reasons, setReasons] = useState(actions.map(() => ''));
    const [localActions, setLocalActions] = useState(actions);
    const [denied, setDenied] = useState([]);
    const [localActionIds, setLocalActionIds] = useState([]);

    useEffect(() => {
        const updatedActions = actions.filter(
            (action) => !localActionIds.includes(action.id)
        );

        if (updatedActions.length > 0) {
            setLocalActions(
                localActions.map((localAction) =>
                    updatedActions.find(({ id }) => id === localAction.id) || localAction
                )
            );

            const updatedDenied = updatedActions.map(() => false);
            const updatedReasons = updatedActions.map(() => '');

            setDenied((prev) => prev.map((value, index) => updatedDenied[index] || value));
            setReasons((prev) => prev.map((value, index) => updatedReasons[index] || value));

            setLocalActionIds([...localActionIds, ...updatedActions.map(({ id }) => id)]);
        }
    }, [actions]);

    const handleDeny = index => {
        const newDeniedState = [...denied];
        newDeniedState[index] = !newDeniedState[index];
        setDenied(newDeniedState);
    };

    const formatDate = (dateString) => {
        const now = new Date();
        const date = new Date(dateString);
        const seconds = Math.floor((now - date) / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        const weeks = Math.floor(days / 7);
        const months = Math.floor(days / 30);
        const years = Math.floor(days / 365);

        if (years > 0) return `${years} yr${years === 1 ? '' : 's'}`;
        if (months > 0) return `${months} mon${months === 1 ? '' : 's'}`;
        if (weeks > 0) return `${weeks} wk${weeks === 1 ? '' : 's'}`;
        if (days > 0) return `${days} day${days === 1 ? '' : 's'}`;
        if (hours > 0) return `${hours} hr${hours === 1 ? '' : 's'}`;
        if (minutes > 0) return `${minutes} min${minutes === 1 ? '' : 's'}`;

        return `${seconds} sec${seconds === 1 ? '' : 's'}`;
    };

    const handleSelection = (index, status, permissionId) => {
        setHiddenActions([...hiddenActions, index]);

        const data = {
            status: status,
            user_feedback: reasons[index],
        };

        updatePermissions(permissionId, data).then((response) => {
            console.log("voila")
        });
    };

    return (
        <>
            {actions.some(action => action.status === "PENDING") ? (<div className={styles.detail_body} style={{ height: "auto" }}>
                {actions.map((action, index) => action.status === "PENDING" && !hiddenActions.includes(index) && (
                    <div key={index} className={styles.history_box} style={{ background: "#272335", padding: "16px", cursor: "default" }}>
                        <div style={{ display: "flex", flexDirection: 'column' }}>
                            <div>Tool <b>{action.tool_name}</b> is seeking for Permissions</div>
                            {denied[index] && (
                                <div style={{marginTop: '26px' }}>
                                    <div>Provide Feedback <span style={{color: '#888888'}}>(Optional)</span></div>
                                    <input style={{marginTop: '6px'}} type="text" value={reasons[index]} onChange={(e) => {const newReasons = [...reasons];newReasons[index] = e.target.value;setReasons(newReasons);}} placeholder="Enter your input here" className="input_medium" />
                                </div>
                            )}
                            {denied[index] ? (
                                <div style={{ display: "inline-flex", marginTop: '16px',gap: '8px' }}>
                                    <button onClick={() => handleDeny(index)} className="secondary_button"><Image width={12} height={12} src="/images/undo.svg" alt="check-icon" /><span className={styles.text_12_n}>Go Back</span></button>
                                    <button onClick={() => handleSelection(index, false, action.id)} className="secondary_button" style={{ marginLeft: "4px", padding: "5px", background: "transparent", border: "none" }}><span className={styles.text_12_n}>Proceed to Deny</span></button>
                                </div>
                            ) : (
                                <div style={{ display: "inline-flex", marginTop: '16px',gap: '8px'  }}>
                                    <button onClick={() => handleSelection(index, true, action.id)} className="secondary_button"><Image width={12} height={12} src="/images/check.svg" alt="check-icon" /><span className={styles.text_12_n}>Approve</span></button>
                                    <button onClick={() => handleDeny(index)} className="secondary_button" style={{ marginLeft: "4px", padding: "5px", background: "transparent", border: "none" }}><Image width={16} height={16} src="/images/close.svg" alt="close-icon" /><div className={styles.text_12_n}>Deny</div></button>
                                </div>
                            )}
                        </div>
                        <div style={{ display: "flex", alignItems: "center", paddingLeft: "0", paddingBottom: "0" }} className={styles.tab_text}>
                            <div>
                                <Image width={12} height={12} src="/images/schedule.svg" alt="schedule-icon" />
                            </div>
                            <div className={styles.history_info}>{formatDate(action.created_at)}</div>
                        </div>
                    </div>
                ))}
            </div>):
                (
                    <div style={{display:'flex',flexDirection:'column',alignItems:'center',marginTop:'40px'}}>
                        <Image width={150} height={60} src="/images/no_permissions.svg" alt="no permissions" />
                        <span className={styles.feed_title} style={{marginTop: '8px'}}>No Actions to Display!</span>
                    </div>)}
        </>
    );
}