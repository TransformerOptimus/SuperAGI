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

  function handleFile(files) {
    if (files.length > 0) {
      const sizeInMB = files[0].size / (1024 * 1024);
      if (sizeInMB > 5) {
        toast.error('File size should not exceed 5MB', {autoClose: 1800});
      } else {
        const fileData = {
          "file": files[0],
          "name": files[0].name,
          "size": files[0].size,
          "type": files[0].type,
        };
        uploadResource(fileData);
      }
    }
  };
  const handleFileInputChange = (event) => {
    const files = event.target.files;
    handleFile(files);
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
    handleFile(files);
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
        toast.success('Resource added successfully', {autoClose: 1800});
      })
      .catch((error) => {
        toast.error(error, {autoClose: 1800});
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
    <div className="detail_top mb_10">
      <button onClick={() => setChannel('input')} className={channel === 'input' ? 'tab_button_selected' : 'tab_button'}>Input</button>
      <button onClick={() => setChannel('output')} className={channel === 'output' ? 'tab_button_selected' : 'tab_button'}>Output</button>
    </div>
    <div className="w_100 mr_10 mb_20">
      {channel === 'input' &&
        <div className={`file-drop-area ${isDragging ? 'dragging' : ''}`} onDragEnter={handleDragEnter}
             onDragLeave={handleDragLeave} onDragOver={handleDragOver} onDrop={handleDrop}
             onClick={handleDropAreaClick}>
            <p className="text_14 text_align_center">+ Choose or drop a file here</p>
            <p className="text_12 text_align_center">Supported file formats are txt, pdf,
              docx, epub, csv, pptx only</p>
            <input type="file" ref={fileInputRef} style={{display: 'none'}} onChange={handleFileInputChange}/>
        </div>}
      <ResourceList files={channel === 'output' ? output : input} channel={channel} runs={runs}/>
    </div>
    <ToastContainer/>
  </>)
}