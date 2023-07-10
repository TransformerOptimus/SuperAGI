import React, {useState, useEffect} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import agentStyles from "@/pages/Content/Agents/Agents.module.css";
import {createInternalId, loadingTextEffect} from "@/utils/utils";
import styles from "@/pages/Content/Marketplace/Market.module.css";
import knowledgeStyles from "@/pages/Content/Knowledge/Knowledge.module.css";
import Image from "next/image";

export default function Database({organisationId, sendDatabaseData}) {
  const databases = [
    {id: 0, name: 'database name 1', database: 'Pinecone', date_added: '1yr ago'},
    {id: 2, name: 'database name 2', database: 'Qdrant', date_added: '1yr ago'},
    {id: 3, name: 'database name 3', database: 'Pinecone', date_added: '1yr ago'},
    {id: 4, name: 'database name 4', database: 'Qdrant', date_added: '1yr ago'}
  ]
  const [vectorDB, setVectorDB] = useState([]);
  const [isLoading, setIsLoading] = useState(true)
  const [loadingText, setLoadingText] = useState("Loading Databases");
  const [dropdown, setDropdown] = useState([]);
  const [deleteModal,setDeleteModal] = useState(false);
  const [selectedDatabase, setSelectedDatabase] = useState(null);

  const preventDefault = (e) => {
    e.stopPropagation();
  };

  useEffect(() => {
    loadingTextEffect('Loading Databases', setLoadingText, 500);
    setTimeout(() => {
      loadDatabases();
    }, 1000);
  }, []);

  useEffect(() => {
    setDropdown(Array(vectorDB.length).fill(false));
  }, [vectorDB]);

  const setDropdownWithIndex = (index, state) => {
    setDropdown((prevDropdown) => {
      const newDropdown = [...prevDropdown];
      newDropdown[index] = state;
      return newDropdown;
    });
  }

  const loadDatabases = () => {
    setIsLoading(false);
    setVectorDB(databases);
  }

  const openDeleteModal = (index) => {
    setDeleteModal(true);
    setDropdownWithIndex(index, false);
    setSelectedDatabase(vectorDB[index]);
  }

  const deleteDatabase = (databaseId) => {
    setDeleteModal(false);
  }

  return (<>
    <div className="row">
      <div className="col-2"></div>
      <div className="col-8" style={{overflowY:'scroll',height:'calc(100vh - 92px)',padding:'25px 20px'}}>
        <div className="title_wrapper">
          <div className={agentStyles.page_title}>Vector Database</div>
          {vectorDB && vectorDB.length > 0 && !isLoading &&
            <button className="primary_button" onClick={() => sendDatabaseData({ id: -7, name: "new database", contentType: "Add_Database", internalId: createInternalId() })} style={{marginTop:'-10px',marginRight:'20px'}}>
              Add
            </button>}
        </div>
        <div>
          <div className={styles.rowContainer} style={{maxHeight: '78vh',overflowY: 'auto'}}>
            {!isLoading ? <div>
              {vectorDB && vectorDB.length > 0 ? <div className={knowledgeStyles.database_wrapper}>
                {vectorDB.map((item, index) => (<div key={index} className={knowledgeStyles.database_container}>
                  <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
                    <div style={{display:'flex',order:'0'}}>
                      <div className={styles.text_block}>{item.name}</div>
                    </div>
                    <div style={{order:'1'}}>
                      <button className="three_dots_vertical" style={{padding:'8px',height:'31px'}} onMouseEnter={() => setDropdownWithIndex(index,true)} onMouseLeave={() => setDropdownWithIndex(index, false)}>
                        <Image width={14} height={14} src="/images/three_dots_vertical.svg" alt="run-icon"/>
                      </button>
                      {dropdown[index] && <div onMouseEnter={() => setDropdownWithIndex(index, true)} onMouseLeave={() => setDropdownWithIndex(index, false)}>
                        <ul className="dropdown_container" style={{marginLeft:'-15px'}}>
                          <li className="dropdown_item" onClick={() => openDeleteModal(index)}>Delete database</li>
                        </ul>
                      </div>}
                    </div>
                  </div>
                  <div style={{display:'flex',alignItems:'center',justifyContent:'flex-start'}}>
                    <div style={{display:'flex',alignItems:'center'}}>
                      <div>
                        <Image width={12} height={12} src="/images/stack.svg" alt="database-icon"/>
                      </div>
                      <div className={styles.history_info}>
                        {item.database}
                      </div>
                    </div>
                    <div style={{display:'flex',alignItems:'center',marginLeft:'10px'}}>
                      <div>
                        <Image width={12} height={12} src="/images/schedule.svg" alt="schedule-icon"/>
                      </div>
                      <div className={styles.history_info}>
                        Added {item.date_added}
                      </div>
                    </div>
                  </div>
                </div>))}</div> : <div style={{display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',marginTop:'40px',width:'100%'}}>
                <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions" />
                <span className={styles.feed_title} style={{marginTop: '8px'}}>No vector database added!</span>
                <div style={{display:'flex',justifyContent:'center',alignItems:'center',marginTop:'10px'}}>
                  <button className="primary_button" onClick={() => sendDatabaseData({ id: -7, name: "new database", contentType: "Add_Database", internalId: createInternalId() })}>Add</button>
                </div>
              </div>}
            </div> : <div style={{display:'flex',justifyContent:'center',alignItems:'center',height:'50vh'}}>
              <div className="signInInfo" style={{fontSize:'16px',fontFamily:'Source Code Pro'}}>{loadingText}</div>
            </div>}
          </div>
        </div>
      </div>
      <div className="col-2"></div>
    </div>

    {deleteModal && (<div className="modal" onClick={() => setDeleteModal(false)}>
      <div className="modal-content" style={{width: '35%'}} onClick={preventDefault}>
        <div className={styles.detail_name}>Delete {selectedDatabase.name}</div>
        <div>
          <label className={styles.form_label}>Are you sure you want to delete this database?</label>
        </div>
        <div style={{display: 'flex', justifyContent: 'flex-end',marginTop:'20px'}}>
          <button className="secondary_button" style={{marginRight: '10px'}} onClick={() => setDeleteModal(false)}>
            Cancel
          </button>
          <button className="primary_button" onClick={() => deleteDatabase(selectedDatabase.id)}>
            Delete
          </button>
        </div>
      </div>
    </div>)}
    <ToastContainer/>
  </>)
}