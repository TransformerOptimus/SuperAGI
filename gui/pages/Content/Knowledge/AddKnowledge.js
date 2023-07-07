import React, {useState, useEffect, useRef} from 'react';
import styles1 from '@/pages/Content/Knowledge/Knowledge.module.css'
import {removeTab, setLocalStorageValue} from "@/utils/utils";
import {ToastContainer, toast} from "react-toastify";
import styles from "@/pages/Content/Agents/Agents.module.css";
import Image from "next/image";

export default function AddKnowledge({internalId}) {
  const [knowledgeName, setKnowledgeName] = useState('');
  const [knowledgeDescription, setKnowledgeDescription] = useState('');
  const [addClickable, setAddClickable] = useState(true);
  const collections = [
    {
      name: 'database name • Pinecone',
      indices: ['index name 1', 'index name 2', 'index name 3']
    },
    {
      name: 'database name • Qdrant',
      indices: ['index name 4', 'index name 5']
    }
  ];
  const [selectedIndex, setSelectedIndex] = useState(collections[0].indices[0]);
  const indexRef = useRef(null);
  const [indexDropdown, setIndexDropdown] = useState(false);

  const handleNameChange = (event) => {
    setLocalStorageValue("knowledge_name_" + String(internalId), event.target.value, setKnowledgeName);
  };

  const handleDescriptionChange = (event) => {
    setLocalStorageValue("knowledge_description_" + String(internalId), event.target.value, setKnowledgeDescription);
  };

  const handleAddKnowledge = () => {
    if (knowledgeName.replace(/\s/g, '') === '') {
      toast.error("Knowledge name can't be blank", {autoClose: 1800});
      return
    }

    if (knowledgeDescription.replace(/\s/g, '') === '') {
      toast.error("Knowledge description can't be blank", {autoClose: 1800});
      return
    }

    setAddClickable(false);
  }

  const handleIndexSelect = (index) => {
    setLocalStorageValue("knowledge_index_" + String(internalId), index, setSelectedIndex);
    setIndexDropdown(false);
  }

  useEffect(() => {
    const knowledge_name = localStorage.getItem("knowledge_name_" + String(internalId))
    if(knowledge_name) {
      setKnowledgeName(knowledge_name);
    }

    const knowledge_description = localStorage.getItem("knowledge_description_" + String(internalId))
    if(knowledge_description) {
      setKnowledgeDescription(knowledge_description);
    }

    const knowledge_index = localStorage.getItem("knowledge_index_" + String(internalId))
    if(knowledge_index) {
      setSelectedIndex(knowledge_index);
    }
  }, [internalId])

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

  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6" style={{overflowY:'scroll',height:'calc(100vh - 92px)',padding:'25px 20px'}}>
        <div>
          <div className={styles.page_title}>Add a new knowledge</div>
        </div>
        <div style={{marginTop:'10px'}}>
          <div className={styles1.knowledge_alert}>
            <div style={{marginRight:'5px',marginLeft:'-5px'}}>
              <Image width={20} height={20} src='/images/info.svg' alt="info-icon"/>
            </div>
            <div>
              Currently we support Open AI “text-knowledge-ada-002” model knowledge only. Please make sure you add the same.</div>
            </div>
        </div>
        <div style={{marginTop:'10px'}}>
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
            <label className={styles.form_label}>Collection i.e, Index</label><br/>
            <div className="dropdown_container_search" style={{width:'100%'}}>
              <div className="custom_select_container" onClick={() => setIndexDropdown(!indexDropdown)} style={{width:'100%'}}>
                {selectedIndex}<Image width={20} height={21} src={!indexDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'} alt="expand-icon"/>
              </div>
              <div>
                {indexDropdown && <div className="custom_select_options" ref={indexRef} style={{width:'100%'}}>
                  <div className={styles1.knowledge_label} style={{padding:'12px 14px',maxWidth:'100%'}}>Select an existing vector database collection/index to install the knowledge</div>
                  {collections.map((collection, index) => (<div key={index} className={styles1.knowledge_db} style={{maxWidth:'100%'}}>
                    <div className={styles1.knowledge_db_name}>{collection.name}</div>
                    {collection.indices.map((item, index) => (<div key={index} className="custom_select_option" onClick={() => handleIndexSelect(item)} style={{padding:'12px 14px',maxWidth:'100%'}}>
                      {item}
                    </div>))}
                  </div>))}
                </div>}
              </div>
            </div>
          </div>
          <div style={{marginTop: '15px', display: 'flex', justifyContent: 'flex-end'}}>
            <button style={{marginRight:'7px'}} className="secondary_button" onClick={() => removeTab(-6, "new knowledge", "Add_Knowledge")}>Cancel</button>
            <button disabled={!addClickable} className="primary_button" onClick={handleAddKnowledge}>Add knowledge</button>
          </div>
        </div>
      </div>
      <div className="col-3"></div>
    </div>
    <ToastContainer/>
  </>)
}