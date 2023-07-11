import React, {useState, useEffect} from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import {downloadFile, formatBytes, returnResourceIcon} from "@/utils/utils";

export default function ResourceList({files, channel, runs}) {
  const [selectedRun, setSelectedRun] = useState(null);
  const [filesByRun, setFilesByRun] = useState([]);

  useEffect(()=>{
    let filesGroupedByRun = [];
    runs.forEach((run) => {
      let relatedFiles = files.filter(file => file.agent_execution_id === run.id);
      if (relatedFiles.length !== 0){
        filesGroupedByRun.push({"run": run, "files": relatedFiles});
      }
    })
    setFilesByRun(filesGroupedByRun);
  }, [files, runs]);

  const isAnyFileWithAgentId = files.some(file => file.agent_execution_id !== null)

  return (<div>
    {(!isAnyFileWithAgentId || files.length <= 0) && channel === 'output' ? <div className="vertical_container">
      <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions" />
      <span className={styles.feed_title} style={{marginTop: '8px'}}>No Output files!</span>
    </div> : <div>
      {channel === 'output' && <div id="division_by_runs">
        {filesByRun.map((filesRun,index) => (
            <div key={index}>
              <div className="horizontal_container justify_space_between cursor_pointer" style={{padding: '8px 6px'}} onClick={() => setSelectedRun(filesRun.run === selectedRun ? null : filesRun.run)}>
                <div className="horizontal_container">
                  <Image src={selectedRun === filesRun.run ? "/images/arrow_downward.svg" : "/images/arrow_forward.svg"} alt="arrow" width={14} height={14} />
                  <span className="text_12 ml_8">{filesRun.run.name}</span>
                  <div className="resource_manager_tip ml_8"><Image src="/images/bolt.svg" alt="bolt" width={10} height={10} /> <span className="text_9">Run {index+1}</span></div>
                </div>
                <Image src="/images/download.svg" alt="download_icon" width={16} height={16} />
              </div>

              {selectedRun === filesRun.run && (
                  <div className={styles.resources}>
                    {filesRun.files.map((file, index) => (
                        <div key={index} onClick={() => downloadFile(file.id, file.name)} className={styles.history_box} style={{ background: '#272335', padding: '0px 10px', width: '49.5%' }}>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-start' }}>
                            <div><Image width={28} height={46} src={returnResourceIcon(file)} alt="file-icon" /></div>
                            <div style={{ marginLeft: '5px', width:'100%' }}>
                              <div style={{ fontSize: '11px' }} className={styles.single_line_block}>{file.name}</div>
                              <div style={{ color: '#888888', fontSize: '9px' }}>{file.type.split("/")[1]}{file.size !== '' ? ` • ${formatBytes(file.size)}` : ''}</div>
                            </div>
                          </div>
                        </div>
                    ))}
                  </div>)}
            </div>
        ))}
      </div>}

      {channel === 'input' && <div className={styles.resources}>
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
      </div>}
    </div>
    }
  </div>)
}