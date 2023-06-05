import React, {useState, useEffect} from 'react';
import SideBar from './Dashboard/SideBar';
import Content from './Dashboard/Content';
import TopBar from './Dashboard/TopBar';
import 'bootstrap/dist/css/bootstrap.css';
import './_app.css'
import Head from 'next/head';
import Image from "next/image";
import { addUser, getOrganization, getProject, validateAccessToken } from "@/pages/api/DashboardService";
import { githubClientId } from "@/pages/api/apiConfig";
import { useRouter } from 'next/router';
import querystring from 'querystring';

export default function App() {
  const [selectedView, setSelectedView] = useState('');
  const [accessToken, setAccessToken] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const organisationId = 1;
  const router = useRouter();

  useEffect(() => {
    if(typeof window !== 'undefined') {
      const includesLocalhost = window.location.href.includes('localhost');

      if(includesLocalhost) {
        const queryParams = router.asPath.split('?')[1];
        const parsedParams = querystring.parse(queryParams);
        let access_token = parsedParams.access_token || null;

        if (access_token) {
          localStorage.setItem('accessToken', access_token);
        } else {
          access_token = localStorage.getItem('accessToken') || null;
        }

        setAccessToken(access_token);
      }
    }
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      getOrganization()
        .then((response) => {

        })
        .catch((error) => {
          console.error('Error adding organization:', error);
        });

      const userData =  {
        "name" : "SuperAGI User",
        "email" : "super6@agi.com",
        "password" : "pass@123",
        "organisation" : organisationId
      }

      addUser(userData)
        .then((response) => {
        })
        .catch((error) => {
          console.error('Error adding user:', error);
        });

      getProject(organisationId)
        .then((response) => {
          setSelectedProject(response.data[0]);
        })
        .catch((error) => {
          console.error('Error fetching project:', error);
        });
    }
  }, [organisationId]);
  
  const handleSelectionEvent = (data) => {
    setSelectedView(data);
  };

  function signInUser() {
    const github_client_id = githubClientId();
    window.open(`https://github.com/login/oauth/authorize?scope=user:email&client_id=${github_client_id}`, '_self')
  }

  return (
    <div className="app">
      <Head>
        {/* eslint-disable-next-line @next/next/no-page-custom-font */}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
      </Head>
      {accessToken !== null && accessToken !== '' ? <div className="projectStyle">
        <div className="sideBarStyle">
          <SideBar onSelectEvent={handleSelectionEvent}/>
        </div>
        <div className="workSpaceStyle">
          <div className="topBarStyle">
            <TopBar selectedProject={selectedProject}/>
          </div>
          <div className="contentStyle">
            <Content selectedView={selectedView} selectedProjectId={selectedProject?.id || ''}/>
          </div>
        </div>
      </div> : <div className="signInStyle">
        <div className="signInTopBar">
          <div className="superAgiLogo"><Image width={132} height={72} src="/images/sign-in-logo.svg" alt="super-agi-logo"/></div>
        </div>
        <div className="signInCenter">
          <div className="signInWrapper">
            <button className="signInButton" onClick={signInUser}>
              <Image width={20} height={20} src="/images/github.svg" alt="github"/>&nbsp;Continue with Github
            </button>
            <div className="signInInfo">
              By continuing, you agree to Super AGI’s Terms of Service and Privacy Policy, and to receive important updates.
            </div>
          </div>
        </div>
      </div>}
    </div>
  );
}
