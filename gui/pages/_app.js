import React, {useState, useEffect} from 'react';
import SideBar from './Dashboard/SideBar';
import Content from './Dashboard/Content';
import TopBar from './Dashboard/TopBar';
import 'bootstrap/dist/css/bootstrap.css';
import './_app.css'
import Head from 'next/head';
import Image from "next/image";
import { addUser, getOrganization, getProject } from "@/app/DashboardService";

export default function App() {
  const [selectedView, setSelectedView] = useState('');
  const [userName, setUserName] = useState("");
  const [isSignedIn, setSignIn] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const organisationId = 1;

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
          setUserName(response.data.name);
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

  const sideBarStyle = {
    height: '100vh',
    width: '6.5vw',
    borderRight: '1px solid #33303F',
    overflowY: 'scroll',
    padding: '0 6px'
  }

  const contentStyle = {
    height: '93.5vh',
    width: '100%',
  }

  const projectStyle = {
    height: '100vh',
    width: '100vw',
    display: 'flex',
    backgroundColor: '#1B192C',
  }

  const workSpaceStyle = {
    height: '100vh',
    width: '93.5vw',
  }

  const topBarStyle = {
    height: '6.5vh',
    width: '100%',
  }

  const signInStyle = {
    background:'#21173A',
    width:'100vw',
    height:'100vh'
  }

  const signInTopBar = {
    width:'100%',
    height:'10vh'
  }

  const superAgiLogo = {
    paddingLeft:'30px',
    display:'flex',
    alignItems:'center'
  }

  const signInCenter = {
    width:'100%',
    height:'90vh',
    display:'flex',
    alignItems:'center',
    justifyContent:'center'
  }

  const signInWrapper = {
    height:'fit-content',
    width:'25vw',
    padding:'25px 20px',
    background: '#3A2E57',
    borderRadius:'8px',
    marginTop:'-30px'
  }

  const signInButton = {
    color:'black',
    width:'100%',
    border:'none',
    background:'white',
    borderRadius:'8px',
    padding:'7px',
    fontWeight:'500',
    display:'flex',
    alignItems:'center',
    justifyContent:'center'
  }

  const signInInfo = {
    color:'white',
    fontSize:'10px',
    textAlign:'center',
    marginTop:'15px',
    opacity:'0.7'
  }

  const handleSelectionEvent = (data) => {
    setSelectedView(data);
  };

  function signInUser() {
    const github_client_id = "eaaf029abe1165e23c1e";
    window.open(`https://github.com/login/oauth/authorize?scope=user:email&client_id=${github_client_id}`, '_self')
  }

  return (
    <div className="app">
      <Head>
        {/* eslint-disable-next-line @next/next/no-page-custom-font */}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
      </Head>
      {isSignedIn ? <div style={projectStyle}>
        <div style={sideBarStyle}>
          <SideBar onSelectEvent={handleSelectionEvent}/>
        </div>
        <div style={workSpaceStyle}>
          <div style={topBarStyle}>
            <TopBar userName={userName} selectedProject={selectedProject}/>
          </div>
          <div style={contentStyle}>
            <Content selectedView={selectedView} selectedProjectId={selectedProject?.id || ''} userName={userName}/>
          </div>
        </div>
      </div> : <div style={signInStyle}>
        <div style={signInTopBar}>
          <div style={superAgiLogo}><Image width={132} height={72} src="/images/sign-in-logo.svg" alt="super-agi-logo"/></div>
        </div>
        <div style={signInCenter}>
          <div style={signInWrapper}>
            <button style={signInButton} onClick={signInUser}>
              <Image width={20} height={20} src="/images/github.svg" alt="github"/>&nbsp;Continue with Github
            </button>
            <div style={signInInfo}>
              By continuing, you agree to Super AGI’s Terms of Service and Privacy Policy, and to receive important updates.
            </div>
          </div>
        </div>
      </div>}
    </div>
  );
}
