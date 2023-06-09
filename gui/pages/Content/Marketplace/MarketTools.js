import React, { useState, useEffect, useRef } from 'react';
import Image from "next/image";
import styles from './Market.module.css';

export default function MarketTools() {
  return (
    <div>
    <div className={styles.history_box}>
        Tools
    </div>
    <div className={styles.featured_text}>Top featured</div>
    <div className={styles.featured_text}>New Tools</div>
    </div>
  );
};


