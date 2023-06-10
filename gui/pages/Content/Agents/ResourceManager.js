import React, {useState, useRef, useEffect} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {getResources, uploadFile} from "@/pages/api/DashboardService";
import {formatBytes, downloadFile} from "@/utils/utils";

export default function ResourceManager({agentId}) {
  const [output, setOutput] = useState([]);
  const [input, setInput] = useState([]);
  const [channel, setChannel] = useState('input')
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);
  const pdf_icon = '/images/pdf_file.svg'
  const txt_icon = '/images/txt_file.svg'
  const img_icon = '/images/img_file.svg'

  const handleFileInputChange = (event) => {
    const files = event.target.files;
    if (files.length > 0) {
      const fileData = {
        "file": files[0],
        "name": files[0].name,
        "size": files[0].size,
        "type": files[0].type,
      };
      uploadResource(fileData);
    }
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
    if (files.length > 0) {
      const fileData = {
        "file": files[0],
        "name": files[0].name,
        "size": files[0].size,
        "type": files[0].type,
      };
      uploadResource(fileData);
    }
  };

  useEffect(() => {
    fetchResources();
  }, [agentId]);

  function uploadResource(fileData) {
    const formData = new FormData();
    formData.append('file', fileData.file);
    formData.append('name', fileData.name);
    formData.append('size', fileData.size);
    formData.append('type', fileData.type);

    uploadFile(agentId, formData)
      .then((response) => {
        fetchResources();
        toast.success('Resource added successfully', { autoClose: 1800 });
      })
      .catch((error) => {
        toast.error(error, { autoClose: 1800 });
        console.error('Error uploading resource:', error);
      });
  }

  function fetchResources() {
    getResources(agentId)
      .then((response) => {
        const resources = response.data;
        const inputFiles = resources.filter((resource) => resource.channel === 'INPUT');
        const outputFiles = resources.filter((resource) => resource.channel === 'OUTPUT');
        setInput(inputFiles);
        setOutput(outputFiles);
      })
      .catch((error) => {
        console.error('Error fetching resources:', error);
      });
  }

  const ResourceItem = ({ file }) => {
    const isPDF = file.type === 'application/pdf';
    const isTXT = file.type === 'application/txt' || file.type === 'text/plain';
    const isIMG = file.type.includes('image');

    return (
      <div onClick={() => downloadFile(file.id)} className={styles.history_box} style={{ background: '#272335', padding: '0px 10px', width: '49.5%' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-start' }}>
          {isPDF && <div><Image width={28} height={46} src={pdf_icon} alt="pdf-icon" /></div>}
          {isTXT && <div><Image width={28} height={46} src={txt_icon} alt="txt-icon" /></div>}
          {isIMG && <div><Image width={28} height={46} src={img_icon} alt="img-icon" /></div>}
          {!isTXT && !isPDF && !isIMG && <div><Image width={28} height={46} src="/images/default_file.svg" alt="file-icon" /></div>}
          <div style={{ marginLeft: '5px', width:'100%' }}>
            <div style={{ fontSize: '11px' }} className={styles.single_line_block}>{file.name}</div>
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
          <button onClick={() => setChannel('input')} className={styles.tab_button} style={channel === 'input' ? {background:'#454254',padding:'5px 10px'} : {background:'transparent',padding:'5px 10px'}}>
            Input
          </button>
        </div>
        <div>
          <button onClick={() => setChannel('output')} className={styles.tab_button} style={channel === 'output' ? {background:'#454254',padding:'5px 10px'} : {background:'transparent',padding:'5px 10px'}}>
            Output
          </button>
        </div>
      </div>
    </div>
    <div className={styles.detail_body} style={{height:'auto'}}>
      {channel === 'input' && <div style={{paddingBottom:'10px'}}>
        <div className={`file-drop-area ${isDragging ? 'dragging' : ''}`} onDragEnter={handleDragEnter} onDragLeave={handleDragLeave} onDragOver={handleDragOver} onDrop={handleDrop} onClick={handleDropAreaClick}>
          <div><p style={{textAlign:'center',color:'white',fontSize:'14px'}}>+ Choose or drop a file here</p>
          <p style={{textAlign:'center',color:'#888888',fontSize:'12px'}}>Supported file format .txt</p>
            <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileInputChange}/></div>
        </div>
      </div>}
      <ResourceList files={channel === 'output' ? output : input} />
    </div>
    <ToastContainer/>
  </>)
}