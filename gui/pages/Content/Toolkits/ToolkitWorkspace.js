import React, {useEffect, useState} from 'react';
import Image from 'next/image';
import {ToastContainer, toast} from 'react-toastify';
import {
  updateToolConfig,
  getToolConfig,
  authenticateGoogleCred,
  authenticateTwitterCred
} from "@/pages/api/DashboardService";
import styles from './Tool.module.css';
import {setLocalStorageValue, setLocalStorageArray, returnToolkitIcon, convertToTitleCase} from "@/utils/utils";

export default function ToolkitWorkspace({env, toolkitDetails, internalId}) {
  const [activeTab, setActiveTab] = useState('configuration')
  const [showDescription, setShowDescription] = useState(false)
  const [apiConfigs, setApiConfigs] = useState([]);
  const [toolsIncluded, setToolsIncluded] = useState([]);
  const [loading, setLoading] = useState(true);
  const authenticateToolkits = ['Google Calendar Toolkit', 'Twitter Toolkit'];

  let handleKeyChange = (event, index) => {
    const updatedData = [...apiConfigs];
    updatedData[index].value = event.target.value;
    setLocalStorageArray('api_configs_' + String(internalId), updatedData, setApiConfigs);
  };

  function getGoogleToken(client_data) {
    var redirect_uri = "";
    if (env == "PROD") {
      redirect_uri = 'https://app.superagi.com/api/google/oauth-tokens';
    } else {
      redirect_uri = "http://localhost:3000/api/google/oauth-tokens";
    }
    const client_id = client_data.client_id
    const scope = 'https://www.googleapis.com/auth/calendar';
    window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${client_id}&redirect_uri=${redirect_uri}&access_type=offline&approval_prompt=force&response_type=code&scope=${scope}&state=${toolkitDetails.id}`;
  }

  function getTwitterToken(oauth_data) {
    window.location.href = `https://api.twitter.com/oauth/authenticate?oauth_token=${oauth_data.oauth_token}`
  }

  useEffect(() => {
    if (toolkitDetails !== null) {
      if (toolkitDetails.tools) {
        setToolsIncluded(toolkitDetails.tools);
      }

      getToolConfig(toolkitDetails.name)
        .then((response) => {
          const localStoredConfigs = localStorage.getItem('api_configs_' + String(internalId));
          const apiConfigs = response.data || [];
          setApiConfigs(localStoredConfigs ? JSON.parse(localStoredConfigs) : apiConfigs);
        })
        .catch((error) => {
          console.log('Error fetching API data:', error);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [toolkitDetails]);

  const handleUpdateChanges = async () => {
    if(apiConfigs.some(config => config?.is_required && !config.value)){
      toast.error("Please input necessary details", 1800)
      return
    }
    const updatedConfigData = apiConfigs.map((config) => ({
      key: config.key,
      value: config.value,
    }));

    updateToolConfig(toolkitDetails.name, updatedConfigData)
      .then((response) => {
        toast.success('Toolkit configuration updated', {autoClose: 1800});
      })
      .catch((error) => {
        toast.error('Unable to update Toolkit configuration', {autoClose: 1800});
        console.error('Error updating tool config:', error);
      });
  };

  const handleAuthenticateClick = async (toolkitName) => {
    handleUpdateChanges();
    if (toolkitName === "Google Calendar Toolkit") {
      authenticateGoogleCred(toolkitDetails.id)
        .then((response) => {
          localStorage.setItem("google_calendar_toolkit_id", toolkitDetails.id)
          getGoogleToken(response.data);
        })
        .catch((error) => {
          toast.error('Unable to authenticate tool', {autoClose: 1800});
          console.error('Error fetching data:', error);
        });
    } else if (toolkitName === "Twitter Toolkit") {
      authenticateTwitterCred(toolkitDetails.id)
        .then((response) => {
          localStorage.setItem("twitter_toolkit_id", toolkitDetails.id)
          getTwitterToken(response.data);
        })
        .catch((error) => {
          toast.error('Unable to authenticate tool', {autoClose: 1800});
          console.error('Error fetching data: ', error);
        });
    }
  };

  useEffect(() => {
    if (internalId !== null) {
      const active_tab = localStorage.getItem('toolkit_tab_' + String(internalId));
      if (active_tab) {
        setActiveTab(active_tab);
      }
    }
  }, [internalId]);

  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6 col-6-scrollable">
        <div className={styles.tools_container}>
          <div className="horizontal_container align_start mb_20">
            <Image src={returnToolkitIcon(toolkitDetails?.name)} alt="toolkit-icon" width={45} height={45} className="tool_icon" />
            <div className="vertical_containers ml_15 text_align_left mr_10">
              <div className="text_17">{toolkitDetails.name}</div>
              <div className={styles.toolkit_description} style={!showDescription ? {overflow: 'hidden'} : {display: 'block'}}>
                {`${showDescription ? toolkitDetails.description : toolkitDetails.description.slice(0, 70)}`}
                {toolkitDetails.description.length > 70 &&
                    <span className={styles.show_more_button} onClick={() => setShowDescription(!showDescription)}>
                      {showDescription ? '...less' : '...more'}
                  </span>}
              </div>
            </div>
          </div>
          <div className="horizontal_container mb_20">
            <div className={activeTab === 'configuration' ? 'tab_button_small_selected' : 'tab_button_small'}
                 onClick={() => setLocalStorageValue('toolkit_tab_' + String(internalId), 'configuration', setActiveTab)}>
              <div className="text_12 color_white padding_8">Configuration</div>
            </div>
            <div className={activeTab === 'tools_included' ? 'tab_button_small_selected' : 'tab_button_small'}
                 onClick={() => setLocalStorageValue('toolkit_tab_' + String(internalId), 'tools_included', setActiveTab)}>
              <div className="text_12 color_white padding_8">Tools Included</div>
            </div>
          </div>
          {!loading && activeTab === 'configuration' && <div>
            {apiConfigs.length > 0 ? (apiConfigs.map((config, index) => (
              <div key={index}>
                <div className="vertical_containers w_100 color_gray mb_20 text_align_left">
                  <label className="mb_6">{convertToTitleCase(config.key)}</label>
                  <div className={styles.search_box}>
                    {config?.key_type !== "file" && <input className="color_white" type={config?.is_secret ? 'password' : 'text'} value={config.value || ''} onChange={(event) => handleKeyChange(event, index)}/>}
                    {config?.key_type === "file" && <textarea className="color_white" type={config?.is_secret ? 'password' : 'text'} value={config.value || ''} onChange={(event) => handleKeyChange(event, index)}/>}
                  </div>
                </div>
              </div>
            ))) : (<div className="vertical_container mt_40 w_100">
              <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions"/>
              <span className="feed_title mt_8">No Keys found!</span>
            </div>)}

            {apiConfigs.length > 0 && (
              <div className="horizontal_space_between">
                {authenticateToolkits.includes(toolkitDetails.name) &&
                  <button className="primary_button w_fit_content" onClick={() => handleAuthenticateClick(toolkitDetails.name)}>Authenticate Tool</button>}
                  <button className="primary_button" onClick={handleUpdateChanges}>Update Changes</button>
              </div>)}
          </div>}
          {activeTab === 'tools_included' && <div>
            {toolsIncluded.map((tool, index) => (
              <div key={index} className={styles.tools_included}>
                <div>
                  <div className="color_white">{tool.name}</div>
                  <div className="color_gray mt_5">{tool.description}</div>
                </div>
              </div>
            ))}
          </div>}
        </div>
      </div>
      <div className="col-3"></div>
    </div>
    <ToastContainer/>
  </>);
}




