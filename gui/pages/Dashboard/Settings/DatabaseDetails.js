import React, {useState, useEffect} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import agentStyles from "@/pages/Content/Agents/Agents.module.css";
import {removeTab, returnDatabaseIcon, setLocalStorageArray, preventDefault} from "@/utils/utils";
import knowledgeStyles from "@/pages/Content/Knowledge/Knowledge.module.css";
import styles from "@/pages/Content/Marketplace/Market.module.css";
import Image from "next/image";
import {deleteVectorDB, getVectorDBDetails, updateVectorDB} from "@/pages/api/DashboardService";

export default function DatabaseDetails({internalId, databaseId}) {
  const [dropdown, setDropdown] = useState(false);
  const [deleteModal, setDeleteModal] = useState(false);
  const [collections, setCollections] = useState([]);
  const [initialCollections, setInitialCollections] = useState([]);
  const [hasChanges, setHasChanges] = useState(false);
  const [databaseDetails, setDatabaseDetails] = useState([]);

  useEffect(() => {
    if (databaseId) {
      getVectorDBDetails(databaseId)
        .then((response) => {
          const data = response.data || [];
          setDatabaseDetails(data);
          if (data) {
            const localIndices = localStorage.getItem("db_details_collections_" + String(internalId));
            const indices = data.indices || [];
            setCollections(localIndices ? JSON.parse(localIndices) : indices);
            setInitialCollections(indices);
          }
        })
        .catch((error) => {
          console.error('Error deleting database:', error);
        });
    }
  }, [internalId]);

  useEffect(() => {
    if (JSON.stringify(collections) !== JSON.stringify(initialCollections)) {
      setHasChanges(true);
    } else {
      setHasChanges(false);
    }
  }, [collections]);

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

    deleteVectorDB(databaseId)
      .then((response) => {
        toast.success("Database deleted successfully", {autoClose: 1800});
        removeTab(databaseId, databaseDetails?.name, "Database", internalId);
      })
      .catch((error) => {
        toast.error("Unable to delete database", {autoClose: 1800});
        console.error('Error deleting database:', error);
      });
  }

  const revertChanges = () => {
    setCollections(initialCollections);
    setHasChanges(false);
  };

  const updateChanges = () => {
    updateVectorDB(databaseId, collections)
      .then((response) => {
          toast.success("Database updated successfully", {autoClose: 1800});
          setInitialCollections(collections);
          setHasChanges(false);
      })
      .catch((error) => {
        toast.error("Unable to update database", {autoClose: 1800});
        console.error('Error fetching knowledge templates:', error);
      });
  };

  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6" style={{overflowY: 'scroll', height: 'calc(100vh - 92px)', padding: '25px 20px'}}>
        <div className="title_wrapper">
          <div className={agentStyles.page_title}>{databaseDetails?.name}</div>
          <div>
            <button className="secondary_button" style={{padding: '8px', height: '31px', marginTop: '-20px'}}
                    onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
              <Image width={14} height={14} src="/images/three_dots.svg" alt="run-icon"/>
            </button>
            {dropdown && <div onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
              <ul className="dropdown_container">
                <li className="dropdown_item" onClick={() => {
                  setDropdown(false);
                  setDeleteModal(true)
                }}>Delete database
                </li>
              </ul>
            </div>}
          </div>
        </div>
        <div className="database_box">
          <div style={{display: 'flex', justifyContent: 'flex-start', order: '0', alignItems: 'center'}}>
            <div style={{marginLeft: '15px'}}>
              <Image src={returnDatabaseIcon(databaseDetails?.db_type)} alt="database-icon" width={40} height={40}/>
            </div>
            <div style={{marginLeft: '15px', fontSize: '14px', marginTop: '23px'}}
                 className={agentStyles.page_title}>{databaseDetails?.db_type}</div>
          </div>
        </div>
        <div style={{marginTop: '15px'}}>
          <div><label className={styles.form_label}>Collection/Index</label></div>
          {collections.map((collection, index) => (<div key={index} style={{
            marginBottom: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{flex: '1'}}>
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
          <div>
            <button className="secondary_button" onClick={addCollection}>+ Add</button>
          </div>
        </div>
        {databaseDetails?.db_type === 'Pinecone' && <div>
          <div style={{marginTop: '15px'}}>
            <label className={knowledgeStyles.knowledge_label}>Pinecone API key</label>
            <div className={knowledgeStyles.knowledge_info}>{databaseDetails?.api_key}</div>
          </div>
          <div style={{marginTop: '15px'}}>
            <label className={knowledgeStyles.knowledge_label}>Pinecone environment</label>
            <div className={knowledgeStyles.knowledge_info}>{databaseDetails?.environment}</div>
          </div>
        </div>}
        {databaseDetails?.db_type === 'Qdrant' && <div>
          <div style={{marginTop: '15px'}}>
            <label className={knowledgeStyles.knowledge_label}>Qdrant API key</label>
            <div className={knowledgeStyles.knowledge_info}>{databaseDetails?.api_key}</div>
          </div>
          <div style={{marginTop: '15px'}}>
            <label className={knowledgeStyles.knowledge_label}>Qdrant URL</label>
            <div className={knowledgeStyles.knowledge_info}>{databaseDetails?.url}</div>
          </div>
          <div style={{marginTop: '15px'}}>
            <label className={knowledgeStyles.knowledge_label}>Port</label>
            <div className={knowledgeStyles.knowledge_info}>{databaseDetails?.port}</div>
          </div>
        </div>}
        {hasChanges && <div style={{display: 'flex', justifyContent: 'flex-end', marginTop: '15px'}}>
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
        <div className={styles.detail_name}>Delete {databaseDetails?.name}</div>
        <div>
          <label className={styles.form_label}>Deleting database will delete all the corresponding knowledge also. Do
            you want to delete database?</label>
        </div>
        <div style={{display: 'flex', justifyContent: 'flex-end', marginTop: '20px'}}>
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