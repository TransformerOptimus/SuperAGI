import React, {useState} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function ResourceManager() {
  const [channel, setChannel] = useState('input')
  const [inputText, setInputText] = useState("")
  const outputFiles = [
    { name: 'name', type: 'pdf', size: '15MB', internal_files: [], icon: '/images/pdf_file.png' },
    { name: 'name', type: 'pdf', size: '24MB', internal_files: [], icon: '/images/pdf_file.png' },
    { name: 'name', type: 'txt', size: '128KB', internal_files: [], icon: '/images/txt_file.png' },
  ]

  const handleTextChange = (event) => {
    setInputText(event.target.value);
  };

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
      {channel === 'output' ? <div>{outputFiles.map((file, index) => (<div key={index} className={styles.history_box} style={{background:'#272335',padding:'0px 10px'}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'flex-start'}}>
          <div><Image width={28} height={46} src={file.icon} alt="file-icon"/></div>
          <div style={{marginLeft:'5px'}}>
            <div style={{fontSize:'11px'}}>{file.name}</div>
            <div style={{color:'#888888',fontSize:'9px'}}>{file.type}{file.size !== '' ? ` • ${file.size}` : ''}{file.internal_files.length > 0 ? ` • ${file.internal_files.length} files` : ''}</div>
          </div>
        </div>
      </div>))}</div> : <div>
        <div className={styles.history_box} style={{background:'#272335',padding:'10px'}}>
          <div>Text input</div>
          <div style={{marginTop:'10px',fontFamily:'Source Code Pro'}}>
            <textarea placeholder="Paste your text here" className="textarea_medium" rows={20} value={inputText} onChange={handleTextChange}/>
          </div>
          <div style={{marginTop:'10px',display:'flex',alignItems:'center',justifyContent:'flex-end'}}>
            <button className={styles.agent_button} onClick={updateEmbedding}>
              Update Embedding
            </button>
          </div>
        </div>
      </div>}
    </div>
    <ToastContainer/>
  </>)
}