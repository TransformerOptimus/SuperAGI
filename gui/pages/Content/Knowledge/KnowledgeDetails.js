import React, {useEffect, useState} from 'react';
import styles1 from './Knowledge.module.css'
import {ToastContainer, toast} from "react-toastify";
import styles from "@/pages/Content/Toolkits/Tool.module.css";
import Image from "next/image";
import KnowledgeForm from "@/pages/Content/Knowledge/KnowledgeForm";
import {deleteCustomKnowledge, deleteMarketplaceKnowledge, getKnowledgeDetails} from "@/pages/api/DashboardService";
import {removeTab, returnToolkitIcon, setLocalStorageValue} from "@/utils/utils";
import {EventBus} from "@/utils/eventBus";
import Metrics from "@/pages/Content/Toolkits/Metrics";

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
  const [activeTab, setActiveTab] = useState('metrics');


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
      <div className="col-12 col-6-scrollable">
        <div className="horizontal_container align_start mb_20">
          <div className="vertical_containers text_align_left mr_10 w_97">
            <div className="text_17">{knowledgeName}</div>
            <div className="text_12" >
              {knowledgeDescription}
            </div>
          </div>
            <div className="w_3">
                <button className="secondary_button padding_8 h_31p"
                        onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
                    <Image width={14} height={14} src="/images/three_dots.svg" alt="run-icon"/>
                </button>
                {dropdown && <div onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
                    <ul className={`${"dropdown_container"} ${styles1.knowledge_options_dropdown}`}>
                        {installationType !== 'Marketplace' &&
                            // <li className="dropdown_item" onClick={viewKnowledge}>View in marketplace</li> :
                            <li className="dropdown_item" onClick={editKnowledge}>Edit details</li>}
                        <li className="dropdown_item" onClick={uninstallKnowledge}>Uninstall knowledge</li>
                    </ul>
                </div>}
            </div>
        </div>
        <div className="horizontal_container mb_10 border_bottom_grey pd_bottom_5">
          <div className={activeTab === 'metrics' ? 'tab_button_small_selected' : 'tab_button_small'}
               onClick={() => setActiveTab('metrics')}>
            <div className="text_12 color_white padding_8">Metrics</div>
          </div>
          <div className={activeTab === 'configuration' ? 'tab_button_small_selected' : 'tab_button_small'}
               onClick={() => setActiveTab('configuration')}>
            <div className="text_12 color_white padding_8">Configuration</div>
          </div>
        </div>
        {activeTab === 'metrics' && <div>
          <Metrics knowledgeName={knowledgeName} />
        </div>}
        { activeTab === "configuration" && <div className="row">
          <div className="col-3" />
          <div className="col-6">
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
            {installationType === 'Marketplace' && <div className={`${styles1.knowledge_wrapper} ${"col-6"} ${"w_100"}`}>
              <div className="w_50">
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
          <div className="col-3" />
        </div>}
      </div>
    </div>
    <ToastContainer/>
  </>);
}