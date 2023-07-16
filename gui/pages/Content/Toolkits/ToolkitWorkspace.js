import React, {useEffect, useState} from 'react';
import Image from 'next/image';
import {ToastContainer, toast} from 'react-toastify';
import {updateToolConfig, getToolConfig, authenticateGoogleCred, authenticateTwitterCred} from "@/pages/api/DashboardService";
import styles from './Tool.module.css';
import {setLocalStorageValue, setLocalStorageArray, returnToolkitIcon, convertToTitleCase} from "@/utils/utils";

export default function ToolkitWorkspace({toolkitDetails, internalId}){
    const [activeTab,setActiveTab] = useState('configuration')
    const [showDescription,setShowDescription] = useState(false)
    const [apiConfigs, setApiConfigs] = useState([]);
    const [toolsIncluded, setToolsIncluded] = useState([]);
    const [loading, setLoading] = useState(true);
    const authenticateToolkits = ['Google Calendar Toolkit', 'Twitter Toolkit'];

    let handleKeyChange = (event, index) => {
      const updatedData = [...apiConfigs];
      updatedData[index].value = event.target.value;
      setLocalStorageArray('api_configs_' + String(internalId), updatedData, setApiConfigs);
    };
    
    function getGoogleToken(client_data){
      const client_id = client_data.client_id 
      const scope = 'https://www.googleapis.com/auth/calendar';
      const redirect_uri = 'http://localhost:3000/api/google/oauth-tokens';
      window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${client_id}&redirect_uri=${redirect_uri}&access_type=offline&response_type=code&scope=${scope}`;
    }
    
    function getTwitterToken(oauth_data){
      window.location.href = `https://api.twitter.com/oauth/authenticate?oauth_token=${oauth_data.oauth_token}`
    }

    useEffect(() => {
      if(toolkitDetails !== null) {
        if (toolkitDetails.tools) {
          setToolsIncluded(toolkitDetails.tools);
        }

        getToolConfig(toolkitDetails.name)
          .then((response) => {
            const localStoredConfigs = localStorage.getItem('api_configs_' + String(internalId));
            const apiConfigs = response.data || [];
            setApiConfigs(localStoredConfigs ? JSON.parse(localStoredConfigs) : apiConfigs);
          })
          .catch((errPor) => {
            console.log('Error fetching API data:', error);
          })
          .finally(() => {
            setLoading(false);
          });
      }
    }, [toolkitDetails]);

    const handleUpdateChanges = async () => {
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
        if (toolkitName === "Google Calendar Toolkit"){
      authenticateGoogleCred(toolkitDetails.id)
        .then((response) => {
          localStorage.setItem("google_calendar_toolkit_id", toolkitDetails.id)
            getGoogleToken(response.data);
        })
        .catch((error) => {
          console.error('Error fetching data:', error);
        });
    }else if(toolkitName === "Twitter Toolkit"){
        authenticateTwitterCred(toolkitDetails.id)
            .then((response) => {
                localStorage.setItem("twitter_toolkit_id", toolkitDetails.id)
                getTwitterToken(response.data);
            })
            .catch((error) => {
                console.error('Error fetching data: ', error);
            });
    }
    };

    useEffect(() => {
      if(internalId !== null) {
        const active_tab = localStorage.getItem('toolkit_tab_' + String(internalId));
        if(active_tab) {
          setActiveTab(active_tab);
        }
      }
    }, [internalId]);

    return (<>
      <div className="row">
        <div className="col-3"></div>
        <div className="col-6" style={{overflowY:'scroll',height:'calc(100vh - 92px)',padding:'25px 20px'}}>
          <div className={styles.tools_container}>
          <div style={{display: 'flex',justifyContent:'flex-start',marginBottom:'20px',width:'95%'}}>
            <div>
              <Image src={returnToolkitIcon(toolkitDetails?.name)} alt="toolkit-icon" width={45} height={45} style={{borderRadius:'25px',background: 'black'}} />
            </div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ marginLeft: '15px',textAlign:'left',paddingRight:'10px' }}>
                <div style={{fontSize:'17px',marginTop:'-3px'}}>{toolkitDetails.name}</div>
                <div className={styles.toolkit_description} style={!showDescription ? { overflow: 'hidden' } : {display:'block'}}>
                  {`${showDescription ? toolkitDetails.description : toolkitDetails.description.slice(0, 70)}`}
                  {toolkitDetails.description.length > 70 && <span className={styles.show_more_button} onClick={() => setShowDescription(!showDescription)}>
                      {showDescription ? '...less' : '...more'}
                  </span>}
                </div>
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center',marginBottom:'20px' }}>
            <div className={styles.tool1_box} onClick={() => setLocalStorageValue('toolkit_tab_' + String(internalId), 'configuration', setActiveTab)} style={activeTab === 'configuration' ? { background: '#454254'} : { background: 'transparent'}}>
              <div className={styles.tab_text}>Configuration</div>
            </div>
            <div className={styles.tool1_box} onClick={() => setLocalStorageValue('toolkit_tab_' + String(internalId), 'tools_included', setActiveTab)} style={activeTab === 'tools_included' ? { background: '#454254' } : { background: 'transparent' }}>
              <div className={styles.tab_text}>Tools Included</div>
            </div>
          </div>
          {!loading && activeTab === 'configuration' && <div>
            {apiConfigs.length > 0 ? (apiConfigs.map((config, index) => (
              <div key={index}>
                <div style={{ color: '#888888', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', marginBottom: '20px' }}>
                  <label style={{ marginBottom: '6px' }}>{convertToTitleCase(config.key)}</label>
                  <div className={styles.search_box}>
                    <input type="text" style={{ color: 'white',width:'100%' }} value={config.value || ''} onChange={(event) => handleKeyChange(event, index)}/>
                  </div>
                </div>
              </div>
            ))) : (<div style={{display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',marginTop:'40px',width:'100%'}}>
              <Image width={150} height={60} src="/images/no_permissions.svg" alt="no-permissions" />
              <span className={styles.feed_title} style={{marginTop: '8px'}}>No Keys found!</span>
            </div>)}

            {apiConfigs.length > 0 && (
              <div style={{ marginLeft: 'auto', display: 'flex', justifyContent:'space-between'}}>
                <div>{authenticateToolkits.includes(toolkitDetails.name) &&
                  <button style={{width:'fit-content'}} className={styles.primary_button} onClick={() => handleAuthenticateClick(toolkitDetails.name)}>Authenticate Tool</button>
                }</div>
                <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <button className={styles.primary_button} onClick={handleUpdateChanges} >Update Changes</button>
                </div>
              </div>)}
          </div>}
          {activeTab === 'tools_included' && <div>
            {toolsIncluded.map((tool, index) => (
              <div key={index} className={styles.tools_included}>
                <div>
                  <div style={{color:'white'}}>{tool.name}</div>
                  <div style={{color:'#888888',marginTop:'5px'}}>{tool.description}</div>
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





