import React from 'react';
import Image from "next/image";
import styles from './Market.module.css';
import Market from './Market';

export default function MarketplacePublic() {
    function handleSignupClick() {
        if (window.location.href.toLowerCase().includes('localhost')) {
            window.location.href = '/';
        }
        else
            window.open(`https://app.superagi.com/`, '_self')
    }

    return (
        <div style={{height:'100vh',width:'100%'}}>
             <div style={{height:'6.5vh',display:'flex',width:'100%'}}>
                 <div className="superAgiLogo" style={{paddingLeft:'24px'}}><Image width={132} height={24} src="/images/sign-in-logo.svg" alt="super-agi-logo"/>
                    <div className={styles.vertical_line} />
                    <div className={styles.topbar_heading}>&nbsp;marketplace</div>
                 </div>
                 <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center',width:'100%',paddingRight:'24px' }}>
                     <button className="primary_button" onClick={handleSignupClick}>Try for free today!</button>
                 </div>
             </div>
            <div style={{height:'92.5vh',width:'99vw',background: 'rgba(255, 255, 255, 0.08)',marginLeft:'8px',borderRadius: '8px'}}>
                <Market />
            </div>
        </div>
    );
};


