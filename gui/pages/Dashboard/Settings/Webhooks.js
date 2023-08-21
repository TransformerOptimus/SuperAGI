import React, {useState, useEffect} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import agentStyles from "@/pages/Content/Agents/Agents.module.css";
import {
  deleteWebhook,
  getWebhook, saveWebhook,
} from "@/pages/api/DashboardService";
import {loadingTextEffect, removeTab} from "@/utils/utils";
import Image from "next/image";
import styles from "@/pages/Content/Marketplace/Market.module.css";
export default function Webhooks() {
  const [webhookUrl, setWebhookUrl] = useState('');
  const [webhookName, setWebhookName] = useState('');
  const [webhookId, setWebhookId] = useState(-1);
  const [isLoading, setIsLoading] = useState(true)
  const [existingWebhook, setExistingWebhook] = useState(false)
  const [loadingText, setLoadingText] = useState("Loading Webhooks");

  useEffect(() => {
    loadingTextEffect('Loading Webhooks', setLoadingText, 500);
    fetchWebhooks();
  }, []);

  const handleWebhookChange = (event) => {
    setWebhookUrl(event.target.value);
  };
  const handleWebhookName = (event) => {
    setWebhookName(event.target.value);
  };

  const handleSaveWebhook = () => {
    if(!webhookUrl || webhookUrl.trim() === ""){
      toast.error("Enter valid webhook", {autoClose: 1800});
      return;
    }

    saveWebhook({name : webhookName, url: webhookUrl, headers: {}})
      .then((response) => {
        setExistingWebhook(true)
        setWebhookId(response.data.id)
        toast.success("Webhook created successfully", {autoClose: 1800});
      })
      .catch((error) => {
        toast.error("Unable to create webhook", {autoClose: 1800});
        console.error('Error saving webhook', error);
      });
  }

  const fetchWebhooks = () => {
    getWebhook()
      .then((response) => {
        setIsLoading(false)
        if(response.data){
          setWebhookUrl(response.data.url)
          setWebhookName(response.data.name)
          setExistingWebhook(true)
          setWebhookId(response.data.id)
        }
        else{
          setWebhookUrl('')
          setWebhookName('')
          setExistingWebhook(false)
          setWebhookId(-1)
        }
      })
      .catch((error) => {
        console.error('Error fetching webhook', error);
      });
  }

  const deleteExistingWebhook = () => {
    deleteWebhook(webhookId)
      .then((response) => {
        fetchWebhooks()
        toast.success("Webhook deleted successfully", {autoClose: 1800});
      })
      .catch((error) => {
        console.error('Error fetching webhook', error);
      });
  }

  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6 col-6-scrollable">
        {!isLoading ? <div>
          <div className="title_wrapper mb_15">
            <div className={styles.page_title}>Webhooks</div>
            {existingWebhook &&
              <button className="primary_button" onClick={() => deleteExistingWebhook()} >
                Delete
              </button>}
          </div>

          <div>
            <label className={agentStyles.form_label}>Name</label>
            <input disabled={existingWebhook ? true : false} placeholder="Enter webhook name" className="input_medium" type="text" value={webhookName}
                   onChange={handleWebhookName}/>
            <br />
            <label className={agentStyles.form_label}>Destination URL</label>
            <div style={{display:'flex', justifyContent: 'space-between'}}>
              <button className="secondary_button mr_5" disabled>
                <span>POST</span>
              </button>
              <input disabled={existingWebhook ? true : false} className="input_medium" placeholder="Enter your destination url" type="text" value={webhookUrl}
                     onChange={handleWebhookChange}/>
            </div>
          </div>

          {!existingWebhook && <div className="justify_end display_flex mt_15">
            <button onClick={() => removeTab(-3, "Settings", "Settings", 0)} className="secondary_button mr_10">
              Cancel
            </button>
            <button className="primary_button" onClick={handleSaveWebhook}>
              Update Changes
            </button>
          </div>}

        </div> :  <div className="loading_container">
          <div className="signInInfo loading_text">{loadingText}</div>
        </div>}
      </div>
      <div className="col-3"></div>
    </div>
    <ToastContainer/>
  </>)
}