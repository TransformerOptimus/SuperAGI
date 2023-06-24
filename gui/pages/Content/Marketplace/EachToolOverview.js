import React, {useState} from 'react';
import Image from "next/image";
import styles from '../Tools/Tool.module.css';
import styles1 from '../Agents/Agents.module.css'
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles2 from "./Market.module.css"

export default function EachToolOverview({}) {

    return (
        <>
            <div className={styles2.left_container} style={{overflowY:'scroll',height:'calc(100vh - 92px)'}}>
                <span className={styles2.description_text}>[![Join our Discord Server](https://img.shields.io/badge/Discord-SuperAGI-blueviolet?logo=discord&logoColor=white)](https://discord.gg/dXbRe5BHJC) ° [![Follow us on Twitter](https://img.shields.io/twitter/follow/_superAGI?label=_superAGI&style=social)](https://twitter.com/_superAGI) ° [![Join the discussion on Reddit](https://img.shields.io/reddit/subreddit-subscribers/Super_AGI?label=%2Fr/Super_AGI&style=social)](https://www.reddit.com/r/Super_AGI)</span><br /><br />
                <span className={styles2.description_heading}>🚀 Provision, Spawn &  Deploy Autonomous AI Agents</span> <br />
                <span className={styles2.description_text}>Seamless provision and run agents</span><br /><br />
                <span className={styles2.description_heading}>🛠️ Extend Agent Capabilities with Tools</span> <br />
                <span className={styles2.description_text}>Give capabilities to your agents by selecting tools from growing library or build your own custom tool</span><br /><br />
                <span className={styles2.description_heading}>🔄 Reload Concurrent Agents Seamlessly</span> <br />
                <span className={styles2.description_text}>Run agents concurrently</span><br /><br />
                <span className={styles2.description_heading}>🔒 Open Source</span> <br />
                <span className={styles2.description_text}>SuperAGI is an open-source platform, enabling developers to join a community of contributors constantly working to make it better.</span><br /><br />
                <span className={styles2.description_heading}>🖥️ GUI</span> <br />
                <span className={styles2.description_text}>Access your agents through a user-friendly graphical interface, simplifying agent management and interaction.</span><br /><br />
                <span className={styles2.description_heading}>⌨️ Action Console</span> <br />
                <span className={styles2.description_text}>Interact with agents by providing input, permissions, and more.</span><br /><br />
            </div>

            <ToastContainer/>
        </>
    );
}