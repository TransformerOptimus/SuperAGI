import React, { useState, useMemo } from 'react';
import styles from './Agents.module.css';
import Image from "next/image";
import { downloadFile, downloadAllFiles, formatBytes, returnResourceIcon } from "@/utils/utils";

export default function ResourceList({ files, channel, runs }) {
  const [selectedRun, setSelectedRun] = useState(null);
  const filesByRun = useMemo(() => runs.map(run => {
    const relatedFiles = files.filter(file => file.agent_execution_id === run.id);
    return relatedFiles.length !== 0 && { "run": run, "files": relatedFiles };
  }).filter(Boolean), [files, runs]);

  const downloadRunFiles = (run_id,name) => {
    const runFiles = files.filter(file => file.agent_execution_id === run_id);
    runFiles.length !== 0 && downloadAllFiles(runFiles,name);
  }

  const isAnyFileWithAgentId = files.some(file => file.agent_execution_id !== null)

  const File = ({ file, index }) => (
      <div key={index} onClick={() => downloadFile(file.id, file.name)} className={styles.history_box} style={{ background: '#272335', padding: '0px 10px', width: '49.5%' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-start' }}>
          <div><Image width={28} height={46} src={returnResourceIcon(file)} alt="file-icon" /></div>
          <div style={{ marginLeft: '5px', width: '100%' }}>
            <div style={{ fontSize: '11px' }} className={styles.single_line_block}>{file.name}</div>
            <div style={{ color: '#888888', fontSize: '9px' }}>{file.type.split("/")[1]}{file.size !== '' ? ` • ${formatBytes(file.size)}` : ''}</div>
          </div>
        </div>
      </div>
  )

  return (
      <div>
        {channel === 'output' && (!isAnyFileWithAgentId || files.length <= 0 ?
                <div className="vertical_container">
                  <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions" />
                  <span className={styles.feed_title} style={{ marginTop: '8px' }}>No Output files!</span>
                </div>
                :
                <div id="division_by_runs">
                  {filesByRun.map((filesRun, index) => (
                      <div key={index}>
                        <div className="horizontal_container justify_space_between cursor_pointer" style={{ padding: '8px 6px' }} onClick={() => setSelectedRun(filesRun.run === selectedRun ? null : filesRun.run)}>
                          <div className="horizontal_container">
                            <Image src={selectedRun === filesRun.run ? "/images/arrow_downward_dropdown.svg" : "/images/arrow_forward.svg"} alt="arrow" width={14} height={14} />
                            <span className="text_12 ml_8">{filesRun.run.name}</span>
                            <div className="resource_manager_tip ml_8"><Image src="/images/bolt.svg" alt="bolt" width={10} height={10} /> <span className="text_9">Run {index + 1}</span></div>
                          </div>
                          <Image src="/images/download.svg" alt="download_icon" width={16} height={16} onClick={() => downloadRunFiles(filesRun.run.id,filesRun.run.name)} />
                        </div>

                        {selectedRun === filesRun.run && (
                            <div className={styles.resources} style={{padding: '2px 8px'}}>
                              {/* eslint-disable-next-line react/jsx-key */}
                              {filesRun.files.map((file, index) => <File file={file} index={index} />)}
                            </div>
                        )}
                      </div>
                  ))}
                </div>
        )}

        {channel === 'input' &&
            <div className={styles.resources}>
              {/* eslint-disable-next-line react/jsx-key */}
              {files.map((file, index) => <File file={file} index={index} />)}
            </div>}
      </div>
  )
}