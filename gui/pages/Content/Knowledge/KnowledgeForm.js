import React, {useState, useEffect, useRef} from 'react';
import styles1 from '@/pages/Content/Knowledge/Knowledge.module.css'
import {removeTab, setLocalStorageValue} from "@/utils/utils";
import styles from "@/pages/Content/Agents/Agents.module.css";
import Image from "next/image";
import {ToastContainer, toast} from "react-toastify";

export default function KnowledgeForm({internalId, knowledgeName, setKnowledgeName, knowledgeDescription, setKnowledgeDescription, selectedIndex, setSelectedIndex, collections, isEditing, setIsEditing}) {
  const [addClickable, setAddClickable] = useState(true);
  const indexRef = useRef(null);
  const [indexDropdown, setIndexDropdown] = useState(false);

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

    if (knowledgeDescription.replace(/\s/g, '') === '') {
      toast.error("Knowledge description can't be blank", {autoClose: 1800});
      isValid = false;
    }

    return isValid;
  }

  const handleAddKnowledge = () => {
    if (!validationCheck()) {
      return
    }

    setAddClickable(false);
  }

  const handleUpdateKnowledge = () => {
    if (!validationCheck()) {
      return
    }

    setIsEditing(false);
    setAddClickable(false);
  }

  const handleIndexSelect = (index) => {
    setLocalStorageValue("knowledge_index_" + String(internalId), index, setSelectedIndex);
    setIndexDropdown(false);
  }

  return (<>
    <div>
      <div className={styles.page_title}>{isEditing ? 'Edit knowledge' : 'Add a new knowledge'}</div>
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
      {isEditing ? <div style={{marginTop: '15px', display: 'flex', justifyContent: 'flex-end'}}>
        <button style={{marginRight:'7px'}} className="secondary_button" onClick={() => setIsEditing(false)}>Cancel</button>
        <button disabled={!addClickable} className="primary_button" onClick={handleUpdateKnowledge}>Update Changes</button>
      </div> : <div style={{marginTop: '15px', display: 'flex', justifyContent: 'flex-end'}}>
        <button style={{marginRight:'7px'}} className="secondary_button" onClick={() => removeTab(-6, "new knowledge", "Add_Knowledge")}>Cancel</button>
        <button disabled={!addClickable} className="primary_button" onClick={handleAddKnowledge}>Add knowledge</button>
      </div>}
    </div>
    <ToastContainer/>
  </>)
}