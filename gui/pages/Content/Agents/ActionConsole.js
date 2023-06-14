import React, { useState } from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import {updatePermissions} from "@/pages/api/DashboardService";

export default function ActionConsole({ actions }) {
    const [hiddenActions, setHiddenActions] = useState([]);
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

    const handleSelection = (index,status,permissionId) => {
        setHiddenActions([...hiddenActions, index])
        updatePermissions(permissionId,status).then((response) => {
            console.log("voila")
        })
    }

    return (<>
            <div className={styles.detail_body} style={{ height: "auto" }}>
                {actions.map(
                    (action, index) =>
                        action.status === null && !hiddenActions.includes(index) && (
                            <div key={index} className={styles.history_box} style={{ background: "#272335", padding: "16px", cursor: "default" }}>
                                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                                    <div>Tool <b>{action.tool_name}</b> is seeking for Permissions</div>
                                    <div style={{ display: "inline-flex"}}>
                                        <button onClick={() => handleSelection(index,false,action.id)} className="secondary_button" style={{ marginLeft: "4px", padding: "5px", background: "transparent", border: "none" }}>
                                            <Image width={20} height={20} src="/images/close.svg" alt="close-icon" />
                                        </button>
                                        <button onClick={() => handleSelection(index,true,action.id)} className="secondary_button" style={{ marginLeft: "4px", padding: "4px 7px" }}>
                                            <Image width={16} height={16} src="/images/check.svg" alt="check-icon" />
                                        </button>
                                    </div>
                                </div>
                                <div style={{ display: "flex", alignItems: "center", paddingLeft: "0", paddingBottom: "0" }} className={styles.tab_text}>
                                    <div>
                                        <Image width={12} height={12} src="/images/schedule.svg" alt="schedule-icon" />
                                    </div>
                                    <div className={styles.history_info}>{formatDate(action.created_at)}</div>
                                </div>
                            </div>
                        )
                )}
            </div>
        </>
    );
}