import React from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import {downloadFile, formatBytes, returnResourceIcon} from "@/utils/utils";

export default function ResourceList({files, channel}) {
  return (<div>
    {files.length <= 0 && channel === 'output' ? <div style={{display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',marginTop:'40px',width:'100%'}}>
      <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions" />
      <span className={styles.feed_title} style={{marginTop: '8px'}}>No Output files!</span>
    </div> : <div className={styles.resources}>
      {files.map((file, index) => (
        <div key={index} onClick={() => downloadFile(file.id, file.name)} className={styles.history_box} style={{ background: '#272335', padding: '0px 10px', width: '49.5%' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-start' }}>
            <div><Image width={28} height={46} src={returnResourceIcon(file)} alt="pdf-icon" /></div>
            <div style={{ marginLeft: '5px', width:'100%' }}>
              <div style={{ fontSize: '11px' }} className={styles.single_line_block}>{file.name}</div>
              <div style={{ color: '#888888', fontSize: '9px' }}>{file.type.split("/")[1]}{file.size !== '' ? ` • ${formatBytes(file.size)}` : ''}</div>
            </div>
          </div>
        </div>
      ))}
    </div>
    }
  </div>)
}