import React, {useEffect, useState} from 'react';
import Image from 'next/image';
import {ToastContainer, toast} from 'react-toastify';
import {updateToolConfig, getToolConfig, authenticateGoogleCred, authenticateTwitterCred} from "@/pages/api/DashboardService";
import styles from './Tool.module.css';
import {EventBus} from "@/utils/eventBus";

export default function ToolWorkspace({toolDetails}){
    const [activeTab,setActiveTab] = useState('Configuration')
    const [showDescription,setShowDescription] = useState(false)
    const [apiConfigs, setApiConfigs] = useState([]);
    const [toolsIncluded, setToolsIncluded] = useState([]);
    const [loading, setLoading] = useState(true);

    let handleKeyChange = (event, index) => {
      const updatedData = [...apiConfigs];
      updatedData[index].value = event.target.value;
      setApiConfigs(updatedData);
    };
    
    function getToken(client_data){
      const client_id = client_data.client_id 
      const scope = 'https://www.googleapis.com/auth/calendar';
      const redirect_uri = 'http://localhost:3000/api/oauth-calendar';
      window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${client_id}&redirect_uri=${redirect_uri}&access_type=offline&response_type=code&scope=${scope}`;
    }
    
    async function getSignature(baseString, signingKey){
      const key = new TextEncoder().encode(signingKey);
      const data = new TextEncoder().encode(baseString);
      const signature = new Uint8Array(await crypto.subtle.sign({name: 'HMAC', hash: 'SHA-1'},))
    }

    function getTwitterToken(oauth_data){
      const oauth_token = oauth_data.oauth_token
      const oauth_token_secret = oauth_data.oauth_token_secret
      const authUrl = `https://api.twitter.com/oauth/authenticate?oauth_token=${oauth_token}`
      window.location.href = authUrl
    }

    useEffect(() => {
      if(toolDetails !== null) {
        if (toolDetails.tools) {
          setToolsIncluded(toolDetails.tools);
        }

        getToolConfig(toolDetails.name)
          .then((response) => {
            const apiConfigs = response.data || [];
            setApiConfigs(apiConfigs);
          })
          .catch((error) => {
            console.log('Error fetching API data:', error);
          })
          .finally(() => {
            setLoading(false);
          });
      }
    }, [toolDetails]);

    const handleUpdateChanges = async () => {
      const updatedConfigData = apiConfigs.map((config) => ({
        key: config.key,
        value: config.value,
      }));
      
      updateToolConfig(toolDetails.name, updatedConfigData)
        .then((response) => {
            toast.success('Toolkit configuration updated', {autoClose: 1800});
        })
        .catch((error) => {
          toast.error('Unable to update Toolkit configuration', {autoClose: 1800});
          console.error('Error updating tool config:', error);
        });
    };

    const handleAuthenticateClick = async () => {
      authenticateGoogleCred(toolDetails.id)
        .then((response) => {
          getToken(response.data);
        })
        .catch((error) => {
          console.error('Error fetching data:', error);
        });
    };

    const handleTwitterAuthClick = async () => {
      authenticateTwitterCred(toolDetails.id)
      .then((response) => {
        console.log("/////////////////////")
        console.log(response.data)
        getTwitterToken(response.data);
      })
      .catch((error) => {
        console.error('Error fetching data: ', error);
      });
    };

    return (<>
        <div className={styles.tools_container}>
          <div style={{display: 'flex',justifyContent:'flex-start',marginBottom:'20px', width:'600px'}}>
            <div>
              <Image src="/images/custom_tool.svg" alt="toolkit-icon" width={45} height={45}/>
            </div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ marginLeft: '15px',textAlign:'left',paddingRight:'10px' }}>
                <div style={{fontSize:'17px',marginTop:'-3px'}}>{toolDetails.name}</div>
                <div className={styles.toolkit_description} style={!showDescription ? { overflow: 'hidden' } : {display:'block'}}>
                  {`${showDescription ? toolDetails.description : toolDetails.description.slice(0, 80)}`}
                  {toolDetails.description.length > 80 && <span className={styles.show_more_button} onClick={() => setShowDescription(!showDescription)}>
                      {showDescription ? '...less' : '...more'}
                  </span>}
                </div>
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center',marginBottom:'20px' }}>
            <div className={styles.tool1_box} onClick={() => setActiveTab('Configuration')} style={activeTab === 'Configuration' ? { background: '#454254'} : { background: 'transparent'}}>
              <div className={styles.tab_text}>Configuration</div>
            </div>
            <div className={styles.tool1_box} onClick={() => setActiveTab('Tools_Included')} style={activeTab === 'Tools_Included' ? { background: '#454254' } : { background: 'transparent' }}>
              <div className={styles.tab_text}>Tools Included</div>
            </div>
          </div>
          {!loading && activeTab === 'Configuration' && <div>
          {apiConfigs.length > 0 ? (apiConfigs.map((config, index) => (
              <div key={index}>
                <div style={{ color: '#888888', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', marginBottom: '20px' }}>
                  <label style={{ marginBottom: '6px' }}>{config.key}</label>
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
              <div>
                {toolDetails.name === 'Google Calendar Toolkit' && <button style={{width:'200px'}} className={styles.primary_button} onClick={handleAuthenticateClick}>Authenticate Tool</button>}
                {toolDetails.name === 'Twitter Toolkit' && <button style={{width:'200px'}} className={styles.primary_button} onClick={handleTwitterAuthClick}>Authenticate Tool</button>}
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <button className={styles.primary_button} onClick={handleUpdateChanges} >Update Changes</button>
              </div>
            </div>)}
          </div>}
          {activeTab === 'Tools_Included' && <div>
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
      <ToastContainer/>
    </>);
}





