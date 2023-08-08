import React from 'react';
import Image from "next/image";
import styles from './Market.module.css';
import Market from './Market';

export default function MarketplacePublic({env}) {
  const handleSignupClick = () => {
    if (env === 'PROD') {
      window.open(`https://app.superagi.com/`, '_self');
    } else {
      window.location.href = '/';
    }
  };

  return (
    <div style={{height: '100vh', width: '100%'}}>
      <div className={styles.marketplace_public_container}>
        <div className="superAgiLogo" style={{paddingLeft: '15px'}}><Image width={132} height={24}
                                                                           style={{cursor: 'pointer'}}
                                                                           onClick={handleSignupClick}
                                                                           src="/images/sign-in-logo.svg"
                                                                           alt="super-agi-logo"/>
          <div className={styles.vertical_line}/>
          <div className={styles.topbar_heading}>&nbsp;Marketplace</div>
        </div>
        <div className={styles.marketplace_public_button}>
          <button className="primary_button" onClick={handleSignupClick}>Sign Up/Sign In</button>
        </div>
      </div>
      <div className={styles.marketplace_public_content}>
        <Market env={env}/>
      </div>
    </div>
  );
};


