import React, { useState, useEffect, useRef } from 'react';
import Image from "next/image";
import styles from './Market.module.css';
import axios from "axios";


export default function MarketTools({ onToolClick }) {
  const [toolData, setToolData] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await axios.get('http://192.168.211.48:8001/tool_kits/get/list?page=0');
      setToolData(response.data);
    } catch (error) {
      console.log('Error fetching tool data:', error);
    }
  };
  const itemsPerRow = 3;

  const handleToolClick = () => {
    onToolClick(true);
  };

  return (
    <div className={styles.marketContainer}>
      <div className={styles.history_box}>Tools</div>
      <div className={styles.featured_text}>Top featured</div>

      <div className={styles.rowContainer}>
        {toolData.map((item, index) => {
          const toolCodeParts = item.tool_code_link.split('/');
          const fourthPart = toolCodeParts[3];

          return (
            <div className={styles.market_tool} key={item.id} onClick={handleToolClick}>
                <div style={{ padding: '12px' }}>
                  <Image width={35} height={35} src={item.imageSrc} alt={item.altText} />
                </div>
                <div style={{ display: 'inline' }}>
                    <div style={{ paddingTop: '12px', paddingLeft: '6px', paddingRight: '8px' }}>{item.name}</div>
                    <div style={{ paddingLeft: '6px', fontSize: 'x-small', color: 'rgb(96, 96, 96)' }}>
                      by {fourthPart}
                    </div>
                    <div style={{ paddingTop: '8px', color: 'rgb(96, 96, 96)' }}>{item.description}</div>
                </div>
                {/* Add a line break after each row */}
                {(index + 1) % itemsPerRow === 0 && <br />}
            </div>
          );
        })}
      </div>
    </div>
  );
}



