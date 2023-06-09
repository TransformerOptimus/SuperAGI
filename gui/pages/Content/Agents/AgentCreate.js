import React, { useState, useEffect, useRef } from 'react';
import Image from "next/image";
import {ToastContainer, toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import styles from './Agents.module.css';
import {createAgent, getOrganisationConfig, uploadFile} from "@/pages/api/DashboardService";
import {formatBytes} from "@/utils/utils";
import {EventBus} from "@/utils/eventBus";

export default function AgentCreate({sendAgentData, selectedProjectId, fetchAgents, tools, organisationId}) {
  const [advancedOptions, setAdvancedOptions] = useState(false);
  const [agentName, setAgentName] = useState("");
  const [agentDescription, setAgentDescription] = useState("");
  const [selfEvaluation, setSelfEvaluation] = useState('');
  const [basePrompt, setBasePrompt] = useState('');
  const [longTermMemory, setLongTermMemory] = useState(true);
  const [addResources, setAddResources] = useState(true);
  const [input, setInput] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [createClickable, setCreateClickable] = useState(true);
  const fileInputRef = useRef(null);
  const pdf_icon = '/images/pdf_file.svg';
  const txt_icon = '/images/txt_file.svg';
  const img_icon = '/images/img_file.svg';
  const [maxIterations, setIterations] = useState(25);

  const constraintsArray = [
    "If you are unsure how you previously did something or want to recall past events, thinking about similar events will help you remember.",
    'Exclusively use the commands listed in double quotes e.g. "command name"'
  ];
  const [constraints, setConstraints] = useState(constraintsArray);

  const [goals, setGoals] = useState(['Describe the agent goals here']);

  const models = ['gpt-4', 'gpt-3.5-turbo']
  const [model, setModel] = useState(models[1]);
  const modelRef = useRef(null);
  const [modelDropdown, setModelDropdown] = useState(false);

  const agentTypes = ["Don't Maintain Task Queue", "Maintain Task Queue"]
  const [agentType, setAgentType] = useState(agentTypes[0]);
  const agentRef = useRef(null);
  const [agentDropdown, setAgentDropdown] = useState(false);

  const exitCriteria = ["No exit criterion", "System defined", "User defined", "Number of steps/tasks"]
  const [exitCriterion, setExitCriterion] = useState(exitCriteria[0]);
  const exitRef = useRef(null);
  const [exitDropdown, setExitDropdown] = useState(false);

  const [stepTime, setStepTime] = useState(500);

  const rollingWindows = ["5", "10", "15", "20"]
  const [rollingWindow, setRollingWindow] = useState(rollingWindows[1]);
  const rollingRef = useRef(null);
  const [rollingDropdown, setRollingDropdown] = useState(false);

  const databases = ["Pinecone"]
  const [database, setDatabase] = useState(databases[0]);
  const databaseRef = useRef(null);
  const [databaseDropdown, setDatabaseDropdown] = useState(false);

  const permissions = ["God Mode"]
  const [permission, setPermission] = useState(permissions[0]);
  const permissionRef = useRef(null);
  const [permissionDropdown, setPermissionDropdown] = useState(false);

  const [myTools, setMyTools] = useState([]);
  const [toolNames, setToolNames] = useState(['GoogleSearch', 'Read File', 'Write File']);
  const toolRef = useRef(null);
  const [toolDropdown, setToolDropdown] = useState(false);

  const excludedTools = ["ThinkingTool", "LlmThinkingTool", "Human", "ReasoningTool"];
  const [hasAPIkey, setHasAPIkey] = useState(false);

  useEffect(() => {
    getOrganisationConfig(organisationId, "model_api_key")
      .then((response) => {
        const apiKey = response.data.value
        setHasAPIkey(!(apiKey === null || apiKey.replace(/\s/g, '') === ''));
      })
      .catch((error) => {
        console.error('Error fetching project:', error);
      });
  }, [organisationId]);

  const filterToolsByNames = () => {
    if(tools) {
      const filteredTools = tools.filter((tool) => toolNames.includes(tool.name));
      const toolIds = filteredTools.map((tool) => tool.id);
      setMyTools(toolIds);
    }
  };

  const handleIterationChange = (event) => {
    setIterations(parseInt(event.target.value));
  };

  useEffect(() => {
    filterToolsByNames();
  }, [toolNames]);

  useEffect(() => {
    function handleClickOutside(event) {
      if (modelRef.current && !modelRef.current.contains(event.target)) {
        setModelDropdown(false)
      }

      if (agentRef.current && !agentRef.current.contains(event.target)) {
        setAgentDropdown(false)
      }

      if (exitRef.current && !exitRef.current.contains(event.target)) {
        setExitDropdown(false)
      }

      if (rollingRef.current && !rollingRef.current.contains(event.target)) {
        setRollingDropdown(false)
      }

      if (databaseRef.current && !databaseRef.current.contains(event.target)) {
        setDatabaseDropdown(false)
      }

      if (permissionRef.current && !permissionRef.current.contains(event.target)) {
        setPermissionDropdown(false)
      }

      if (toolRef.current && !toolRef.current.contains(event.target)) {
        setToolDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const addTool = (tool) => {
    if (!myTools.includes(tool.id)) {
      setMyTools((prevArray) => [...prevArray, tool.id]);
      setToolNames((prevArray) => [...prevArray, tool.name]);
    }
  };
  
  const removeTool = (indexToDelete) => {
    setMyTools((prevArray) => {
      const newArray = [...prevArray];
      newArray.splice(indexToDelete, 1);
      return newArray;
    });

    setToolNames((prevArray) => {
      const newArray = [...prevArray];
      newArray.splice(indexToDelete, 1);
      return newArray;
    });
  };

  const handlePermissionSelect = (index) => {
    setPermission(permissions[index]);
    setPermissionDropdown(false);
  };

  const handleDatabaseSelect = (index) => {
    setDatabase(databases[index]);
    setDatabaseDropdown(false);
  };

  const handleWindowSelect = (index) => {
    setRollingWindow(rollingWindows[index]);
    setRollingDropdown(false);
  };

  const handleStepChange = (event) => {
    setStepTime(event.target.value)
  };

  const handleExitSelect = (index) => {
    setExitCriterion(exitCriteria[index]);
    setExitDropdown(false);
  };

  const handleAgentSelect = (index) => {
    setAgentType(agentTypes[index]);
    setAgentDropdown(false);
  };

  const handleModelSelect = (index) => {
    setModel(models[index]);
    setModelDropdown(false);
  };

  const handleGoalChange = (index, newValue) => {
    const updatedGoals = [...goals];
    updatedGoals[index] = newValue;
    setGoals(updatedGoals);
  };

  const handleConstraintChange = (index, newValue) => {
    const updatedConstraints = [...constraints];
    updatedConstraints[index] = newValue;
    setConstraints(updatedConstraints);
  };

  const handleGoalDelete = (index) => {
    const updatedGoals = [...goals];
    updatedGoals.splice(index, 1);
    setGoals(updatedGoals);
  };

  const handleConstraintDelete = (index) => {
    const updatedConstraints = [...constraints];
    updatedConstraints.splice(index, 1);
    setConstraints(updatedConstraints);
  };

  const addGoal = () => {
    setGoals((prevArray) => [...prevArray, 'new goal']);
  };

  const addConstraint = () => {
    setConstraints((prevArray) => [...prevArray, 'new constraint']);
  };

  const handleNameChange = (event) => {
    setAgentName(event.target.value);
  };

  const handleDescriptionChange = (event) => {
    setAgentDescription(event.target.value);
  };

  const handleSelfEvaluationChange = (event) => {
    setSelfEvaluation(event.target.value);
  };

  const handleBasePromptChange = (event) => {
    setBasePrompt(event.target.value);
  };

  const preventDefault = (e) => {
    e.stopPropagation();
  };

  function uploadResource(agentId, fileData) {
    const formData = new FormData();
    formData.append('file', fileData.file);
    formData.append('name', fileData.name);
    formData.append('size', fileData.size);
    formData.append('type', fileData.type);

    return uploadFile(agentId, formData);
  }

  useEffect(() => {
    const keySet = (eventData) => {
      setHasAPIkey(true);
    };

    EventBus.on('keySet', keySet);

    return () => {
      EventBus.off('keySet', keySet);
    };
  });

  const handleAddAgent = () => {
    if(!hasAPIkey) {
      toast.error("Your OpenAI API key is empty!", {autoClose: 1800});
      EventBus.emit("openSettings", {});
      return
    }

    if (agentName.replace(/\s/g, '') === '') {
      toast.error("Agent name can't be blank", {autoClose: 1800});
      return
    }

    if (agentDescription.replace(/\s/g, '') === '') {
      toast.error("Agent description can't be blank", {autoClose: 1800});
      return
    }

    const isEmptyGoal = goals.some((goal) => goal.replace(/\s/g, '') === '');
    if (isEmptyGoal) {
      toast.error("Goal can't be empty", { autoClose: 1800 });
      return;
    }

    if (myTools.length <= 0) {
      toast.error("Add atleast one tool", {autoClose: 1800});
      return
    }

    setCreateClickable(false);

    const agentData = {
      "name": agentName,
      "project_id": selectedProjectId,
      "description": agentDescription,
      "goal": goals,
      "agent_type": agentType,
      "constraints": constraints,
      "tools": myTools,
      "exit": exitCriterion,
      "iteration_interval": stepTime,
      "model": model,
      "max_iterations": maxIterations,
      "permission_type": permission,
      "LTM_DB": longTermMemory ? database : null,
      "memory_window": rollingWindow
    };

    createAgent(agentData)
      .then((response) => {
        const agent_id = response.data.id;
        fetchAgents();
        cancelCreate();
        sendAgentData({ id: agent_id, name: response.data.name, contentType: "Agents", execution_id: response.data.execution_id });
        if(addResources) {
          input.forEach((fileData) => {
            input.forEach(fileData => {
              uploadResource(agent_id, fileData)
                .then(response => {})
                .catch(error => {
                  console.error('Error uploading resource:', error);
                });
            });
          });
        }
        toast.success('Agent created successfully', {autoClose: 1800});
        setCreateClickable(true);
      })
      .catch((error) => {
        console.error('Error creating agent:', error);
        setCreateClickable(true);
      });
  };

  function cancelCreate() {
    EventBus.emit('cancelAgentCreate', {});
  }

  const handleFileInputChange = (event) => {
    const files = event.target.files;
    setFileData(files);
  };

  const handleDropAreaClick = () => {
    fileInputRef.current.click();
  };

  const handleDragEnter = (event) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  function setFileData(files) {
    if (files.length > 0) {
      const fileData = {
        "file": files[0],
        "name": files[0].name,
        "size": files[0].size,
        "type": files[0].type,
      };
      setInput((prevArray) => [...prevArray, fileData]);
    }
  }

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    const files = event.dataTransfer.files;
    setFileData(files);
  };

  const removeFile = (index) => {
    const updatedFiles = input.filter((file) => input.indexOf(file) !== index);
    setInput(updatedFiles);
  };

  const ResourceItem = ({ file, index }) => {
    const isPDF = file.type === 'application/pdf';
    const isTXT = file.type === 'application/txt' || file.type === 'text/plain';
    const isIMG = file.type.includes('image');

    return (
      <div className={styles.history_box} style={{ background: '#272335', padding: '0px 10px', width: '100%', cursor: 'default' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-start' }}>
          {isPDF && <div><Image width={28} height={46} src={pdf_icon} alt="pdf-icon" /></div>}
          {isTXT && <div><Image width={28} height={46} src={txt_icon} alt="txt-icon" /></div>}
          {isIMG && <div><Image width={28} height={46} src={img_icon} alt="img-icon" /></div>}
          {!isTXT && !isIMG && !isPDF && <div><Image width={28} height={46} src="/images/default_file.svg" alt="file-icon" /></div>}
          <div style={{ marginLeft: '5px', width:'100%' }}>
            <div style={{ fontSize: '11px' }} className={styles.single_line_block}>{file.name}</div>
            <div style={{ color: '#888888', fontSize: '9px' }}>{file.type.split("/")[1]}{file.size !== '' ? ` • ${formatBytes(file.size)}` : ''}</div>
          </div>
          <div style={{cursor:'pointer'}} onClick={() => removeFile(index)}><Image width={20} height={20} src='/images/close_light.svg' alt="close-icon" /></div>
        </div>
      </div>
    );
  };

  const ResourceList = ({ files }) => (
    <div className={styles.agent_resources}>
      {files.map((file, index) => (
        <ResourceItem key={index} file={file} index={index} />
      ))}
    </div>
  );

  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6" style={{overflowY:'scroll',height:'calc(100vh - 92px)',padding:'25px 20px'}}>
        <div>
          <div className={styles.page_title}>Create new agent</div>
        </div>
        <div style={{marginTop:'10px'}}>
          <div>
            <label className={styles.form_label}>Name</label>
            <input className="input_medium" type="text" value={agentName} onChange={handleNameChange}/>
          </div>
          <div style={{marginTop: '15px'}}>
            <label className={styles.form_label}>Description</label>
            <textarea className="textarea_medium" rows={3} value={agentDescription} onChange={handleDescriptionChange}/>
          </div>
          <div style={{marginTop: '15px'}}>
            <div><label className={styles.form_label}>Goals</label></div>
            {goals.map((goal, index) => (<div key={index} style={{marginBottom:'10px',display:'flex',alignItems:'center',justifyContent:'space-between'}}>
              <div style={{flex:'1'}}><input className="input_medium" type="text" value={goal} onChange={(event) => handleGoalChange(index, event.target.value)}/></div>
              {goals.length > 1 && <div>
                <button className="secondary_button" style={{marginLeft: '4px', padding: '5px'}}
                        onClick={() => handleGoalDelete(index)}>
                  <Image width={20} height={21} src="/images/close_light.svg" alt="close-icon"/>
                </button>
              </div>}
            </div>))}
            <div><button className="secondary_button" onClick={addGoal}>+ Add</button></div>
          </div>
          <div style={{marginTop: '15px'}}>
            <label className={styles.form_label}>Model</label><br/>
            <div className="dropdown_container_search" style={{width:'100%'}}>
                <div className="custom_select_container" onClick={() => setModelDropdown(!modelDropdown)} style={{width:'100%'}}>
                  {model}<Image width={20} height={21} src={!modelDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'} alt="expand-icon"/>
                </div>
                <div>
                  {modelDropdown && <div className="custom_select_options" ref={modelRef} style={{width:'100%'}}>
                  {models.map((model, index) => (<div key={index} className="custom_select_option" onClick={() => handleModelSelect(index)} style={{padding:'12px 14px',maxWidth:'100%'}}>
                    {model}
                  </div>))}
                </div>}
              </div>
            </div>
          </div>
          <div style={{marginTop: '15px'}}>
            <label className={styles.form_label}>Tools</label>
            <div className="dropdown_container_search" style={{width:'100%'}}>
              <div className="custom_select_container" onClick={() => setToolDropdown(!toolDropdown)} style={{width:'100%'}}>
                {toolNames && toolNames.length > 0 ? <div style={{display:'flex',overflowX:'scroll'}}>
                  {toolNames.map((tool, index) => (<div key={index} className="tool_container" style={{marginTop:'0'}} onClick={preventDefault}>
                    <div className={styles.tool_text}>{tool}</div>
                    <div><Image width={12} height={12} src='/images/close_light.svg' alt="close-icon" style={{margin:'-2px -5px 0 2px'}} onClick={() => removeTool(index)}/></div>
                  </div>))}
                </div> : <div style={{color:'#666666'}}>Select Tools</div>}
                <Image width={20} height={21} src={!toolDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'} alt="expand-icon"/>
              </div>
              <div>
                {toolDropdown && <div className="custom_select_options" ref={toolRef} style={{width:'100%'}}>
                  {tools && tools.map((tool, index) => (<div key={index}>
                    {tool.name !== null && !excludedTools.includes(tool.name) && <div className="custom_select_option" onClick={() => addTool(tool)}
                          style={{padding: '12px 14px', maxWidth: '100%'}}>
                      {tool.name}
                    </div>}
                  </div>))}
                </div>}
              </div>
            </div>
          </div>
          <div style={{marginTop: '15px'}}>
            <button className="medium_toggle" onClick={() => setAdvancedOptions(!advancedOptions)} style={advancedOptions ? {background:'#494856'} : {}}>
              {advancedOptions ? 'Hide Advanced Options' : 'Show Advanced Options'}{advancedOptions ? <Image style={{marginLeft:'10px'}} width={20} height={21} src="/images/dropdown_up.svg" alt="expand-icon"/> : <Image style={{marginLeft:'10px'}} width={20} height={21} src="/images/dropdown_down.svg" alt="expand-icon"/>}
            </button>
          </div>
          {advancedOptions &&
            <div>
              <div style={{marginTop: '15px'}}>
                <label className={styles.form_label}>Agent Type</label><br/>
                <div className="dropdown_container_search" style={{width:'100%'}}>
                  <div className="custom_select_container" onClick={() => setAgentDropdown(!agentDropdown)} style={{width:'100%'}}>
                    {agentType}<Image width={20} height={21} src={!agentDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'} alt="expand-icon"/>
                  </div>
                  <div>
                    {agentDropdown && <div className="custom_select_options" ref={agentRef} style={{width:'100%'}}>
                      {agentTypes.map((agent, index) => (<div key={index} className="custom_select_option" onClick={() => handleAgentSelect(index)} style={{padding:'12px 14px',maxWidth:'100%'}}>
                        {agent}
                      </div>))}
                    </div>}
                  </div>
                </div>
              </div>
              {/*<div style={{marginTop: '15px'}}>*/}
              {/*  <label className={styles.form_label}>Base prompt</label><br/>*/}
              {/*  <p className={styles.form_label} style={{fontSize:'11px'}}>This will defined the agent role definitely and reduces hallucination. This will defined the agent role definitely and reduces hallucination.</p>*/}
              {/*  <textarea className="textarea_medium" rows={3} value={basePrompt} onChange={handleBasePromptChange}/>*/}
              {/*</div>*/}
              {/*<div style={{marginTop: '15px'}}>*/}
              {/*  <label className={styles.form_label}>Self Evaluation</label><br/>*/}
              {/*  <p className={styles.form_label} style={{fontSize:'11px'}}>Allows the agent to evaluate and correct themselves as they proceed further.</p>*/}
              {/*  <textarea className="textarea_medium" rows={3} value={selfEvaluation} onChange={handleSelfEvaluationChange}/>*/}
              {/*</div>*/}
              <div style={{marginTop: '15px'}}>
                <div style={{display:'flex'}}>
                  <input className="checkbox" type="checkbox" checked={addResources} onChange={() => setAddResources(!addResources)} />
                  <label className={styles.form_label} style={{marginLeft:'7px',cursor:'pointer'}} onClick={() => setAddResources(!addResources)}>
                    Add Resources
                  </label>
                </div>
              </div>
              <div style={{width:'100%',height:'auto',marginTop:'10px'}}>
                {addResources && <div style={{paddingBottom:'10px'}}>
                  <div className={`file-drop-area ${isDragging ? 'dragging' : ''}`} onDragEnter={handleDragEnter} onDragLeave={handleDragLeave} onDragOver={handleDragOver} onDrop={handleDrop} onClick={handleDropAreaClick}>
                    <div><p style={{textAlign:'center',color:'white',fontSize:'14px'}}>+ Choose or drop a file here</p>
                      <p style={{textAlign:'center',color:'#888888',fontSize:'12px'}}>Supported file format .txt</p>
                      <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileInputChange}/></div>
                  </div>
                  <ResourceList files={input}/>
                </div>}
              </div>
              <div style={{marginTop: '5px'}}>
                <div><label className={styles.form_label}>Constraints</label></div>
                {constraints.map((constraint, index) => (<div key={index} style={{marginBottom:'10px',display:'flex',alignItems:'center',justifyContent:'space-between'}}>
                  <div style={{flex:'1'}}><input className="input_medium" type="text" value={constraint} onChange={(event) => handleConstraintChange(index, event.target.value)}/></div>
                  <div>
                    <button className="secondary_button" style={{marginLeft:'4px',padding:'5px'}} onClick={() => handleConstraintDelete(index)}>
                      <Image width={20} height={21} src="/images/close_light.svg" alt="close-icon"/>
                    </button>
                  </div>
                </div>))}
                <div><button className="secondary_button" onClick={addConstraint}>+ Add</button></div>
              </div>
              <div style={{marginTop:'15px'}}>
                <label className={styles.form_label}>Max iterations</label>
                <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
                  <input style={{width:'90%'}} type="range" min={5} max={100} value={maxIterations} onChange={handleIterationChange}/>
                  <input style={{width:'9%',order:'1',textAlign:'center',paddingLeft:'0',paddingRight:'0'}} disabled={true} className="input_medium" type="text" value={maxIterations}/>
                </div>
              </div>
              {/*<div style={{marginTop: '15px'}}>*/}
              {/*  <label className={styles.form_label}>Exit criterion</label>*/}
              {/*  <div className="dropdown_container_search" style={{width:'100%'}}>*/}
              {/*    <div className="custom_select_container" onClick={() => setExitDropdown(!exitDropdown)} style={{width:'100%'}}>*/}
              {/*      {exitCriterion}<Image width={20} height={21} src={!exitDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'} alt="expand-icon"/>*/}
              {/*    </div>*/}
              {/*    <div>*/}
              {/*      {exitDropdown && <div className="custom_select_options" ref={exitRef} style={{width:'100%'}}>*/}
              {/*        {exitCriteria.map((exit, index) => (<div key={index} className="custom_select_option" onClick={() => handleExitSelect(index)} style={{padding:'12px 14px',maxWidth:'100%'}}>*/}
              {/*          {exit}*/}
              {/*        </div>))}*/}
              {/*      </div>}*/}
              {/*    </div>*/}
              {/*  </div>*/}
              {/*</div>*/}
              <div style={{marginTop: '15px'}}>
                <label className={styles.form_label}>Time between steps (in milliseconds)</label>
                <input className="input_medium" type="number" value={stepTime} onChange={handleStepChange}/>
              </div>
              <div style={{marginTop: '15px'}}>
                <label className={styles.form_label}>Short term memory - Rolling window</label>
                <div className="dropdown_container_search" style={{width:'100%'}}>
                  <div className="custom_select_container" onClick={() => setRollingDropdown(!rollingDropdown)} style={{width:'100%'}}>
                    {rollingWindow} messages<Image width={20} height={21} src={!rollingDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'} alt="expand-icon"/>
                  </div>
                  <div>
                    {rollingDropdown && <div className="custom_select_options" ref={rollingRef} style={{width:'100%'}}>
                      {rollingWindows.map((window, index) => (<div key={index} className="custom_select_option" onClick={() => handleWindowSelect(index)} style={{padding:'12px 14px',maxWidth:'100%'}}>
                        {window}
                      </div>))}
                    </div>}
                  </div>
                </div>
              </div>
              <div style={{marginTop: '15px'}}>
                <div style={{display:'flex'}}>
                  <input className="checkbox" type="checkbox" checked={longTermMemory} onChange={() => setLongTermMemory(!longTermMemory)} />
                  <label className={styles.form_label} style={{marginLeft:'7px',cursor:'pointer'}} onClick={() => setLongTermMemory(!longTermMemory)}>
                    Long term memory
                  </label>
                </div>
              </div>
              {longTermMemory === true && <div style={{marginTop: '10px'}}>
                <label className={styles.form_label}>Choose an LTM database</label>
                <div className="dropdown_container_search" style={{width:'100%'}}>
                  <div className="custom_select_container" onClick={() => setDatabaseDropdown(!databaseDropdown)} style={{width:'100%'}}>
                    {database}<Image width={20} height={21} src={!databaseDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'} alt="expand-icon"/>
                  </div>
                  <div>
                    {databaseDropdown && <div className="custom_select_options" ref={databaseRef} style={{width:'100%'}}>
                      {databases.map((data, index) => (<div key={index} className="custom_select_option" onClick={() => handleDatabaseSelect(index)} style={{padding:'12px 14px',maxWidth:'100%'}}>
                        {data}
                      </div>))}
                    </div>}
                  </div>
                </div>
              </div>}
              <div style={{marginTop: '15px'}}>
                <label className={styles.form_label}>Permission Type</label>
                <div className="dropdown_container_search" style={{width:'100%'}}>
                  <div className="custom_select_container" onClick={() => setPermissionDropdown(!permissionDropdown)} style={{width:'100%'}}>
                    {permission}<Image width={20} height={21} src={!permissionDropdown ? '/images/dropdown_down.svg' : '/images/dropdown_up.svg'} alt="expand-icon"/>
                  </div>
                  <div>
                    {permissionDropdown && <div className="custom_select_options" ref={permissionRef} style={{width:'100%'}}>
                      {permissions.map((permit, index) => (<div key={index} className="custom_select_option" onClick={() => handlePermissionSelect(index)} style={{padding:'12px 14px',maxWidth:'100%'}}>
                        {permit}
                      </div>))}
                    </div>}
                  </div>
                </div>
              </div>
            </div>
          }
          <div style={{marginTop: '15px', display: 'flex', justifyContent: 'flex-end'}}>
            <button style={{marginRight:'7px'}} className="secondary_button" onClick={cancelCreate}>Cancel</button>
            <button disabled={!createClickable} className="primary_button" onClick={handleAddAgent}>Create and Run</button>
          </div>
        </div>
      </div>
      <div className="col-3"></div>
    </div>
    <ToastContainer/>
  </>)
}