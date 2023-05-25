import React, {useState} from 'react';
import Image from "next/image";
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles from './Tool.module.css';
import styles1 from '../Agents/Agents.module.css'

export default function ToolCreate({tool,addNewTool}) {
  const goalsArray = ['agent goal 1', 'agent goal 2', 'agent goal 3']
  const [goals, setGoals] = useState(goalsArray);
  const [toolName, setToolName] = useState(tool.name);

  const handleNameChange = (event) => {
    setToolName(event.target.value);
  };
  return (<>
    <div>
      <div className="row" style={{padding: '10px'}}>
        <div className="col-12">
          <div>
            <div className={styles1.page_title} style={{marginTop:'10px'}}>Create new tool</div>
          </div>
          <div style={{marginTop:'10px'}}>
            <div>
              <label className={styles1.form_label}>Name</label>
              <input className="input_medium" type="text" value={toolName} onChange={handleNameChange} />
            </div>
            <div style={{marginTop: '15px'}}>
              <label className={styles1.form_label}>Description</label>
              <textarea className="textarea_medium" rows={3} value={toolName} onChange={handleNameChange} />
            </div>
            <div style={{marginTop: '15px'}}>
              <label className={styles1.form_label}>Input values</label>
              {goals.map((goal, index) => (<div key={index} style={{marginBottom:'10px',display:'flex',alignItems:'center',justifyContent:'space-between'}}>
                <div style={{flex:'1'}}><input className="input_medium" type="text" value={goal} onChange={handleNameChange} /></div>
                <div>
                  <button className={styles1.agent_button} style={{marginLeft:'4px',padding:'5px'}} onClick={handleNameChange} >
                    <Image width={20} height={21} src="/images/close_light.png" alt="close-icon"/>
                  </button>
                </div>
              </div>))}
              <button className={styles1.agent_button} onClick={addNewTool}>
                Add
              </button>
            </div>
          </div>
    </div>
      </div>
    </div>
    <ToastContainer/>
  </>)
}