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
    {name: 'database name 1', database: 'Pinecone', date_added: '1yr ago'},
    {name: 'database name 2', database: 'Qdrant', date_added: '1yr ago'},
    {name: 'database name 3', database: 'Pinecone', date_added: '1yr ago'},
    {name: 'database name 4', database: 'Qdrant', date_added: '1yr ago'}
  ]
  const [vectorDB, setVectorDB] = useState([]);
  const [isLoading, setIsLoading] = useState(true)
  const [loadingText, setLoadingText] = useState("Loading Databases");

  useEffect(() => {
    loadingTextEffect('Loading Databases', setLoadingText, 500);
    setTimeout(() => {
      loadDatabases();
    }, 1000);
  }, []);

  const loadDatabases = () => {
    setIsLoading(false);
    setVectorDB(databases);
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
                  <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:'10px'}}>
                    <div style={{display:'flex',order:'0'}}>
                      <div className={styles.text_block}>{item.name}</div>
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
    <ToastContainer/>
  </>)
}