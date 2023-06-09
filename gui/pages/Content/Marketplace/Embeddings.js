import React from "react";
import Image from "next/image";
import styles from './Market.module.css';

export default function Embeddings(){
    return(
        <div>
        <div className={styles.history_box}>
        Embeddings
        </div>
        <div className={styles.featured_text}>Top featured</div>
        <div className={styles.featured_text}>New Tools</div>
        </div>
    )
};
