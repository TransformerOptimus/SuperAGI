import React, {useState, useRef} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function ResourceManager({agentId}) {
  const [channel, setChannel] = useState('input')
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);
  const pdf_icon = '/images/pdf_file.svg'
  const txt_icon = '/images/txt_file.svg'

  const handleFileInputChange = (event) => {
    const files = event.target.files;
    setInput((prevArray) => [...prevArray, files[0]]);
  };

  const handleDropAreaClick = () => {
    fileInputRef.current.click();
  };

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
    setInput((prevArray) => [...prevArray, files[0]]);
  };

  const outputFiles = [
    { name: 'output_file1', type: 'application/txt', size: '128KB' },
    { name: 'output_file2', type: 'application/txt', size: '128KB' },
    { name: 'output_file3', type: 'application/txt', size: '128KB' },
  ]

  const inputFiles = [
    { name: 'input_file1', type: 'application/pdf', size: '15MB' },
    { name: 'input_file2', type: 'application/pdf', size: '24MB' },
    { name: 'input_file3', type: 'application/txt', size: '128KB' },
    { name: 'input_file4', type: 'application/txt', size: '128KB' },
  ]

  const [output, setOutput] = useState(outputFiles);
  const [input, setInput] = useState(inputFiles);

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
      {channel === 'input' && <div style={{paddingBottom:'10px'}}>
        <div className={`file-drop-area ${isDragging ? 'dragging' : ''}`} onDragEnter={handleDragEnter} onDragLeave={handleDragLeave} onDragOver={handleDragOver} onDrop={handleDrop} onClick={handleDropAreaClick}>
          <div><p style={{textAlign:'center',color:'white',fontSize:'14px'}}>+ Choose or drop a file here</p>
          <p style={{textAlign:'center',color:'#888888',fontSize:'12px'}}>File Formats .pdf, .txt</p>
            <input type="file" ref={fileInputRef} accept=".pdf,.txt" style={{ display: 'none' }} onChange={handleFileInputChange}/></div>
        </div>
      </div>}
      <div className={styles.resources}>
        {channel === 'output' && output.map((file, index) => (<div key={index} className={styles.history_box} style={{background:'#272335',padding:'0px 10px',width:'49.5%'}}>
          <div style={{display:'flex',alignItems:'center',justifyContent:'flex-start'}}>
            {file.type === 'application/pdf' && <div><Image width={28} height={46} src={pdf_icon} alt="file-icon"/></div>}
            {file.type === 'application/txt' && <div><Image width={28} height={46} src={txt_icon} alt="file-icon"/></div>}
            <div style={{marginLeft:'5px'}}>
              <div style={{fontSize:'11px'}} className={styles.tool_text}>{file.name}</div>
              <div style={{color:'#888888',fontSize:'9px'}}>{file.type.split("/")[1]}{file.size !== '' ? ` • ${file.size}` : ''}</div>
            </div>
          </div>
        </div>))}
        {channel === 'input' && input.map((file, index) => (<div key={index} className={styles.history_box} style={{background:'#272335',padding:'0px 10px',width:'49.5%'}}>
          <div style={{display:'flex',alignItems:'center',justifyContent:'flex-start'}}>
            {file.type === 'application/pdf' && <div><Image width={28} height={46} src={pdf_icon} alt="file-icon"/></div>}
            {file.type === 'application/txt' && <div><Image width={28} height={46} src={txt_icon} alt="file-icon"/></div>}
            <div style={{marginLeft:'5px'}}>
              <div style={{fontSize:'11px'}} className={styles.tool_text}>{file.name}</div>
              <div style={{color:'#888888',fontSize:'9px'}}>{file.type.split("/")[1]}{file.size !== '' ? ` • ${file.size}` : ''}</div>
            </div>
          </div>
        </div>))}
      </div>
    </div>
    <ToastContainer/>
  </>)
}