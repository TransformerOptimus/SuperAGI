import React, {useState, useRef, useEffect} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {getResources, uploadFile} from "@/pages/api/DashboardService";
import {formatBytes, downloadFile} from "@/utils/utils";

export default function ResourceManager({agentId, runs}) {
  const [output, setOutput] = useState([]);
  const [input, setInput] = useState([]);
  const [channel, setChannel] = useState('input')
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);
  const pdf_icon = '/images/pdf_file.svg'
  const txt_icon = '/images/txt_file.svg'
  const img_icon = '/images/img_file.svg'
  const initialItems = [
    { name: ["Item 1",'Item 5'], run: 1 },
    { name: ["Item 2","Item 6"], run: 2 },
    // Add more items here as needed
  ];
  const [items, setItems] = useState([]);

  const handleClick = (index) => {
    setItems(items.map((item, i) => {
      if(i === index) {
        return {...item, isOpen: !item.isOpen};
      }
      return item;
    }));
  };


  useEffect(() => {
    const updatedItems = runs.map(item => {
      const initialItem = initialItems.find(initial => initial.run === item.id);
      if (initialItem) {
        return { ...item, file_name: initialItem.name };
      }
      return item;
    });
    setItems(updatedItems);
    console.log(updatedItems)
  }, []);

  useEffect(() => {
    console.log('items:', items);
  }, [items]);

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
    console.log(file)
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
          <div style={{ width:'100%' }} className='row'>
            <div style={{ fontSize: '11px', display: 'flex',  justifyContent: 'space-between' }} className='col-12'>
              <div className={styles.single_line_block}>{file.name}</div>
              {file.channel === 'output' && <div>
                <Image width={14} height={14} src="/images/download_icon.svg" alt="download-icon"/>
              </div>}
            </div>
           <div style={{ color: '#888888', fontSize: '9px' }}>{file.type.split("/")[1]}{file.size !== '' ? ` • ${formatBytes(file.size)}` : ''}</div>
          </div>
        </div>
      </div>
    );
  };

  const ResourceList = ({ files }) => (
    <div>
      {files.length <= 0 && channel === 'output' ? <div style={{display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',marginTop:'40px',width:'100%'}}>
        <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions" />
        <span className={styles.feed_title} style={{marginTop: '8px'}}>No Output files!</span>
      </div> : <div className={styles.resources}>
        {files.map((file, index) => (
          <ResourceItem key={index} file={file} />
        ))}
      </div>
      }
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
      {channel === 'output' && <div>
        {items.map((item, index) => (
            <div key={index}>
              <div onClick={() => handleClick(index)} className={styles.resource_runs}>
                <Image src={item.isOpen ? "/images/arrow_down.svg" : "/images/arrow_forward.svg"} width={11} height={11}
                       alt="expand-arrow"/>
                {item.name}
                <span class={styles.run_count}>
                <Image src="/images/bolt_icon.svg" width={10} height={12}
                       alt="expand-arrow"/>Run 1</span>
              </div>
              {item.isOpen && item.file_name && item.file_name.map((subItem, subIndex) => (
                  <div key={subIndex} style={{marginLeft: '20px'}}>
                    {subItem}
                  </div>
              ))}
            </div>
        ))}
      </div>}
      <ResourceList files={channel === 'output' ? output : input} />
    </div>
    <ToastContainer/>
  </>)
}