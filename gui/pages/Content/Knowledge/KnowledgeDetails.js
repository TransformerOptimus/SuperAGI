import React, {useEffect, useState} from 'react';
import styles1 from './Knowledge.module.css'
import {ToastContainer, toast} from "react-toastify";
import styles from "@/pages/Content/Toolkits/Tool.module.css";
import Image from "next/image";
import KnowledgeForm from "@/pages/Content/Knowledge/KnowledgeForm";
import {deleteCustomKnowledge, deleteMarketplaceKnowledge, getKnowledgeDetails} from "@/pages/api/DashboardService";
import {removeTab} from "@/utils/utils";
import {EventBus} from "@/utils/eventBus";

export default function KnowledgeDetails({internalId, knowledgeId}) {
  const [showDescription, setShowDescription] = useState(false);
  const [dropdown, setDropdown] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [knowledgeName, setKnowledgeName] = useState('');
  const [knowledgeDescription, setKnowledgeDescription] = useState('');
  const [installationType, setInstallationType] = useState('');
  const [model, setModel] = useState('');
  const [tokenizer, setTokenizer] = useState('');
  const [chunkSize, setChunkSize] = useState('');
  const [vectorDatabase, setVectorDatabase] = useState('');
  const [knowledgeDatatype, setKnowledgeDatatype] = useState('');
  const [textSplitters, setTextSplitters] = useState('');
  const [chunkOverlap, setChunkOverlap] = useState('');
  const [dimension, setDimension] = useState('');
  const [vectorDBIndex, setVectorDBIndex] = useState('');

  const uninstallKnowledge = () => {
    setDropdown(false);

    if (installationType === 'Marketplace') {
      deleteMarketplaceKnowledge(knowledgeName)
        .then((response) => {
          console.log(response)
          toast.success("Knowledge uninstalled successfully", {autoClose: 1800});
            removeTab(knowledgeId, knowledgeName, "Knowledge", internalId);
            EventBus.emit('reFetchKnowledge', {});
        })
        .catch((error) => {
          toast.error("Unable to uninstall knowledge", {autoClose: 1800});
          console.error('Error uninstalling knowledge:', error);
        });
    } else {
      deleteCustomKnowledge(knowledgeId)
        .then((response) => {
            toast.success("Knowledge uninstalled successfully", {autoClose: 1800});
          removeTab(knowledgeId, knowledgeName, "Knowledge", internalId);
          EventBus.emit('reFetchKnowledge', {});
        })
        .catch((error) => {
          toast.error("Unable to uninstall knowledge", {autoClose: 1800});
          console.error('Error uninstalling knowledge:', error);
        });
    }
  }

  const viewKnowledge = () => {
    setDropdown(false);
  }

  const editKnowledge = () => {
    setIsEditing(true);
    setDropdown(false);
  }

  useEffect(() => {
    if (knowledgeId) {
      getKnowledgeDetails(knowledgeId)
        .then((response) => {
          const data = response.data || [];
          setKnowledgeName(data.name);
          setKnowledgeDescription(data.description);
          setInstallationType(data.installation_type);
          setModel(data.model);
          setTokenizer(data.tokenizer);
          setChunkSize(data.chunk_size);
          setVectorDatabase(data.vector_database);
          setKnowledgeDatatype(data.data_type);
          setTextSplitters(data.text_splitter);
          setChunkOverlap(data.chunk_overlap);
          setDimension(data.dimensions);
          setVectorDBIndex(data.vector_database_index);
        })
        .catch((error) => {
          console.error('Error fetching knowledge details:', error);
        });
    }
  }, [internalId]);

  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6" style={{overflowY: 'scroll', height: 'calc(100vh - 92px)', padding: '25px 20px'}}>
        {isEditing ?
          <KnowledgeForm internalId={internalId}
                         knowledgeId={knowledgeId}
                         knowledgeName={knowledgeName}
                         setKnowledgeName={setKnowledgeName}
                         knowledgeDescription={knowledgeDescription}
                         setKnowledgeDescription={setKnowledgeDescription}
                         selectedIndex={vectorDBIndex}
                         setSelectedIndex={setVectorDBIndex}
                         isEditing={true}
                         setIsEditing={setIsEditing}
                         sendKnowledgeData={null}
          /> :
          <div>
            <div className={styles.tools_container}>
              <div className={styles1.knowledge_wrapper} style={{width: '95%'}}>
                <div style={{display: 'flex', alignItems: 'center', width: '100%'}}>
                  <div style={{textAlign: 'left', paddingRight: '10px', width: '95%'}}>
                    <div style={{fontSize: '17px', marginTop: '-3px'}}>{knowledgeName}</div>
                    <div className={styles.toolkit_description}
                         style={!showDescription ? {overflow: 'hidden'} : {display: 'block'}}>
                      {`${showDescription ? knowledgeDescription : knowledgeDescription.slice(0, 70)}`}
                      {knowledgeDescription.length > 70 &&
                        <span className={styles.show_more_button} onClick={() => setShowDescription(!showDescription)}>
                        {showDescription ? '...less' : '...more'}
                    </span>}
                    </div>
                  </div>
                </div>
                <div style={{width: '5%'}}>
                  <button className="secondary_button" style={{padding: '8px', height: '31px'}}
                          onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
                    <Image width={14} height={14} src="/images/three_dots.svg" alt="run-icon"/>
                  </button>
                  {dropdown && <div onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
                    <ul className="dropdown_container" style={{marginTop: '0', marginLeft: '-10px', width: '165px'}}>
                      {installationType !== 'Marketplace' &&
                        // <li className="dropdown_item" onClick={viewKnowledge}>View in marketplace</li> :
                        <li className="dropdown_item" onClick={editKnowledge}>Edit details</li>}
                      <li className="dropdown_item" onClick={uninstallKnowledge}>Uninstall knowledge</li>
                    </ul>
                  </div>}
                </div>
              </div>
            </div>
            {installationType === 'Marketplace' && <div className={styles1.knowledge_wrapper} style={{width: '100%'}}>
              <div style={{width: '50%'}}>
                <div className={styles1.knowledge_info_box}>
                  <label className={styles1.knowledge_label}>Installation Type</label>
                  <div className={styles1.knowledge_info}>{installationType}</div>
                </div>
                <div className={styles1.knowledge_info_box}>
                  <label className={styles1.knowledge_label}>Model</label>
                  <div className={styles1.knowledge_info}>{model}</div>
                </div>
                <div className={styles1.knowledge_info_box}>
                  <label className={styles1.knowledge_label}>Tokenizer</label>
                  <div className={styles1.knowledge_info}>{tokenizer}</div>
                </div>
                <div className={styles1.knowledge_info_box}>
                  <label className={styles1.knowledge_label}>Chunk Size</label>
                  <div className={styles1.knowledge_info}>{chunkSize}</div>
                </div>
                <div className={styles1.knowledge_info_box}>
                  <label className={styles1.knowledge_label}>Vector Database</label>
                  <div className={styles1.knowledge_info}>{vectorDatabase}</div>
                </div>
              </div>
              <div style={{width: '50%'}}>
                <div className={styles1.knowledge_info_box}>
                  <label className={styles1.knowledge_label}>Knowledge datatype</label>
                  <div className={styles1.knowledge_info}>{knowledgeDatatype}</div>
                </div>
                <div className={styles1.knowledge_info_box}>
                  <label className={styles1.knowledge_label}>Text splitters</label>
                  <div className={styles1.knowledge_info}>{textSplitters}</div>
                </div>
                <div className={styles1.knowledge_info_box}>
                  <label className={styles1.knowledge_label}>Chunk overlap</label>
                  <div className={styles1.knowledge_info}>{chunkOverlap}</div>
                </div>
                <div className={styles1.knowledge_info_box}>
                  <label className={styles1.knowledge_label}>Dimension</label>
                  <div className={styles1.knowledge_info}>{dimension}</div>
                </div>
                <div className={styles1.knowledge_info_box}>
                  <label className={styles1.knowledge_label}>Vector database index</label>
                  <div className={styles1.knowledge_info}>{vectorDBIndex?.name || ''}</div>
                </div>
              </div>
            </div>}
            {installationType === 'Custom' && <div className={styles1.knowledge_wrapper}>
              <div style={{width: '50%'}}>
                <div className={styles1.knowledge_info_box}>
                  <label className={styles1.knowledge_label}>Installation Type</label>
                  <div className={styles1.knowledge_info}>{installationType}</div>
                </div>
                <div className={styles1.knowledge_info_box}>
                  <label className={styles1.knowledge_label}>Vector database index</label>
                  <div className={styles1.knowledge_info}>{vectorDBIndex?.name || ''}</div>
                </div>
              </div>
              <div style={{width: '50%'}}>
                <div className={styles1.knowledge_info_box}>
                  <label className={styles1.knowledge_label}>Vector Database</label>
                  <div className={styles1.knowledge_info}>{vectorDatabase}</div>
                </div>
              </div>
            </div>}
          </div>}
      </div>
      <div className="col-3"></div>
    </div>
    <ToastContainer/>
  </>);
}