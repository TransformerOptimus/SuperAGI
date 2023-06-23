import React from "react";
import Image from "next/image";
import styles from './Market.module.css';

export default function Embeddings(){
    const dummyData = [];
    const numIterations = 6;
    const itemsPerRow = 3;

    for (let i = 0; i < numIterations; i++) {
      const dummyItem = {
        id: i,
        toolName: `Tool ${i + 1}`,
        author: 'Google',
        imageSrc: '/images/gmail.png',
        altText: 'empty-state',
      };
  
      dummyData.push(dummyItem);
    }

    return(
        <div>
          <div className={styles.history_box}>Embeddings</div>
          <div className={styles.featured_text}>Top featured</div>

          <div className={styles.rowContainer}>
            {dummyData.map((item, index) => (
              <div className={styles.market_tool} key={item.id}>
                <div style={{ padding: '12px' }}>
                  <Image width={35} height={35} src={item.imageSrc} alt={item.altText} />
                </div>
                <div style={{ display: 'inline' }}>
                  <div style={{ paddingTop: '12px', paddingLeft: '6px' }}>{item.toolName}</div>
                  <div style={{ paddingLeft: '6px', fontSize: 'x-small', color: 'rgb(96, 96, 96)' }}>by {item.author}</div>
                </div>
                {/* Add a line break after each row */}
                {(index + 1) % itemsPerRow === 0 && <br />}
              </div>
            ))}
          </div>

          <div className={styles.featured_text}>New Tools</div>

          <div className={styles.rowContainer}>
            {dummyData.map((item, index) => (
              <div className={styles.market_tool} key={item.id}>
                <div style={{ padding: '12px' }}>
                  <Image width={35} height={35} src={item.imageSrc} alt={item.altText} />
                </div>
                <div style={{ display: 'inline' }}>
                  <div style={{ paddingTop: '12px', paddingLeft: '6px' }}>{item.toolName}</div>
                  <div style={{ paddingLeft: '6px', fontSize: 'x-small', color: 'rgb(96, 96, 96)' }}>by {item.author}</div>
                </div>
                {/* Add a line break after each row */}
                {(index + 1) % itemsPerRow === 0 && <br />}
              </div>
            ))}
          </div>

        </div>
    )
};
