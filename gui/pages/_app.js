import React, {useState, useEffect} from 'react';
import SideBar from './Dashboard/SideBar';
import Content from './Dashboard/Content';
import TopBar from './Dashboard/TopBar';
import 'bootstrap/dist/css/bootstrap.css';
import './_app.css'
import Head from 'next/head';
import { addUser, getOrganization, getProject } from "@/app/DashboardService";

export default function App() {
  const [selectedView, setSelectedView] = useState('');
  const [userName, setUserName] = useState("");
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

  const handleSelectionEvent = (data) => {
    setSelectedView(data);
  };

  return (
    <div className="app">
      <Head>
        {/* eslint-disable-next-line @next/next/no-page-custom-font */}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
      </Head>
      <div style={projectStyle}>
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
      </div>
    </div>
  );
}
