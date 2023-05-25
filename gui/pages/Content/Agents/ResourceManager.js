import React, {useState} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";

export default function ResourceManager() {
  const [channel, setChannel] = useState('input')
  const inputFiles = [
    { name: 'name', type: 'pdf', size: '1.2MB', internal_files: [], icon: '/images/pdf_file.png' },
    { name: 'name', type: 'xls', size: '1.2MB', internal_files: [], icon: '/images/xls_file.png' },
    { name: 'name', type: 'pdf', size: '1.2MB', internal_files: [], icon: '/images/pdf_file.png' },
    { name: 'name', type: 'zip', size: '1.2MB', internal_files: [
        { name: 'name', type: 'txt', size: '67KB', internal_files: [], icon: '/images/txt_file.png' },
        { name: 'name', type: 'txt', size: '128KB', internal_files: [], icon: '/images/txt_file.png' }
      ], icon: '/images/zip_file.png' },
    { name: 'name', type: 'txt', size: '67KB', internal_files: [], icon: '/images/txt_file.png' },
    { name: 'name', type: 'txt', size: '67KB', internal_files: [], icon: '/images/txt_file.png' },
    { name: 'name', type: 'txt', size: '128KB', internal_files: [], icon: '/images/txt_file.png' },
    { name: 'name', type: 'txt', size: '128KB', internal_files: [], icon: '/images/txt_file.png' },
    { name: 'name', type: 'txt', size: '128KB', internal_files: [], icon: '/images/txt_file.png' },
  ]

  const outputFiles = [
    { name: 'name', type: 'pdf', size: '15MB', internal_files: [], icon: '/images/pdf_file.png' },
    { name: 'name', type: 'pdf', size: '24MB', internal_files: [], icon: '/images/pdf_file.png' },
    { name: 'name', type: 'txt', size: '128KB', internal_files: [], icon: '/images/txt_file.png' },
  ]

  const finalFiles = channel === 'input' ? inputFiles : outputFiles

  return (<>
    <div className={styles.detail_top} style={{height:'auto',marginBottom:'10px'}}>
      <div style={{display:'flex',overflowX:'scroll'}}>
        <div>
          <button onClick={() => setChannel('input')} className={styles.tab_button} style={channel === 'input' ? {background:'#454254'} : {background:'transparent'}}>
            Input
          </button>
        </div>
        <div>
          <button onClick={() => setChannel('output')} className={styles.tab_button} style={channel === 'output' ? {background:'#454254'} : {background:'transparent'}}>
            Output
          </button>
        </div>
      </div>
    </div>
    <div className={styles.detail_body} style={{height:'auto'}}>
      {finalFiles.map((file, index) => (<div key={index} className={styles.history_box} style={{background:'#272335',padding:'0px 10px'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'flex-start'}}>
          <div><Image width={28} height={46} src={file.icon} alt="file-icon"/></div>
          <div style={{marginLeft:'5px'}}>
            <div style={{fontSize:'11px'}}>{file.name}</div>
            <div style={{color:'#888888',fontSize:'9px'}}>{file.type}{file.size !== '' ? ` • ${file.size}` : ''}{file.internal_files.length > 0 ? ` • ${file.internal_files.length} files` : ''}</div>
          </div>
        </div>
      </div>))}
    </div>
  </>)
}