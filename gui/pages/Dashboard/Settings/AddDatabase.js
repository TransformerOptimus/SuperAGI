import React, {useState, useEffect} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import agentStyles from "@/pages/Content/Agents/Agents.module.css";
import {removeTab, setLocalStorageValue} from "@/utils/utils";
import knowledgeStyles from "@/pages/Content/Knowledge/Knowledge.module.css";
import styles from "@/pages/Content/Marketplace/Market.module.css";
import Image from "next/image";

export default function AddDatabase({internalId}) {
  const [activeView, setActiveView] = useState('select_database');
  const vectorDatabases = [
    { name: "Pinecone", icon: "/images/pinecone.svg" },
    { name: "Qdrant", icon: "/images/qdrant.svg" }
  ]
  const [selectedDB, setSelectedDB] = useState(vectorDatabases[0].name);

  useEffect(() => {
    const active_view = localStorage.getItem('add_database_tab_' +  String(internalId));
    if(active_view) {
      setActiveView(active_view);
    }
  }, []);

  return (<>
    <div className="row">
      <div className="col-3"></div>
      {activeView === 'select_database' && <div className="col-6" style={{overflowY:'scroll',height:'calc(100vh - 92px)',padding:'25px 20px'}}>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
          <div className={agentStyles.page_title}>Choose a vector database</div>
        </div>
        <div className={knowledgeStyles.database_wrapper}>
          {vectorDatabases.map((item, index) => (
            <div key={index} style={item.name === selectedDB ? {border:'1px solid #9B9AA1'} : {border:'1px solid rgb(39, 35, 53)'}} className={knowledgeStyles.database_container} onClick={() => setSelectedDB(item.name)}>
              <div style={{display:'flex',alignItems:'center',justifyContent:'center',margin:'20px'}}>
                <Image width={40} height={40} src={item.icon} alt=""/>
              </div>
              <div className={styles.text_block} style={{width:'100%',marginBottom:'10px',textAlign:'center'}}>{item.name}</div>
            </div>))}
        </div>
        <div style={{display: 'flex', justifyContent: 'flex-end',marginTop:'15px'}}>
          <button onClick={() => removeTab(-7, "new database", "Add_Database")} className="secondary_button" style={{marginRight: '10px'}}>
            Cancel
          </button>
          <button className="primary_button" onClick={() => setLocalStorageValue('add_database_tab_' + String(internalId), 'form_database', setActiveView)}>
            Proceed
          </button>
        </div>
      </div>}
      {activeView === 'form_database' && <div className="col-6" style={{overflowY:'scroll',height:'calc(100vh - 92px)',padding:'25px 20px'}}>

      </div>}
      <div className="col-3"></div>
    </div>
    <ToastContainer/>
  </>)
}