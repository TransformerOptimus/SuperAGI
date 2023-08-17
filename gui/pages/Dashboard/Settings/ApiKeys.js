import React, {useState, useEffect, useRef} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import agentStyles from "@/pages/Content/Agents/Agents.module.css";
import {
  createApiKey, deleteApiKey,
  editApiKey, getApiKeys,
} from "@/pages/api/DashboardService";
import {EventBus} from "@/utils/eventBus";
import {createInternalId, loadingTextEffect, preventDefault, removeTab, returnToolkitIcon} from "@/utils/utils";
import Image from "next/image";
import styles from "@/pages/Content/Marketplace/Market.module.css";
import styles1 from "@/pages/Content/Knowledge/Knowledge.module.css";

export default function ApiKeys() {
  const [apiKeys, setApiKeys] = useState([]);
  const [keyName, setKeyName] = useState('');
  const [editKey, setEditKey] = useState('');
  const apiKeyRef = useRef(null);
  const editKeyRef = useRef(null);
  const [editKeyId, setEditKeyId] = useState(-1);
  const [deleteKey, setDeleteKey] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [activeDropdown, setActiveDropdown] = useState(null);
  const [editModal, setEditModal] = useState(false);
  const [deleteKeyId, setDeleteKeyId] = useState(-1);
  const [deleteModal, setDeleteModal] = useState(false);
  const [createModal, setCreateModal] = useState(false);
  const [displayModal, setDisplayModal] = useState(false);
  const [apiKeyGenerated, setApiKeyGenerated] = useState('');
  const [loadingText, setLoadingText] = useState("Loading Api Keys");



  useEffect(() => {
    loadingTextEffect('Loading Api Keys', setLoadingText, 500);
    fetchApiKeys()
  }, []);


  const handleModelApiKey = (event) => {
    setKeyName(event.target.value);
  };

  const handleEditApiKey = (event) => {
    setEditKey(event.target.value);
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
        const formattedData = response.data.map(item => {
          return {
            ...item,
            created_at: `${new Date(item.created_at).getDate()}-${["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"][new Date(item.created_at).getMonth()]}-${new Date(item.created_at).getFullYear()}`
          };
        });
        setApiKeys(formattedData)
        setIsLoading(false)
      })
      .catch((error) => {
        console.error('Error fetching Api Keys', error);
      });
  }

  const handleEditClick = () => {
    if(editKeyRef.current.value.length <1){
      toast.error("Enter valid key name", {autoClose: 1800});
      return;
    }
    editApiKey({id: editKeyId,name : editKey})
      .then((response) => {
        toast.success("Api Key Edited", {autoClose: 1800});
        fetchApiKeys();
        setEditModal(false);
        setEditKey('')
        setEditKeyId(-1)
      })
      .catch((error) => {
        console.error('Error editing api key', error);
      });
  }

  const handleDeleteClick = () => {
    deleteApiKey(deleteKeyId)
      .then((response) => {
        toast.success("Api Key Deleted", {autoClose: 1800});
        fetchApiKeys();
        setDeleteModal(false);
        setDeleteKeyId(-1)
        setDeleteKey('')
      })
      .catch((error) => {
        toast.error("Error deleting api key", {autoClose: 1800});
        console.error('Error deleting api key', error);
      });
  }

  return (<>
    <div className="row">
      <div className="col-2"></div>
      <div className="col-8 col-6-scrollable">
        {!isLoading ? <div>
          <div className="title_wrapper mb_15">
          <div className={styles.page_title}>API Keys</div>
            {apiKeys && apiKeys.length > 0 && !isLoading &&
              <button className={`${'primary_button mr_20'} ${agentStyles.button_margin}`} onClick={() => {setCreateModal(true); setKeyName('')}}>
                Create Key
              </button>}
          </div>
          <div>
          <label className={agentStyles.form_label}>Your secret API keys are important and should be kept safe. Do not share them with anyone or expose them in any case.</label>
          <label className={agentStyles.form_label}>To help keep your API keys safe, you can store them in a secure location, rotate them regularly, and use different API keys for different applications. By following these tips, you can help protect your account and your data.</label>

            {apiKeys.length < 1 && <div className={agentStyles.table_contents}>
            <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions"/>
            <span className={`${styles.feed_title} ${'mt_8'}`}>No API Keys created!</span>
            <div className={agentStyles.create_settings_button}>
              <button className="primary_button" onClick={() => {setCreateModal(true); setKeyName('')}}>Create Key
              </button>
            </div>
          </div>}

            {apiKeys.length > 0 && <div className="scrollable_container table_container">
              <table className="table_css margin_0 padding_0">
                <thead>
                <tr className="border_top_none">
                  <th className="table_header w_60">Name</th>
                  <th className="table_header w_18">Key</th>
                  <th className="table_header w_18">Created Date</th>
                  <th className="table_header w_4"></th>
                </tr>
                </thead>
              </table>
              <div className="overflow_auto w_100">
                <table className="table_css margin_0">
                  <tbody>
                  {apiKeys.map((item, index) => (
                    <tr key={index}>
                      <td className="table_data w_60">{item.name}</td>
                      <td className="table_data w_18">{item.key.slice(0, 2) + "****" + item.key.slice(-4)}</td>
                      <td className="table_data w_18">{item.created_at}</td>
                      <td className="table_data w_4 cursor_pointer" onMouseLeave={() => setActiveDropdown(null)} onClick={() => {
                        if (activeDropdown === index) {
                          setActiveDropdown(null);
                        } else {
                          setActiveDropdown(index);
                        }
                      }}>
                        <Image className="rotate_90" width={16} height={16} src="/images/three_dots.svg" alt="run-icon"/>
                       <div style={activeDropdown === index ? {display: 'block'} : {display: 'none'}} onMouseLeave={() => setActiveDropdown(null)}>
                          <ul className="dropdown_container">
                            <li className="dropdown_item" onClick={() => {setEditKey(item.name); setEditKeyId(item.id); setEditModal(true); setActiveDropdown(null);}}>Edit</li>
                            <li className="dropdown_item" onClick={() => {setDeleteKeyId(item.id); setDeleteKey(item.name) ; setDeleteModal(true); setActiveDropdown(null);}}>Delete</li>
                          </ul> </div></td>
                    </tr>
                  ))}
                  </tbody>
                </table>
              </div>
            </div>}
        </div>
      </div> :  <div className="loading_container">
          <div className="signInInfo loading_text">{loadingText}</div>
        </div>}
      </div>
      <div className="col-2"></div>
    </div>

    {createModal && (<div className="modal" onClick={() => setCreateModal(false)}>
      <div className="modal-content w_35" onClick={preventDefault}>
        <div className={styles.detail_name}>Create new API Key</div>
        <div>
          <label className={styles.form_label}>Name</label>
          <input placeholder="Enter key name" className="input_medium" type="text" value={keyName} onChange={handleModelApiKey}/>
        </div>
        <div className={agentStyles.modal_buttons}>
          <button className="secondary_button mr_10" onClick={() => setCreateModal(false)}>
            Cancel
          </button>
          <button className="primary_button" onClick={() => createApikey()}>
            Create Key
          </button>
        </div>
      </div>
    </div>)}

    {displayModal && apiKeyGenerated && (<div className="modal" onClick={() => setDisplayModal(false)}>
      <div className="modal-content w_35" onClick={preventDefault}>
        <div className={styles.detail_name}>{keyName} is created</div>
        <div>
          <div className="mt_15 mb_25">
            <div className={styles1.knowledge_alert}>
              <div className={agentStyles.modal_info_class}>
                <Image width={20} height={20} src='/images/info.svg' alt="info-icon"/>
              </div>
              <div>
                Your secret API keys are sensitive pieces of information that should be kept confidential. Do not share them with anyone, and do not expose them in any way. If your secret API keys are compromised, someone could use them to access your API and make unauthorized changes to your data. This secret key is only displayed once for security reasons. Please save it in a secure location where you can access it easily.
              </div>
            </div>
          </div>
          <div>
           <div className="title_wrapper">
              <div className="flex_1"><input ref={apiKeyRef} className="input_medium" type="text" value={apiKeyGenerated} disabled />
              </div>
             <div>
                <button className="secondary_button ml_4 padding_5" onClick={handleCopyClick}>
                  <Image width={20} height={21} src="/images/copy_icon.svg" alt="copy-icon"/>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div className={agentStyles.modal_buttons}>
          <button className="primary_button" onClick={() => setDisplayModal(false)}>
            OK
          </button>
        </div>
      </div>
    </div>)}

    {editModal && (<div className="modal" onClick={() => {setEditModal(false); setEditKey(''); setEditKeyId(-1)}}>
      <div className="modal-content w_35" onClick={preventDefault}>
        <div className={styles.detail_name}>Edit API Key</div>
            <div>
                <label className={styles.form_label}>Name</label>
                <input ref={editKeyRef} placeholder={editKey} className="input_medium" type="text" onChange={handleEditApiKey}/>
            </div>
        <div className={agentStyles.modal_buttons}>
          <button className="secondary_button mr_10" onClick={() => {setEditModal(false); setEditKey(''); setEditKeyId(-1)}}>
            Cancel
          </button>
          <button className="primary_button" onClick={() => handleEditClick()}>
            Update Changes
          </button>
        </div>
      </div>
    </div>)}

    {deleteModal && (<div className="modal" onClick={() => {setDeleteModal(false); setDeleteKeyId(-1); setDeleteKey('')}}>
      <div className="modal-content w_35" onClick={preventDefault}>
        <div className={styles.detail_name}>Delete {deleteKey} Key</div>
        <div>
          <label className={styles.form_label}>Deleting this API key will make it unusable. Any API requests made using this key will be rejected. Are you sure you want to proceed?</label>
        </div>
        <div className={agentStyles.modal_buttons}>
          <button className="secondary_button mr_10" onClick={() => {setDeleteModal(false); setDeleteKeyId(-1); setDeleteKey('')}}>
            Cancel
          </button>
          <button className="primary_button" onClick={() => handleDeleteClick()}>
            Delete Key
          </button>
        </div>
      </div>
    </div>)}
    <ToastContainer/>
  </>)
}