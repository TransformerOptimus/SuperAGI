import React, {useState, useRef, useEffect} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {getResources, uploadFile} from "@/pages/api/DashboardService";
import {downloadAllFiles} from "@/utils/utils";
import ResourceList from "@/pages/Content/Agents/ResourceList";

export default function ResourceManager({agentId, runs}) {
  const [output, setOutput] = useState([]);
  const [input, setInput] = useState([]);
  const [channel, setChannel] = useState('input')
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

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

  return (<>
    <div className={styles.detail_top} style={{height:'auto',marginBottom:'10px'}}>
      <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',width:'100%'}}>
        <div style={{display:'flex',order:0}}>
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
    </div>
    <div className={styles.detail_body} style={{height:'auto'}}>
      {channel === 'input' && <div style={{paddingBottom:'10px'}}>
        <div className={`file-drop-area ${isDragging ? 'dragging' : ''}`} onDragEnter={handleDragEnter} onDragLeave={handleDragLeave} onDragOver={handleDragOver} onDrop={handleDrop} onClick={handleDropAreaClick}>
          <div><p style={{textAlign:'center',color:'white',fontSize:'14px'}}>+ Choose or drop a file here</p>
          <p style={{textAlign:'center',color:'#888888',fontSize:'12px'}}>Supported file formats are txt, pdf, docx, epub, csv, pptx only</p>
            <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileInputChange}/></div>
        </div>
      </div>}
      <ResourceList files={channel === 'output' ? output : input} channel={channel} runs={runs}/>
    </div>
    <ToastContainer/>
  </>)
}