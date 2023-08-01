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
          toast.success('Tool will be installed in a while', {autoClose: 1800});
          setAddClickable(true);
          setLocalStorageValue("tool_github_" + String(internalId), '', setGithubURl);
        }
      })
      .catch((error) => {
        if (error.response && error.response.status === 400) {
          console.error('Error adding tool:', error);
          toast.error('Invalid Github URL', {autoClose: 1800});
        } else {
          console.error('Error adding tool:', error);
          toast.error(error.message, {autoClose: 1800});
        }
        setAddClickable(true);
        setLocalStorageValue("tool_github_" + String(internalId), '', setGithubURl);
      });

  };

  useEffect(() => {
    if (internalId !== null) {
      const github_url = localStorage.getItem("tool_github_" + String(internalId))
      if (github_url) {
        setGithubURl(github_url);
      }
    }
  }, [internalId])

  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6 col-6-scrollable">
        <div className="page_title mt_10">Add a new tool</div>
        <label className="form_label_13">Github Repository URL</label><br/>
        <label className="form_label_13">Paste your toolkits Github repo url here and we will sync & install</label>
        <input placeholder="Enter URL here" className="input_medium" type="text" value={githubURL} onChange={handleURLChange}/>

        <div className="horizontal_container justify_end mt_14">
          <button className="secondary_button mr_7" onClick={() => removeTab(-2, "new tool", "Add_Toolkit", internalId)}>Cancel
          </button>
          <button disabled={!addClickable} className="primary_button" onClick={handleAddTool}>Add tool</button>
        </div>
      </div>
      <div className="col-3"></div>
    </div>
    <ToastContainer/>
  </>)
}