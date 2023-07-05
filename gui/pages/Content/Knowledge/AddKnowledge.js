import React from 'react';
import styles1 from '../Agents/Agents.module.css'
import {removeTab, setLocalStorageValue} from "@/utils/utils";
import {ToastContainer, toast} from "react-toastify";

export default function AddKnowledge({internalId}) {
  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6" style={{overflowY:'scroll',height:'calc(100vh - 92px)',padding:'25px 20px'}}>
        <div>
          <div className={styles1.page_title}>Add a new knowledge</div>
        </div>
        <div style={{marginTop:'10px'}}>
          <div>
            <label className={styles1.form_label}>Github Repository URL</label><br/>
            <label className={styles1.form_label}>Paste your toolkits Github repo url here and we will sync & install</label>
            <input placeholder="Enter URL here" className="input_medium" type="text" value={githubURL} onChange={handleURLChange}/>
          </div>
          <div style={{marginTop: '15px', display: 'flex', justifyContent: 'flex-end'}}>
            <button style={{marginRight:'7px'}} className="secondary_button" onClick={() => removeTab(-2, "new tool", "Add_Toolkit")}>Cancel</button>
            <button disabled={!addClickable} className="primary_button" onClick={handleAddTool}>Add tool</button>
          </div>
        </div>
      </div>
      <div className="col-3"></div>
    </div>
    <ToastContainer/>
  </>)
}