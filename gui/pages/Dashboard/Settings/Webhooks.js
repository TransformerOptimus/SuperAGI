import React, {useState, useEffect} from 'react';
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import agentStyles from "@/pages/Content/Agents/Agents.module.css";
import {
  editWebhook,
  getWebhook, saveWebhook,
} from "@/pages/api/DashboardService";
import {loadingTextEffect, removeTab} from "@/utils/utils";
import styles from "@/pages/Content/Marketplace/Market.module.css";
export default function Webhooks() {
  const [webhookUrl, setWebhookUrl] = useState('');
  const [webhookId, setWebhookId] = useState(-1);
  const [isLoading, setIsLoading] = useState(true)
  const [existingWebhook, setExistingWebhook] = useState(false)
  const [isEdtiting, setIsEdtiting] = useState(false)
  const [loadingText, setLoadingText] = useState("Loading Webhooks");
  const [selectedCheckboxes, setSelectedCheckboxes] = useState([]);
  const checkboxes = [
    { label: 'Agent is running', value: 'RUNNING' },
    { label: 'Agent run is paused', value: 'PAUSED' },
    { label: 'Agent run is completed', value: 'COMPLETED' },
    { label: 'Agent is terminated ', value: 'TERMINATED' },
    { label: 'Agent run max iteration reached', value: 'MAX ITERATION REACHED' },
  ];


  useEffect(() => {
    loadingTextEffect('Loading Webhooks', setLoadingText, 500);
    fetchWebhooks();
  }, []);

  const handleWebhookChange = (event) => {
    setWebhookUrl(event.target.value);
  };

  const handleSaveWebhook = () => {
    if(!webhookUrl || webhookUrl.trim() === ""){
      toast.error("Enter valid webhook", {autoClose: 1800});
      return;
    }
    if(isEdtiting){
      editWebhook(webhookId, { url: webhookUrl, filters: {status: selectedCheckboxes}})
          .then((response) => {
            setIsEdtiting(false)
            fetchWebhooks()
            toast.success("Webhook edited successfully", {autoClose: 1800});
          })
          .catch((error) => {
            console.error('Error fetching webhook', error);
          });
      return;
    }
    saveWebhook({name : "Webhook 1", url: webhookUrl, headers: {}, filters: {status: selectedCheckboxes}})
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
          setExistingWebhook(true)
          setWebhookId(response.data.id)
          setSelectedCheckboxes(response.data.filters.status)
        }
        else{
          setWebhookUrl('')
          setExistingWebhook(false)
          setWebhookId(-1)
        }
      })
      .catch((error) => {
        console.error('Error fetching webhook', error);
      });
  }

  const toggleCheckbox = (value) => {
    if (selectedCheckboxes.includes(value)) {
      setSelectedCheckboxes(selectedCheckboxes.filter((item) => item !== value));
    } else {
      setSelectedCheckboxes([...selectedCheckboxes, value]);
    }
  };

  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6 col-6-scrollable">
        {!isLoading ? <div>
          <div className="title_wrapper mb_15">
            <div className={styles.page_title}>Webhooks</div>
            {existingWebhook &&
              <button className="primary_button" onClick={() => {setExistingWebhook(false);setIsEdtiting(true)} } >
                Edit
              </button>}
          </div>

          <div>
            <label className={agentStyles.form_label}>Destination URL</label>
              <input disabled={existingWebhook ? true : false} className="input_medium" placeholder="Enter your destination url" type="text" value={webhookUrl}
                     onChange={handleWebhookChange}/>
            <br />
            <label className={agentStyles.form_label}>Events to include</label>
            <div className={styles.checkboxGroup} >
              {checkboxes.map((checkbox) => (
                <label key={checkbox.value} className={styles.checkboxLabel}>
                  <input
                    disabled={existingWebhook ? true : false}
                    className="checkbox"
                    type="checkbox"
                    value={checkbox.value}
                    checked={selectedCheckboxes.includes(checkbox.value)}
                    onChange={() => toggleCheckbox(checkbox.value)}
                  />
                  <span className={styles.checkboxText}>&nbsp;{checkbox.label}</span>
                </label>
              ))}
            </div>
          </div>

          {!existingWebhook && <div className="justify_end display_flex_container mt_15">
            <button onClick={() => removeTab(-3, "Settings", "Settings", 0)} className="secondary_button mr_10">
              Cancel
            </button>
            <button className="primary_button" onClick={handleSaveWebhook}>
              {isEdtiting ? "Update" : "Create"}
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