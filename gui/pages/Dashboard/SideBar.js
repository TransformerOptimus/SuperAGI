import React, {useState} from 'react';
import Image from 'next/image';
import styles from './Dashboard.module.css';
import {openNewTab} from "@/utils/utils";

export default function SideBar({onSelectEvent, env}) {
    const [sectionSelected, setSelection] = useState('');

    const sections = [
        { name: 'agents', icon: '/images/agents_light.svg' },
        { name: 'toolkits', icon: '/images/tools_light.svg' },
        { name: 'apm', icon: '/images/apm.svg' },
        { name: 'knowledge', icon: '/images/knowledge.svg' },
    ];

    const handleClick = (value) => {
        setSelection(value);
        onSelectEvent(value);
        if (value === 'apm') {
            openNewTab(-9, "APM", "APM", false);
        }
    };

    return (
        <div className="side_bar">
            <Image width={72} height={56} className="cursor_default mt_4 mb_4"
                   src={env === 'PROD' ? '/images/superagi_logo_beta.png' : '/images/superagi_logo.png'} alt="super-agi-logo"/>

            {sections.map((section) => (
                <div key={section.name} className="w_100 mb_5">
                    <div onClick={() => handleClick(sectionSelected !== section.name ? section.name : '')}
                         className={`${styles.section} ${sectionSelected === section.name ? styles.selected : ''}`}>
                        <div className={styles.button_icon}>
                            <Image width={17} height={17} src={section.icon} alt={`${section.name}-icon`}/>
                        </div>
                        <div>{section.name.charAt(0).toUpperCase() + section.name.slice(1)}</div>
                    </div>
                </div>
            ))}
        </div>
    );
}