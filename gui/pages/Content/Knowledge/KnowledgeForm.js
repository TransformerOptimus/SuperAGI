import React, {useState, useEffect, useRef} from 'react';
import styles1 from '@/pages/Content/Knowledge/Knowledge.module.css'
import {removeTab, setLocalStorageValue, setLocalStorageArray, createInternalId} from "@/utils/utils";
import styles from "@/pages/Content/Agents/Agents.module.css";
import Image from "next/image";
import {ToastContainer, toast} from "react-toastify";
import {addUpdateKnowledge, getValidIndices} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";

export default function KnowledgeForm({
                                        internalId,
                                        knowledgeId,
                                        knowledgeName,
                                        setKnowledgeName,
                                        knowledgeDescription,
                                        setKnowledgeDescription,
                                        selectedIndex,
                                        setSelectedIndex,
                                        isEditing,
                                        setIsEditing,
                                        sendKnowledgeData
                                      }) {
  const [addClickable, setAddClickable] = useState(true);
  const indexRef = useRef(null);
  const [indexDropdown, setIndexDropdown] = useState(false);
  const [pinconeIndices, setPineconeIndices] = useState([]);
  const [qdrantIndices, setQdrantIndices] = useState([]);
  const [weaviateIndices, setWeaviateIndices] = useState([]);

  useEffect(() => {
    getValidIndices()
      .then((response) => {
        const data = response.data || [];
        if (data) {
          setPineconeIndices(data.pinecone || []);
          setQdrantIndices(data.qdrant || []);
          setWeaviateIndices(data.weaviate || []);
        }
      })
      .catch((error) => {
        console.error('Error fetching indices:', error);
      });
  }, []);

  useEffect(() => {
    function handleClickOutside(event) {
      if (indexRef.current && !indexRef.current.contains(event.target)) {
        setIndexDropdown(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleNameChange = (event) => {
    setLocalStorageValue("knowledge_name_" + String(internalId), event.target.value, setKnowledgeName);
  };

  const handleDescriptionChange = (event) => {
    setLocalStorageValue("knowledge_description_" + String(internalId), event.target.value, setKnowledgeDescription);
  };

  function validationCheck() {
    let isValid = true;

    if (knowledgeName.replace(/\s/g, '') === '') {
      toast.error("Knowledge name can't be blank", {autoClose: 1800});
      isValid = false;
    }

    if (!selectedIndex) {
      toast.error("Please select an index", {autoClose: 1800});
      isValid = false;
    }

    return isValid;
  }

  const handleAddKnowledge = () => {
    if (!validationCheck()) {
      return
    }

    const knowledgeData = {
      "id": 0,
      "name": knowledgeName,
      "description": knowledgeDescription,
      "index_id": selectedIndex.id
    }

    addUpdateKnowledge(knowledgeData)
      .then((response) => {
        toast.success("Knowledge added successfully", {autoClose: 1800});
        sendKnowledgeData({
          id: response.data.id,
          name: knowledgeName,
          contentType: "Knowledge",
          internalId: createInternalId()
        });
        EventBus.emit('reFetchKnowledge', {});
      })
      .catch((error) => {
        toast.error("Unable to add knowledge", {autoClose: 1800});
        console.error('Error deleting knowledge:', error);
      });

    setAddClickable(false);
  }

  const handleUpdateKnowledge = () => {
    if (!validationCheck()) {
      return
    }

    const knowledgeData = {
      "id": knowledgeId,
      "name": knowledgeName,
      "description": knowledgeDescription,
      "index_id": selectedIndex.id
    }

    addUpdateKnowledge(knowledgeData)
      .then((response) => {
        toast.success("Knowledge updated successfully", {autoClose: 1800});
        EventBus.emit('reFetchKnowledge', {});
      })
      .catch((error) => {
        toast.error("Unable to update knowledge", {autoClose: 1800});
        console.error('Error deleting knowledge:', error);
      });

    setIsEditing(false);
    setAddClickable(false);
  }

  const handleIndexSelect = (index) => {
    setLocalStorageArray("knowledge_index_" + String(internalId), index, setSelectedIndex);
    setIndexDropdown(false);
  }

  const checkIndexValidity = (validState) => {
    let errorMessage = "";
    let isValid = true;

    if (!validState) {
      isValid = false;
      errorMessage = "The configured index is either empty or has marketplace knowledge";
    }

    return [isValid, errorMessage];
  }

  return (<>
    <div>
      <div className={styles.page_title}>{isEditing ? 'Edit knowledge' : 'Add a new knowledge'}</div>
    </div>
    <div style={{marginTop: '10px'}}>
      <div className={styles1.knowledge_alert}>
        <div style={{marginRight: '5px', marginLeft: '-5px'}}>
          <Image width={20} height={20} src='/images/info.svg' alt="info-icon"/>
        </div>
        <div>
          Currently we support Open AI “text-embedding-ada-002” model knowledge only. Please make sure you add the same.
        </div>
      </div>
    </div>
    <div style={{marginTop: '10px'}}>
      <div>
        <label className={styles.form_label}>Knowledge name</label>
        <input className="input_medium" type="text" value={knowledgeName} onChange={handleNameChange}/>
      </div>
      <div style={{marginTop: '15px'}}>
        <label className={styles.form_label}>Description</label><br/>
        <label className={styles.form_label}>This description will be passed to the agent as knowledge context.</label>
        <textarea className="textarea_medium" rows={3} value={knowledgeDescription} onChange={handleDescriptionChange}/>
      </div>
      <div style={{marginTop: '15px'}}>
        <label className={styles.form_label}>Collection/Index</label><br/>
        <div className="dropdown_container_search" style={{width: '100%'}}>
          <div className="custom_select_container" onClick={() => setIndexDropdown(!indexDropdown)}
               style={{width: '100%', color: !selectedIndex ? '#888888' : ''}}>
            {selectedIndex?.name || 'Select Index'}<Image width={20} height={21}
                                                          src={!indexDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'}
                                                          alt="expand-icon"/>
          </div>
          <div>
            {indexDropdown && <div className="custom_select_options" ref={indexRef} style={{width: '100%'}}>
              <div className={styles1.knowledge_label} style={{padding: '12px 14px', maxWidth: '100%'}}>Select an
                existing vector database collection/index to install the knowledge
              </div>
              {pinconeIndices && pinconeIndices.length > 0 &&
                <div className={styles1.knowledge_db} style={{maxWidth: '100%'}}>
                  <div className={styles1.knowledge_db_name}>Pinecone</div>
                  {pinconeIndices.map((index) => (<div key={index.id} className="custom_select_option index_options"
                                                       onClick={() => handleIndexSelect(index)}>
                    <div style={!checkIndexValidity(index.is_valid_state)[0] ? {
                      color: '#888888',
                      textDecoration: 'line-through',
                      pointerEvents : 'none',
                    } : {}}>{index.name}</div>
                    {!checkIndexValidity(index.is_valid_state)[0] &&
                      <div>
                        <Image width={15} height={15} src="/images/info.svg" alt="info-icon"
                               title={checkIndexValidity(index.is_valid_state)[1]}/>
                      </div>}
                  </div>))}
                </div>}
              {qdrantIndices && qdrantIndices.length > 0 &&
                <div className={styles1.knowledge_db} style={{maxWidth: '100%'}}>
                  <div className={styles1.knowledge_db_name}>Qdrant</div>
                  {qdrantIndices.map((index) => (<div key={index.id} className="custom_select_option index_options"
                                                      onClick={() => handleIndexSelect(index)}>
                    <div style={!checkIndexValidity(index.is_valid_state)[0] ? {
                      color: '#888888',
                      textDecoration: 'line-through',
                      pointerEvents : 'none',
                    } : {}}>{index.name}</div>
                    {!checkIndexValidity(index.is_valid_state)[0] &&
                      <div>
                        <Image width={15} height={15} src="/images/info.svg" alt="info-icon"
                               title={checkIndexValidity(index.is_valid_state)[1]}/>
                      </div>}
                  </div>))}
                </div>}
              {weaviateIndices && weaviateIndices.length > 0 &&
                <div className={styles1.knowledge_db} style={{maxWidth: '100%'}}>
                  <div className={styles1.knowledge_db_name}>Weaviate</div>
                  {weaviateIndices.map((index) => (<div key={index.id} className="custom_select_option index_options"
                                                      onClick={() => handleIndexSelect(index)}>
                    <div style={!checkIndexValidity(index.is_valid_state)[0] ? {
                      color: '#888888',
                      textDecoration: 'line-through',
                      pointerEvents : 'none',
                    } : {}}>{index.name}</div>
                    {!checkIndexValidity(index.is_valid_state)[0] &&
                      <div>
                        <Image width={15} height={15} src="/images/info.svg" alt="info-icon"
                               title={checkIndexValidity(index.is_valid_state)[1]}/>
                      </div>}
                  </div>))}
                </div>}
            </div>}
          </div>
        </div>
      </div>
      {isEditing ? <div style={{marginTop: '15px', display: 'flex', justifyContent: 'flex-end'}}>
        <button style={{marginRight: '7px'}} className="secondary_button" onClick={() => setIsEditing(false)}>Cancel
        </button>
        <button disabled={!addClickable} className="primary_button" onClick={handleUpdateKnowledge}>Update Changes
        </button>
      </div> : <div style={{marginTop: '15px', display: 'flex', justifyContent: 'flex-end'}}>
        <button style={{marginRight: '7px'}} className="secondary_button"
                onClick={() => removeTab(-6, "new knowledge", "Add_Knowledge", internalId)}>Cancel
        </button>
        <button disabled={!addClickable} className="primary_button" onClick={handleAddKnowledge}>Add knowledge</button>
      </div>}
    </div>
    <ToastContainer/>
  </>)
}