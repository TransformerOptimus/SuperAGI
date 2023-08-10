import React, {useState, useEffect, useRef} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import agentStyles from "@/pages/Content/Agents/Agents.module.css";
import {
  createApiKey,
  deleteVectorDB, getApiKeys,
  getOrganisationConfig,
  updateOrganisationConfig,
  validateLLMApiKey
} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import {createInternalId, loadingTextEffect, preventDefault, removeTab, returnToolkitIcon} from "@/utils/utils";
import Image from "next/image";
import styles from "@/pages/Content/Marketplace/Market.module.css";
import styles1 from "@/pages/Content/Knowledge/Knowledge.module.css";

export default function ApiKeys() {
  const [apiKeys, setApiKeys] = useState([]);
  const [keyName, setKeyName] = useState('');
  const [apiKeyGenerated, setApiKeyGenerated] = useState('');
  const apiKeyRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true)
  const [createModal, setCreateModal] = useState(false);
  const [displayModal, setDisplayModal] = useState(false);
  const [loadingText, setLoadingText] = useState("Loading Api Keys");


  useEffect(() => {
    loadingTextEffect('Loading Api Keys', setLoadingText, 500);
    fetchApiKeys()
  }, []);

  const handleModelApiKey = (event) => {
    setKeyName(event.target.value);
  };

  const createApikey = () => {
    if(!keyName){
      toast.error("Enter key name", {autoClose: 1800});
      return;
    }
    createApiKey({name : keyName})
      .then((response) => {
        setApiKeyGenerated(response.data.api_key)
        toast.success("Api Key Generated", {autoClose: 1800});
        setCreateModal(false);
        setDisplayModal(true);
        fetchApiKeys();
      })
      .catch((error) => {
        console.error('Error creating api key', error);
      });
  }
  const handleCopyClick = async () => {
    if (apiKeyRef.current) {
      try {
        await navigator.clipboard.writeText(apiKeyRef.current.value);
        toast.success("Key Copied", {autoClose: 1800});
      } catch (err) {
        toast.error('Failed to Copy', {autoClose: 1800});
      }
    }
  };

  const fetchApiKeys = () => {
    getApiKeys()
      .then((response) => {
        setApiKeys(response.data)
        setIsLoading(false)
      })
      .catch((error) => {
        console.error('Error fetching Api Keys', error);
      });
  }

  return (<>
    <div className="row">
      <div className="col-2"></div>
      <div className="col-8" style={{overflowY: 'scroll', height: 'calc(100vh - 92px)', padding: '25px 20px'}}>
        {!isLoading ? <div>
          <div className="title_wrapper mb_15">
          <div className={styles.page_title}>Api Keys</div>
            {apiKeys && apiKeys.length > 0 && !isLoading &&
              <button className="primary_button" onClick={() => {setCreateModal(true); setKeyName('')}} style={{marginTop: '-10px', marginRight: '20px'}}>
                Create Key
              </button>}
          </div>
          <div>
          <label className={agentStyles.form_label}>Your secret API keys are important and should be kept safe. Do not share them with anyone or expose them in any case.</label>
          <label className={agentStyles.form_label}>To help keep your API keys safe, you can store them in a secure location, rotate them regularly, and use different API keys for different applications. By following these tips, you can help protect your account and your data.</label>

            {apiKeys.length < 1 && <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', marginTop: '40px', width: '100%'}}>
            <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions"/>
            <span className={styles.feed_title} style={{marginTop: '8px'}}>No API Keys created!</span>
            <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', marginTop: '10px'}}>
              <button className="primary_button" onClick={() => {setCreateModal(true); setKeyName('')}}>Create Key
              </button>
            </div>
          </div>}

            {apiKeys.length > 0 && <div className="scrollable_container" style={{background: '#272335', borderRadius: '8px',marginTop:'15px'}}>
              <table className="table_css margin_0 padding_0">
                <thead>
                <tr style={{borderTop: 'none'}}>
                  <th className="table_header w_56">Name</th>
                  <th className="table_header w_22">Key</th>
                  <th className="table_header w_22">Created Date</th>
                  <th className="table_header w_22"></th>
                </tr>
                </thead>
              </table>
              <div className="overflow_auto w_100">
                <table className="table_css margin_0">
                  <tbody>
                  {apiKeys.map((item, index) => (
                    <tr key={index}>
                      <td className="table_data w_56">{item.name}</td>
                      <td className="table_data w_22">{item.key.slice(0, 2) + "****" + item.key.slice(-4)}</td>
                      <td className="table_data w_22">23-JUN-2023</td>
                      <td className="table_data w_22"></td>
                    </tr>
                  ))}
                  </tbody>
                </table>
              </div>
            </div>}
        </div>
      </div> :  <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh'}}>
          <div className="signInInfo" style={{fontSize: '16px', fontFamily: 'Source Code Pro'}}>{loadingText}</div>
        </div>}
      </div>
      <div className="col-2"></div>
    </div>

    {createModal && (<div className="modal" onClick={() => setCreateModal(false)}>
      <div className="modal-content" style={{width: '35%'}} onClick={preventDefault}>
        <div className={styles.detail_name}>Create new Api Key</div>
        <div>
          <label className={styles.form_label}>Name</label>
          <input placeholder="Enter your Palm API key" className="input_medium" type="text" value={keyName} onChange={handleModelApiKey}/>
        </div>
        <div style={{display: 'flex', justifyContent: 'flex-end', marginTop: '20px'}}>
          <button className="secondary_button" style={{marginRight: '10px'}} onClick={() => setCreateModal(false)}>
            Cancel
          </button>
          <button className="primary_button" onClick={() => createApikey()}>
            Create Key
          </button>
        </div>
      </div>
    </div>)}

    {displayModal && apiKeyGenerated && (<div className="modal" onClick={() => setDisplayModal(false)}>
      <div className="modal-content" style={{width: '35%'}} onClick={preventDefault}>
        <div className={styles.detail_name}>{keyName} is created</div>
        <div>
          <div style={{marginTop: '15px',marginBottom: '25px'}}>
            <div className={styles1.knowledge_alert}>
              <div style={{marginRight: '5px', marginLeft: '-5px'}}>
                <Image width={20} height={20} src='/images/info.svg' alt="info-icon"/>
              </div>
              <div>
                Your secret API keys are sensitive pieces of information that should be kept confidential. Do not share them with anyone, and do not expose them in any way. If your secret API keys are compromised, someone could use them to access your API and make unauthorized changes to your data.</div>
            </div>
          </div>
          <div>
           <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
              <div style={{flex: '1'}}><input ref={apiKeyRef} className="input_medium" type="text" value={apiKeyGenerated} disabled />
              </div>
             <div>
                <button className="secondary_button" style={{marginLeft: '4px', padding: '5px'}} onClick={handleCopyClick}>
                  <Image width={20} height={21} src="/images/copy_icon.svg" alt="copy-icon"/>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div style={{display: 'flex', justifyContent: 'flex-end', marginTop: '20px'}}>
          <button className="primary_button" onClick={() => setDisplayModal(false)}>
            OK
          </button>
        </div>
      </div>
    </div>)}
    <ToastContainer/>
  </>)
}