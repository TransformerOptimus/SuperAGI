import React, {useState, useRef, useEffect} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {getResources, uploadResource} from "@/app/DashboardService";

export default function ResourceManager({selectedProjectId}) {
  console.log(selectedProjectId)
  const [output, setOutput] = useState([]);
  const [input, setInput] = useState([]);
  const [channel, setChannel] = useState('input')
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);
  const pdf_icon = '/images/pdf_file.svg'
  const txt_icon = '/images/txt_file.svg'

  const handleFileInputChange = (event) => {
    const files = event.target.files;
    const fileData = {"name": files[0].name, "size": files[0].size, "type": files[0].type, "channel": 'INPUT'}
    uploadFile(fileData);
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
    const fileData = {"name": files[0].name, "size": files[0].size, "type": files[0].type, "channel": 'INPUT'}
    uploadFile(fileData);
  };

  useEffect(() => {
    fetchResources(selectedProjectId);
  }, [selectedProjectId]);

  function uploadFile(fileData) {
    uploadResource(selectedProjectId, fileData)
      .then((response) => {
        fetchResources(selectedProjectId);
        toast.success('Resource added successfully', {autoClose: 1800});
      })
      .catch((error) => {
        console.error('Error uploading resource:', error);
      });
  }

  function fetchResources(selectedProjectId) {
    getResources(selectedProjectId)
      .then((response) => {
        const resources = response.data;
        const inputFiles = resources.filter((resource) => resource.channel === 'INPUT');
        const outputFiles = resources.filter((resource) => resource.channel === 'OUTPUT');
        console.log(inputFiles)
        console.log(outputFiles)
        setInput(inputFiles);
        setOutput(outputFiles);
      })
      .catch((error) => {
        console.error('Error fetching resources:', error);
      });
  }

  function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) {
      return '0 Bytes';
    }

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    const formattedValue = parseFloat((bytes / Math.pow(k, i)).toFixed(decimals));
    
    return `${formattedValue} ${sizes[i]}`;
  }

  const ResourceItem = ({ file }) => {
    const isPDF = file.type === 'application/pdf';
    const isTXT = file.type === 'application/txt';

    return (
      <div className={styles.history_box} style={{ background: '#272335', padding: '0px 10px', width: '49.5%' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-start' }}>
          {isPDF && <div><Image width={28} height={46} src={pdf_icon} alt="file-icon" /></div>}
          {isTXT && <div><Image width={28} height={46} src={txt_icon} alt="file-icon" /></div>}
          <div style={{ marginLeft: '5px' }}>
            <div style={{ fontSize: '11px' }} className={styles.tool_text}>{file.name}</div>
            <div style={{ color: '#888888', fontSize: '9px' }}>{file.type.split("/")[1]}{file.size !== '' ? ` • ${formatBytes(file.size)}` : ''}</div>
          </div>
        </div>
      </div>
    );
  };

  const ResourceList = ({ files }) => (
    <div className={styles.resources}>
      {files.map((file, index) => (
        <ResourceItem key={index} file={file} />
      ))}
    </div>
  );

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
            output
          </button>
        </div>
      </div>
    </div>
    <div className={styles.detail_body} style={{height:'auto'}}>
      {channel === 'input' && <div style={{paddingBottom:'10px'}}>
        <div className={`file-drop-area ${isDragging ? 'dragging' : ''}`} onDragEnter={handleDragEnter} onDragLeave={handleDragLeave} onDragOver={handleDragOver} onDrop={handleDrop} onClick={handleDropAreaClick}>
          <div><p style={{textAlign:'center',color:'white',fontSize:'14px'}}>+ Choose or drop a file here</p>
          <p style={{textAlign:'center',color:'#888888',fontSize:'12px'}}>Supported file format .txt</p>
            <input type="file" ref={fileInputRef} accept=".pdf,.txt" style={{ display: 'none' }} onChange={handleFileInputChange}/></div>
        </div>
      </div>}
      <ResourceList files={channel === 'output' ? output : input} />
    </div>
    <ToastContainer/>
  </>)
}