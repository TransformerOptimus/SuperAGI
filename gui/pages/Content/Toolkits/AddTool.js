import React, {useState, useEffect} from 'react';
import {addTool} from "@/pages/api/DashboardService";
import styles1 from '../Agents/Agents.module.css'
import {removeTab, setLocalStorageValue} from "@/utils/utils";
import {ToastContainer, toast} from "react-toastify";

export default function AddTool({internalId}) {
  const [githubURL, setGithubURl] = useState('');
  const [addClickable, setAddClickable] = useState(true);

  const handleURLChange = (event) => {
    setLocalStorageValue("tool_github_" + String(internalId), event.target.value, setGithubURl);
  };

  const handleAddTool = () => {
    if (githubURL.replace(/\s/g, '') === '') {
      toast.error("Github URL can't be blank", {autoClose: 1800});
      return
    }

    setAddClickable(false);

    const toolData = {
      "github_link": githubURL
    }

    addTool(toolData)
      .then((response) => {
        if (response.status === 200) {
          toast.success('Tool will be installed in a while', { autoClose: 1800 });
          setAddClickable(true);
          setLocalStorageValue("tool_github_" + String(internalId), '', setGithubURl);
        }
      })
      .catch((error) => {
        if (error.response && error.response.status === 400) {
          console.error('Error adding tool:', error);
          toast.error('Invalid Github URL', { autoClose: 1800 });
        } else {
          console.error('Error adding tool:', error);
          toast.error(error.message, { autoClose: 1800 });
        }
        setAddClickable(true);
        setLocalStorageValue("tool_github_" + String(internalId), '', setGithubURl);
      });

  };

  useEffect(() => {
    if(internalId !== null) {
      const github_url = localStorage.getItem("tool_github_" + String(internalId))
      if(github_url) {
        setGithubURl(github_url);
      }
    }
  }, [internalId])

  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6" style={{overflowY:'scroll',height:'calc(100vh - 92px)',padding:'25px 20px'}}>
        <div>
          <div className={styles1.page_title}>Add a new tool</div>
        </div>
        <div style={{marginTop:'10px'}}>
          <div>
            <label className={styles1.form_label}>Github Repository URL</label><br/>
            <label className={styles1.form_label}>Paste your toolkits Github repo url here and we will sync & install</label>
            <input placeholder="Enter URL here" className="input_medium" type="text" value={githubURL} onChange={handleURLChange}/>
          </div>
          <div style={{marginTop: '15px', display: 'flex', justifyContent: 'flex-end'}}>
            <button style={{marginRight:'7px'}} className="secondary_button" onClick={() => removeTab(-2, "new tool", "Add_Toolkit", internalId)}>Cancel</button>
            <button disabled={!addClickable} className="primary_button" onClick={handleAddTool}>Add tool</button>
          </div>
        </div>
      </div>
      <div className="col-3"></div>
    </div>
    <ToastContainer/>
  </>)
}