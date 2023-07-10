import React, {useState, useEffect} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import agentStyles from "@/pages/Content/Agents/Agents.module.css";
import {returnDatabaseIcon, setLocalStorageArray} from "@/utils/utils";
import knowledgeStyles from "@/pages/Content/Knowledge/Knowledge.module.css";
import styles from "@/pages/Content/Marketplace/Market.module.css";
import Image from "next/image";

export default function DatabaseDetails({internalId, databaseDetails}) {
  const [dropdown,setDropdown] = useState(false);
  const [deleteModal,setDeleteModal] = useState(false);
  const [selectedDB, setSelectedDB] = useState('');
  const [databaseName, setDatabaseName] = useState('');
  const [collections, setCollections] = useState([]);
  const [initialCollections, setInitialCollections] = useState([]);
  const [hasChanges, setHasChanges] = useState(false);

  const [pineconeApiKey, setPineconeApiKey] = useState('');
  const [pineconeEnvironment, setPineconeEnvironment] = useState('');

  const [qdrantApiKey, setQdrantApiKey] = useState('');
  const [qdrantURL, setQdrantURL] = useState('');
  const [qdrantPort, setQdrantPort] = useState(8001);

  useEffect(() => {
    if(databaseDetails) {
      setSelectedDB(databaseDetails.database);
      setDatabaseName(databaseDetails.name);
      setCollections(databaseDetails.collections);
      setInitialCollections(databaseDetails.collections);
      setPineconeApiKey(databaseDetails.pineconeApiKey);
      setPineconeEnvironment(databaseDetails.pineconeEnvironment);
      setQdrantApiKey(databaseDetails.qdrantApiKey);
      setQdrantURL(databaseDetails.qdrantURL);
      setQdrantPort(databaseDetails.qdrantPort);
    }
  }, [internalId]);

  useEffect(() => {
    if (JSON.stringify(collections) !== JSON.stringify(initialCollections)) {
      setHasChanges(true);
    } else {
      setHasChanges(false);
    }
  }, [collections]);

  const preventDefault = (e) => {
    e.stopPropagation();
  };

  const addCollection = () => {
    setLocalStorageArray("db_details_collections_" + String(internalId), [...collections, 'collection name'], setCollections);
  };

  const handleCollectionChange = (index, newValue) => {
    const updatedCollections = [...collections];
    updatedCollections[index] = newValue;
    setLocalStorageArray("db_details_collections_" + String(internalId), updatedCollections, setCollections);
  };

  const handleCollectionDelete = (index) => {
    const updatedCollections = [...collections];
    updatedCollections.splice(index, 1);
    setLocalStorageArray("db_details_collections_" + String(internalId), updatedCollections, setCollections);
  };

  const deleteDatabase = () => {
    setDeleteModal(false);
  }

  const revertChanges = () => {
    setCollections(initialCollections);
    setHasChanges(false);
  };

  const updateChanges = () => {
    setInitialCollections(collections);
    setHasChanges(false);
  };

  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6" style={{overflowY:'scroll',height:'calc(100vh - 92px)',padding:'25px 20px'}}>
        <div className="title_wrapper">
          <div className={agentStyles.page_title}>{databaseName}</div>
          <div>
            <button className="secondary_button" style={{padding:'8px',height:'31px',marginTop:'-20px'}} onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
              <Image width={14} height={14} src="/images/three_dots.svg" alt="run-icon"/>
            </button>
            {dropdown && <div onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
              <ul className="dropdown_container">
                <li className="dropdown_item" onClick={() => {setDropdown(false);setDeleteModal(true)}}>Delete database</li>
              </ul>
            </div>}
          </div>
        </div>
        <div className="database_box">
          <div style={{display:'flex',justifyContent:'flex-start',order:'0',alignItems:'center'}}>
            <div style={{marginLeft:'15px'}}>
              <Image src={returnDatabaseIcon(selectedDB)} alt="database-icon" width={40} height={40}/>
            </div>
            <div style={{marginLeft:'15px',fontSize:'14px',marginTop:'23px'}} className={agentStyles.page_title}>{selectedDB}</div>
          </div>
        </div>
        <div style={{marginTop: '15px'}}>
          <div><label className={styles.form_label}>Collection i.e, Index</label></div>
          {collections.map((collection, index) => (<div key={index} style={{marginBottom:'10px',display:'flex',alignItems:'center',justifyContent:'space-between'}}>
            <div style={{flex:'1'}}>
              <input className="input_medium" type="text" value={collection}
                     onChange={(event) => handleCollectionChange(index, event.target.value)}/>
            </div>
            {collections.length > 1 && <div>
              <button className="secondary_button" style={{marginLeft: '4px', padding: '5px'}}
                      onClick={() => handleCollectionDelete(index)}>
                <Image width={20} height={21} src="/images/close.svg" alt="close-icon"/>
              </button>
            </div>}
          </div>))}
          <div><button className="secondary_button" onClick={addCollection}>+ Add</button></div>
        </div>
        {selectedDB === 'Pinecone' && <div>
          <div style={{marginTop:'15px'}}>
            <label className={knowledgeStyles.knowledge_label}>Pinecone API key</label>
            <div className={knowledgeStyles.knowledge_info}>{pineconeApiKey}</div>
          </div>
          <div style={{marginTop:'15px'}}>
            <label className={knowledgeStyles.knowledge_label}>Pinecone environment</label>
            <div className={knowledgeStyles.knowledge_info}>{pineconeEnvironment}</div>
          </div>
        </div>}
        {selectedDB === 'Qdrant' && <div>
          <div style={{marginTop:'15px'}}>
            <label className={knowledgeStyles.knowledge_label}>Qdrant API key</label>
            <div className={knowledgeStyles.knowledge_info}>{qdrantApiKey}</div>
          </div>
          <div style={{marginTop:'15px'}}>
            <label className={knowledgeStyles.knowledge_label}>Qdrant URL</label>
            <div className={knowledgeStyles.knowledge_info}>{qdrantURL}</div>
          </div>
          <div style={{marginTop:'15px'}}>
            <label className={knowledgeStyles.knowledge_label}>Port</label>
            <div className={knowledgeStyles.knowledge_info}>{qdrantPort}</div>
          </div>
        </div>}
        {hasChanges && <div style={{display: 'flex', justifyContent: 'flex-end',marginTop:'15px'}}>
          <button className="secondary_button" style={{marginRight: '10px'}} onClick={revertChanges}>
            Cancel
          </button>
          <button className="primary_button" onClick={updateChanges}>
            Update
          </button>
        </div>}
      </div>
      <div className="col-3"></div>
    </div>

    {deleteModal && (<div className="modal" onClick={() => setDeleteModal(false)}>
      <div className="modal-content" style={{width: '35%'}} onClick={preventDefault}>
        <div className={styles.detail_name}>Delete {databaseName}</div>
        <div>
          <label className={styles.form_label}>Are you sure you want to delete this database?</label>
        </div>
        <div style={{display: 'flex', justifyContent: 'flex-end',marginTop:'20px'}}>
          <button className="secondary_button" style={{marginRight: '10px'}} onClick={() => setDeleteModal(false)}>
            Cancel
          </button>
          <button className="primary_button" onClick={deleteDatabase}>
            Delete
          </button>
        </div>
      </div>
    </div>)}
    
    <ToastContainer/>
  </>)
}