import React, {useState, useEffect} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import agentStyles from "@/pages/Content/Agents/Agents.module.css";
import {
  createInternalId,
  removeTab,
  returnDatabaseIcon,
  setLocalStorageArray,
  setLocalStorageValue
} from "@/utils/utils";
import knowledgeStyles from "@/pages/Content/Knowledge/Knowledge.module.css";
import styles from "@/pages/Content/Marketplace/Market.module.css";
import Image from "next/image";
import styles1 from "@/pages/Content/Agents/Agents.module.css";
import {connectPinecone, connectQdrant, connectWeaviate, fetchVectorDBList} from "@/pages/api/DashboardService";

export default function AddDatabase({internalId, sendDatabaseDetailsData}) {
  const [activeView, setActiveView] = useState('select_database');
  const [vectorDatabases, setVectorDatabases] = useState(null);
  const [selectedDB, setSelectedDB] = useState('');
  const [databaseName, setDatabaseName] = useState('database name');
  const [collections, setCollections] = useState(['']);

  const [pineconeApiKey, setPineconeApiKey] = useState('');
  const [pineconeEnvironment, setPineconeEnvironment] = useState('');

  const [qdrantApiKey, setQdrantApiKey] = useState('');
  const [qdrantURL, setQdrantURL] = useState('');

  const [weaviateApiKey, setWeaviateApiKey] = useState('');
  const [weaviateURL, setWeaviateURL] = useState('');

  const [qdrantPort, setQdrantPort] = useState(8001);
  const [connectText, setConnectText] = useState('Connect');

  useEffect(() => {
    const active_view = localStorage.getItem('add_database_tab_' + String(internalId));
    if (active_view) {
      setActiveView(active_view);
    }

    const db_name = localStorage.getItem('db_name_' + String(internalId));
    if (db_name) {
      setDatabaseName(db_name);
    }

    const db_collections = localStorage.getItem('db_collections_' + String(internalId));
    if (db_collections) {
      setCollections(JSON.parse(db_collections));
    }

    const pinecone_api = localStorage.getItem('pincone_api_' + String(internalId));
    if (pinecone_api) {
      setPineconeApiKey(pinecone_api);
    }

    const pinecone_env = localStorage.getItem('pinecone_env_' + String(internalId));
    if (pinecone_env) {
      setPineconeEnvironment(pinecone_env);
    }

    const qdrant_api = localStorage.getItem('qdrant_api_' + String(internalId));
    if (qdrant_api) {
      setQdrantApiKey(qdrant_api);
    }

    const qdrant_url = localStorage.getItem('qdrant_url_' + String(internalId));
    if (qdrant_url) {
      setQdrantURL(qdrant_url);
    }

    const qdrant_port = localStorage.getItem('qdrant_port_' + String(internalId));
    if (qdrant_port) {
      setQdrantPort(Number(qdrant_port));
    }

    const weaviate_api = localStorage.getItem('weaviate_api_' + String(internalId));
    if (weaviate_api) {
      setWeaviateApiKey(weaviate_api);
    }

    const weaviate_url = localStorage.getItem('weaviate_url_' + String(internalId));
    if (weaviate_url) {
      setWeaviateURL(weaviate_url);
    }

  }, [internalId]);

  useEffect(() => {
    fetchVectorDBList()
      .then((response) => {
        const data = response.data || [];
        setVectorDatabases(data);
        const selected_db = localStorage.getItem('selected_db_' + String(internalId));
        setSelectedDB(selected_db ? selected_db : data[0].name || '');
      })
      .catch((error) => {
        console.error('Error fetching vector databases:', error);
      });
  }, [internalId]);

  const handleNameChange = (event) => {
    setLocalStorageValue('db_name_' + String(internalId), event.target.value, setDatabaseName);
  }

  const handlePineconeAPIKeyChange = (event) => {
    setLocalStorageValue('pincone_api_' + String(internalId), event.target.value, setPineconeApiKey);
  }

  const handlePineconeEnvironmentChange = (event) => {
    setLocalStorageValue('pinecone_env_' + String(internalId), event.target.value, setPineconeEnvironment);
  }

  const handleQdrantAPIKeyChange = (event) => {
    setLocalStorageValue('qdrant_api_' + String(internalId), event.target.value, setQdrantApiKey);
  }

  const handleQdrantURLChange = (event) => {
    setLocalStorageValue('qdrant_url_' + String(internalId), event.target.value, setQdrantURL);
  }

  const handleQdrantPortChange = (event) => {
    setLocalStorageValue('qdrant_port_' + String(internalId), event.target.value, setQdrantPort);
  }

  const handleWeaviateAPIKeyChange = (event) => {
    setLocalStorageValue('weaviate_api_' + String(internalId), event.target.value, setWeaviateApiKey);
  }

  const handleWeaviateURLChange = (event) => {
    setLocalStorageValue('weaviate_url_' + String(internalId), event.target.value, setWeaviateURL);
  }

  const addCollection = () => {
    setLocalStorageArray("db_collections_" + String(internalId), [...collections, 'collection name'], setCollections);
  };

  const handleCollectionChange = (index, newValue) => {
    const updatedCollections = [...collections];
    updatedCollections[index] = newValue;
    setLocalStorageArray("db_collections_" + String(internalId), updatedCollections, setCollections);
  };

  const handleCollectionDelete = (index) => {
    const updatedCollections = [...collections];
    updatedCollections.splice(index, 1);
    setLocalStorageArray("db_collections_" + String(internalId), updatedCollections, setCollections);
  };

  const connectResponse = (data) => {
    if (!data) {
      return;
    }
      toast.success("Database connected successfully", {autoClose: 1800});
      setConnectText("Connected");
      sendDatabaseDetailsData({id: data.id, name: data.name, contentType: "Database", internalId: createInternalId()});
  }

  const connectDatabase = () => {
    if (databaseName.replace(/\s/g, '') === '') {
      toast.error("Database name can't be blank", {autoClose: 1800});
      return;
    }

    if(collections.length === 1 && collections[0].length < 1){
      toast.error("Atleast add 1 Collection/Index", {autoClose: 1800});
      return;
    }

    if (selectedDB === 'Pinecone') {
      if (pineconeApiKey.replace(/\s/g, '') === '') {
        toast.error("Pinecone API key is empty", {autoClose: 1800});
        return;
      }

      if (pineconeEnvironment.replace(/\s/g, '') === '') {
        toast.error("Pinecone environment is empty", {autoClose: 1800});
        return;
      }

      setConnectText("Connecting...");

      const pineconeData = {
        "name": databaseName,
        "collections": collections,
        "api_key": pineconeApiKey,
        "environment": pineconeEnvironment,
      }

      connectPinecone(pineconeData)
        .then((response) => {
          connectResponse(response.data);
        })
        .catch((error) => {
          toast.error("Unable to connect database", {autoClose: 1800});
          console.error('Error fetching vector databases:', error);
          setConnectText("Connect");
        });
    }

    if (selectedDB === 'Qdrant') {
      if (qdrantApiKey.replace(/\s/g, '') === '') {
        toast.error("Qdrant API key is empty", {autoClose: 1800});
        return;
      }

      if (qdrantURL.replace(/\s/g, '') === '') {
        toast.error("Qdrant URL is empty", {autoClose: 1800});
        return;
      }

      if (String(qdrantPort).replace(/\s/g, '') === '') {
        toast.error("Qdrant port can't be blank", {autoClose: 1800});
        return;
      }

      setConnectText("Connecting...");

      const qdrantData = {
        "name": databaseName,
        "collections": collections,
        "api_key": qdrantApiKey,
        "url": qdrantURL,
        "port": qdrantPort
      }

      connectQdrant(qdrantData)
        .then((response) => {
          connectResponse(response.data);
        })
        .catch((error) => {
          toast.error("Unable to connect database", {autoClose: 1800});
          console.error('Error fetching vector databases:', error);
          setConnectText("Connect");
        });
    }

    if (selectedDB === 'Weaviate') {
      if (weaviateApiKey.replace(/\s/g, '') === '') {
        toast.error("Weaviate API key is empty", {autoClose: 1800});
        return;
      }

      if (weaviateURL.replace(/\s/g, '') === '') {
        toast.error("Weaviate URL is empty", {autoClose: 1800});
        return;
      }

      setConnectText("Connecting...");

      const weaviateData = {
        "name": databaseName,
        "collections": collections,
        "api_key": weaviateApiKey,
        "url": weaviateURL,
      }

      connectWeaviate(weaviateData)
        .then((response) => {
          connectResponse(response.data);
        })
        .catch((error) => {
          toast.error("Unable to connect database", {autoClose: 1800});
          console.error('Error fetching vector databases:', error);
          setConnectText("Connect");
        });
    }
  }

  const proceedAddDatabase = () => {
    if (selectedDB === null) {
      toast.error("Please select a database", {autoClose: 1800});
      return;
    }

    setLocalStorageValue('add_database_tab_' + String(internalId), 'form_database', setActiveView)
  }

  return (<>
    <div className="row">
      <div className="col-3"></div>
      {activeView === 'select_database' &&
        <div className="col-6" style={{overflowY: 'scroll', height: 'calc(100vh - 92px)', padding: '25px 20px'}}>
          <div className="title_wrapper">
            <div className={agentStyles.page_title}>Choose a vector database</div>
          </div>
          <div className={knowledgeStyles.database_wrapper}>
            {vectorDatabases?.map((item, index) => (
              <div key={index}
                   style={item.name === selectedDB ? {border: '1px solid #9B9AA1'} : {border: '1px solid rgb(39, 35, 53)'}}
                   className={knowledgeStyles.database_container}
                   onClick={() => setLocalStorageValue('selected_db_' + String(internalId), item.name, setSelectedDB)}>
                <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '20px'}}>
                  <Image width={40} height={40} src={returnDatabaseIcon(item.name)} alt=""/>
                </div>
                <div className={styles.text_block}
                     style={{width: '100%', marginBottom: '10px', textAlign: 'center'}}>{item.name}</div>
              </div>))}
          </div>
          <div style={{display: 'flex', justifyContent: 'flex-end', marginTop: '15px'}}>
            <button onClick={() => removeTab(-7, "new database", "Add_Database", internalId)}
                    className="secondary_button" style={{marginRight: '10px'}}>
              Cancel
            </button>
            <button className="primary_button" onClick={proceedAddDatabase}>
              Proceed
            </button>
          </div>
        </div>}
      {activeView === 'form_database' &&
        <div className="col-6" style={{overflowY: 'scroll', height: 'calc(100vh - 92px)', padding: '25px 20px'}}>
          <div className={styles.back_button} style={{margin: '8px 0', padding: '2px'}}
               onClick={() => setLocalStorageValue('add_database_tab_' + String(internalId), 'select_database', setActiveView)}>
            <Image src="/images/arrow_back.svg" alt="back_button" width={14} height={12}/>
            <span className={styles.back_button_text}>Back</span>
          </div>
          <div className="title_wrapper">
            <div className={agentStyles.page_title}>Connect new vector database</div>
          </div>
          <div className="database_box">
            <div style={{display: 'flex', justifyContent: 'flex-start', alignItems: 'center'}}>
              <div style={{marginLeft: '15px'}}>
                <Image src={returnDatabaseIcon(selectedDB)} alt="database-icon" width={40} height={40}/>
              </div>
              <div style={{marginLeft: '15px', fontSize: '14px', marginTop: '23px'}} className={agentStyles.page_title}>
                <p>{selectedDB}</p></div>
            </div>
          </div>
          <div style={{marginTop: '15px'}}>
            <label className={styles1.form_label}>Name</label>
            <input className="input_medium" type="text" value={databaseName} onChange={handleNameChange}/>
          </div>
          <div style={{marginTop: '15px'}}>
            <div>{selectedDB === 'Weaviate' ? <label className={styles.form_label}>Class/Collection/Index</label> : <label className={styles.form_label}>Collection/Index</label>}</div>
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
          {selectedDB === 'Pinecone' && <div>
            <div style={{marginTop: '15px'}}>
              <label className={styles1.form_label}>Pinecone API key</label>
              <input className="input_medium" type="password" value={pineconeApiKey}
                     onChange={handlePineconeAPIKeyChange}/>
            </div>
            <div style={{marginTop: '15px'}}>
              <label className={styles1.form_label}>Pinecone environment</label>
              <input className="input_medium" type="text" value={pineconeEnvironment}
                     onChange={handlePineconeEnvironmentChange}/>
            </div>
          </div>}
          {selectedDB === 'Qdrant' && <div>
            <div style={{marginTop: '15px'}}>
              <label className={styles1.form_label}>Qdrant API key</label>
              <input className="input_medium" type="password" value={qdrantApiKey} onChange={handleQdrantAPIKeyChange}/>
            </div>
            <div style={{marginTop: '15px'}}>
              <label className={styles1.form_label}>Qdrant URL</label>
              <input className="input_medium" type="text" value={qdrantURL} onChange={handleQdrantURLChange}/>
            </div>
            <div style={{marginTop: '15px'}}>
              <label className={styles1.form_label}>Port</label>
              <input className="input_medium" type="number" value={qdrantPort} onChange={handleQdrantPortChange}/>
            </div>
          </div>}
          {selectedDB === 'Weaviate' && <div>
            <div className="mt_15">
              <label className={styles1.form_label}>Weaviate API key</label>
              <input className="input_medium" type="password" value={weaviateApiKey} onChange={handleWeaviateAPIKeyChange}/>
            </div>
            <div className="mt_15">
              <label className={styles1.form_label}>Weaviate URL</label>
              <input className="input_medium" type="text" value={weaviateURL} onChange={handleWeaviateURLChange}/>
            </div>
          </div>}
          <div style={{display: 'flex', justifyContent: 'flex-end', marginTop: '15px'}}>
            <button onClick={() => removeTab(-7, "new database", "Add_Database", internalId)}
                    className="secondary_button" style={{marginRight: '10px'}}>
              Cancel
            </button>
            <button className="primary_button" onClick={connectDatabase}>
              {connectText}
            </button>
          </div>
        </div>}
      <div className="col-3"></div>
    </div>
    <ToastContainer/>
  </>)
}