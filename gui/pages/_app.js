import React, {useState, useEffect} from 'react';
import SideBar from './Dashboard/SideBar';
import Content from './Dashboard/Content';
import TopBar from './Dashboard/TopBar';
import 'bootstrap/dist/css/bootstrap.css';
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import './_app.css'
import Head from 'next/head';
import Image from "next/image";
import {
  getOrganisation,
  getProject,
  validateAccessToken,
  checkEnvironment,
  addUser,
  installToolkitTemplate, installAgentTemplate, installKnowledgeTemplate
} from "@/pages/api/DashboardService";
import {githubClientId} from "@/pages/api/apiConfig";
import {
  getGithubClientId
} from "@/pages/api/DashboardService";
import {useRouter} from 'next/router';
import querystring from 'querystring';
import {refreshUrl, loadingTextEffect} from "@/utils/utils";
import MarketplacePublic from "./Content/Marketplace/MarketplacePublic"
import {toast} from "react-toastify";

export default function App() {
  const [selectedView, setSelectedView] = useState('');
  const [applicationState, setApplicationState] = useState("LOADING");
  const [selectedProject, setSelectedProject] = useState(null);
  const [userName, setUserName] = useState('');
  const [organisationId, setOrganisationId] = useState(null);
  const [env, setEnv] = useState('DEV');
  const [loadingText, setLoadingText] = useState("Initializing SuperAGI");
  const router = useRouter();
  const [showMarketplace, setShowMarketplace] = useState(false);
  const excludedKeys = [
    'repo_starred',
    'popup_closed_time',
    'twitter_toolkit_id',
    'accessToken',
    'agent_to_install',
    'toolkit_to_install',
    'google_calendar_toolkit_id',
    'knowledge_to_install',
    'knowledge_index_to_install',
    'myLayoutKey'
  ];

  function fetchOrganisation(userId) {
    getOrganisation(userId)
      .then((response) => {
        setOrganisationId(response.data.id);
      })
      .catch((error) => {
        console.error('Error fetching project:', error);
      });
  }

  const installFromMarketplace = () => {
    const toolkitName = localStorage.getItem('toolkit_to_install') || null;
    const agentTemplateId = localStorage.getItem('agent_to_install') || null;
    const knowledgeTemplateName = localStorage.getItem('knowledge_to_install') || null;
    const knowledgeIndexId = localStorage.getItem('knowledge_index_to_install') || null;

    if (knowledgeTemplateName !== null && knowledgeIndexId !== null) {
      installKnowledgeTemplate(knowledgeTemplateName, knowledgeIndexId)
        .then((response) => {
          toast.success("Template installed", {autoClose: 1800});
        })
        .catch((error) => {
          console.error('Error installing template:', error);
        });
      localStorage.removeItem('knowledge_to_install');
      localStorage.removeItem('knowledge_index_to_install');
    }

    if (toolkitName !== null) {
      installToolkitTemplate(toolkitName)
        .then((response) => {
          toast.success("Template installed", {autoClose: 1800});
        })
        .catch((error) => {
          console.error('Error installing template:', error);
        });
      localStorage.removeItem('toolkit_to_install');
    }

    if (agentTemplateId !== null) {
      installAgentTemplate(agentTemplateId)
        .then((response) => {
          toast.success("Template installed", {autoClose: 1800});
        })
        .catch((error) => {
          console.error('Error installing template:', error);
        });
      localStorage.removeItem('agent_to_install');
    }
  }

  useEffect(() => {
    if (window.location.href.toLowerCase().includes('marketplace')) {
      setShowMarketplace(true);
    } else {
      installFromMarketplace();
    }

    loadingTextEffect('Initializing SuperAGI', setLoadingText, 500);

    checkEnvironment()
      .then((response) => {
        const env = response.data.env;
        setEnv(env);

        if (typeof window !== 'undefined') {
          localStorage.setItem('applicationEnvironment', env);
        }

        if (response.data.env === 'PROD') {
          setApplicationState("NOT_AUTHENTICATED");
          const queryParams = router.asPath.split('?')[1];
          const parsedParams = querystring.parse(queryParams);
          let access_token = parsedParams.access_token || null;

          if (typeof window !== 'undefined' && access_token) {
            localStorage.setItem('accessToken', access_token);
            refreshUrl();
          }

          validateAccessToken()
            .then((response) => {
              setUserName(response.data.name || '');
              fetchOrganisation(response.data.id);
            })
            .catch((error) => {
              console.error('Error validating access token:', error);
            });
        } else {
          const userData = {
            "name": "SuperAGI User",
            "email": "super6@agi.com",
            "password": "pass@123",
          }

          addUser(userData)
            .then((response) => {
              setUserName(response.data.name);
              fetchOrganisation(response.data.id);
            })
            .catch((error) => {
              console.error('Error adding user:', error);
            });
        }
      })
      .catch((error) => {
        console.error('Error fetching project:', error);
      });
  }, []);

  useEffect(() => {
    if (organisationId !== null) {
      getProject(organisationId)
        .then((response) => {
          setSelectedProject(response.data[0]);
        })
        .catch((error) => {
          console.error('Error fetching project:', error);
        });
    }
  }, [organisationId]);

  useEffect(() => {
    if (selectedProject !== null) {
      setApplicationState("AUTHENTICATED");
    }
  }, [selectedProject]);

  const handleSelectionEvent = (data) => {
    setSelectedView(data);
  };

  async function signInUser() {
    let github_client_id = githubClientId();

      // If `github_client_id` does not exist, make the API call
      if (!github_client_id) {
        const response = await getGithubClientId();
        github_client_id = response.data.github_client_id;
      }
      if(!github_client_id) {
         console.error('Error fetching github client id make sure to set it in the config file');
      }
      else {
        window.open(`https://github.com/login/oauth/authorize?scope=user:email&client_id=${github_client_id}`, '_self')
      }
  }

  useEffect(() => {
    const clearLocalStorage = () => {
      Object.keys(localStorage).forEach((key) => {
        if (!excludedKeys.includes(key)) {
          localStorage.removeItem(key);
        }
      });
    };

    window.addEventListener('beforeunload', clearLocalStorage);
    window.addEventListener('unload', clearLocalStorage);

    return () => {
      window.removeEventListener('beforeunload', clearLocalStorage);
      window.removeEventListener('unload', clearLocalStorage);
    };
  }, []);

  return (
    <div className="app">
      <Head>
        <title>SuperAGI</title>
        {/* eslint-disable-next-line @next/next/no-page-custom-font */}
        <link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro&display=swap" rel="stylesheet"/>
        {/* eslint-disable-next-line @next/next/no-page-custom-font */}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
              rel="stylesheet"/>
      </Head>
      {showMarketplace && <div className="projectStyle"><MarketplacePublic env={env}/></div>}
      {applicationState === 'AUTHENTICATED' && !showMarketplace ? (<div className="projectStyle">
        <div className="sideBarStyle">
          <SideBar onSelectEvent={handleSelectionEvent} env={env}/>
        </div>
        <div className="workSpaceStyle">
          <div className="topBarStyle">
            <TopBar selectedProject={selectedProject} organisationId={organisationId} userName={userName} env={env}/>
          </div>
          <div className="contentStyle">
            <Content env={env} organisationId={organisationId} selectedView={selectedView}
                     selectedProjectId={selectedProject?.id || ''}/>
          </div>
        </div>
      </div>) : !showMarketplace ? (<div className="signInStyle">
        <div className="signInTopBar">
          <div className="superAgiLogo"><Image width={132} height={72} src="/images/sign-in-logo.svg"
                                               alt="super-agi-logo"/></div>
        </div>
        <div className="signInCenter">
          {applicationState === 'NOT_AUTHENTICATED' && !showMarketplace ? <div className="signInWrapper">
            <button className="signInButton" onClick={signInUser}>
              <Image width={20} height={20} src="/images/github.svg" alt="github"/>&nbsp;Continue with Github
            </button>
            <div className="signInInfo">
              By continuing, you agree to Super AGI’s Terms of Service and Privacy Policy, and to receive important
              updates.
            </div>
          </div> : <div className="signInWrapper" style={{background: 'transparent'}}>
            <div className="signInInfo" style={{fontSize: '16px', fontFamily: 'Source Code Pro'}}>{loadingText}</div>
          </div>}
        </div>
      </div>) : true}
    </div>
  );
}