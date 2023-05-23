import React, {useState} from 'react';
import SideBar from './Dashboard/SideBar';
import Content from './Dashboard/Content';
import TopBar from './Dashboard/TopBar';
import 'bootstrap/dist/css/bootstrap.css';
import './_app.css'
import Head from 'next/head';

export default function App() {
  let [selectedView, setSelectedView] = useState('agents')

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
    overflowY: 'scroll'
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
    setSelectedView(data)
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
            <TopBar/>
          </div>
          <div style={contentStyle}>
            <Content selectedView={selectedView}/>
          </div>
        </div>
      </div>
    </div>
  );
}
