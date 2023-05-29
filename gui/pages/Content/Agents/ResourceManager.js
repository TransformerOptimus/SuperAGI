import React, {useState} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function ResourceManager() {
  const [channel, setChannel] = useState('input')
  const [isDragging, setIsDragging] = useState(false);

  const handleDragEnter = (event) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);

    const files = event.dataTransfer.files;
    console.log(files);
  };

  const outputFiles = [
    { name: 'output_file1', type: '.txt', size: '128KB', icon: '/images/txt_file.svg' },
    { name: 'output_file2', type: 'txt', size: '128KB', icon: '/images/txt_file.svg' },
    { name: 'output_file3', type: 'txt', size: '128KB', icon: '/images/txt_file.svg' },
  ]

  const inputFiles = [
    { name: 'input_file1', type: '.pdf', size: '15MB', icon: '/images/pdf_file.svg' },
    { name: 'input_file2', type: '.pdf', size: '24MB', icon: '/images/pdf_file.svg' },
    { name: 'input_file3', type: '.txt', size: '128KB', icon: '/images/txt_file.svg' },
    { name: 'input_file4', type: '.txt', size: '128KB', icon: '/images/txt_file.svg' },
  ]

  const finalFiles = channel === 'input' ? inputFiles : outputFiles

  const updateEmbedding = () => {
    toast.dark('Embedding updated', {autoClose: 1800});
  }

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
      <div className={`file-drop-area ${isDragging ? 'dragging' : ''}`} onDragEnter={handleDragEnter} onDragLeave={handleDragLeave} onDragOver={handleDragOver} onDrop={handleDrop}>

      </div>
      {finalFiles.map((file, index) => (<div key={index} className={styles.history_box} style={{background:'#272335',padding:'0px 10px'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'flex-start'}}>
          <div><Image width={28} height={46} src={file.icon} alt="file-icon"/></div>
          <div style={{marginLeft:'5px'}}>
            <div style={{fontSize:'11px'}}>{file.name}</div>
            <div style={{color:'#888888',fontSize:'9px'}}>{file.type}{file.size !== '' ? ` • ${file.size}` : ''}</div>
          </div>
        </div>
      </div>))}
    </div>
    <ToastContainer/>
  </>)
}