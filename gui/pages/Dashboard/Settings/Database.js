import React, {useState, useEffect} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import agentStyles from "@/pages/Content/Agents/Agents.module.css";
import {createInternalId, formatTimeDifference, loadingTextEffect, preventDefault} from "@/utils/utils";
import styles from "@/pages/Content/Marketplace/Market.module.css";
import knowledgeStyles from "@/pages/Content/Knowledge/Knowledge.module.css";
import Image from "next/image";
import {deleteVectorDB, getVectorDatabases} from "@/pages/api/DashboardService";

export default function Database({sendDatabaseData}) {
  const [vectorDB, setVectorDB] = useState([]);
  const [isLoading, setIsLoading] = useState(true)
  const [loadingText, setLoadingText] = useState("Loading Databases");
  const [dropdown, setDropdown] = useState([]);
  const [deleteModal, setDeleteModal] = useState(false);
  const [selectedDatabase, setSelectedDatabase] = useState(null);

  function fetchDatabases() {
    setIsLoading(true);

    getVectorDatabases()
      .then((response) => {
        const data = response.data || [];
        setVectorDB(data);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error('Error fetching vector databases:', error);
      });
  }

  useEffect(() => {
    loadingTextEffect('Loading Databases', setLoadingText, 500);
    fetchDatabases();
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

  const openDeleteModal = (e, index) => {
    e.stopPropagation();
    setDeleteModal(true);
    setSelectedDatabase(vectorDB[index]);
    setDropdownWithIndex(index, false);
  }

  const deleteDatabase = (databaseId) => {
    setDeleteModal(false);

    deleteVectorDB(databaseId)
      .then((response) => {
        toast.success("Database deleted successfully", {autoClose: 1800});
        fetchDatabases();
      })
      .catch((error) => {
        toast.error("Unable to delete database", {autoClose: 1800});
        console.error('Error fetching knowledge templates:', error);
      });
  }

  return (<>
    <div className="row">
      <div className="col-2"></div>
      <div className="col-8" style={{overflowY: 'scroll', height: 'calc(100vh - 92px)', padding: '25px 20px'}}>
        <div className="title_wrapper">
          <div className={agentStyles.page_title}>Vector Database</div>
          {vectorDB && vectorDB.length > 0 && !isLoading &&
            <button className="primary_button" onClick={() => sendDatabaseData({
              id: -7,
              name: "new database",
              contentType: "Add_Database",
              internalId: createInternalId()
            })} style={{marginTop: '-10px', marginRight: '20px'}}>
              Add
            </button>}
        </div>
        <div>
          <div className={styles.rowContainer} style={{maxHeight: '78vh', overflowY: 'auto'}}>
            {!isLoading ? <div>
              {vectorDB && vectorDB.length > 0 ? <div className={knowledgeStyles.database_wrapper}>
                {vectorDB.map((item, index) => (<div key={index} className={knowledgeStyles.database_container}
                                                     onClick={() => sendDatabaseData({
                                                       id: item.id,
                                                       name: item.name,
                                                       contentType: "Database",
                                                       internalId: createInternalId()
                                                     })}>
                  <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
                    <div style={{display: 'flex', order: '0'}}>
                      <div className={styles.text_block}>{item.name}</div>
                    </div>
                    <div style={{order: '1'}}>
                      <button className="three_dots_vertical" style={{padding: '8px', height: '31px'}}
                              onMouseEnter={() => setDropdownWithIndex(index, true)}
                              onMouseLeave={() => setDropdownWithIndex(index, false)}>
                        <Image width={14} height={14} src="/images/three_dots_vertical.svg" alt="run-icon"/>
                      </button>
                      {dropdown[index] && <div onMouseEnter={() => setDropdownWithIndex(index, true)}
                                               onMouseLeave={() => setDropdownWithIndex(index, false)}>
                        <ul className="dropdown_container" style={{marginLeft: '-15px'}}>
                          <li className="dropdown_item" onClick={(e) => openDeleteModal(e, index)}>Delete database</li>
                        </ul>
                      </div>}
                    </div>
                  </div>
                  <div style={{display: 'flex', alignItems: 'center', justifyContent: 'flex-start'}}>
                    <div style={{display: 'flex', alignItems: 'center'}}>
                      <div>
                        <Image width={12} height={12} src="/images/stack.svg" alt="database-icon"/>
                      </div>
                      <div className={styles.history_info}>
                        {item.db_type}
                      </div>
                    </div>
                    <div style={{display: 'flex', alignItems: 'center', marginLeft: '10px'}}>
                      <div>
                        <Image width={12} height={12} src="/images/schedule.svg" alt="schedule-icon"/>
                      </div>
                      <div className={styles.history_info}>
                        Added {formatTimeDifference(item.updated_at)}
                      </div>
                    </div>
                  </div>
                </div>))}</div> : <div style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                marginTop: '40px',
                width: '100%'
              }}>
                <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions"/>
                <span className={styles.feed_title} style={{marginTop: '8px'}}>No vector database added!</span>
                <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', marginTop: '10px'}}>
                  <button className="primary_button" onClick={() => sendDatabaseData({
                    id: -7,
                    name: "new database",
                    contentType: "Add_Database",
                    internalId: createInternalId()
                  })}>Add
                  </button>
                </div>
              </div>}
            </div> : <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh'}}>
              <div className="signInInfo" style={{fontSize: '16px', fontFamily: 'Source Code Pro'}}>{loadingText}</div>
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
          <label className={styles.form_label}>Deleting database will delete all the corresponding knowledge also. Do
            you want to delete database?</label>
        </div>
        <div style={{display: 'flex', justifyContent: 'flex-end', marginTop: '20px'}}>
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