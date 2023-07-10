import React, {useState} from 'react';
import styles1 from './Knowledge.module.css'
import {ToastContainer, toast} from "react-toastify";
import styles from "@/pages/Content/Toolkits/Tool.module.css";
import Image from "next/image";
import KnowledgeForm from "@/pages/Content/Knowledge/KnowledgeForm";

export default function KnowledgeDetails({internalId, knowledgeDetails}) {
  const [showDescription,setShowDescription] = useState(false);
  const [dropdown,setDropdown] = useState(false);
  const [isEditing,setIsEditing] = useState(false);

  const [knowledgeName, setKnowledgeName] = useState(knowledgeDetails.name || '');
  const [knowledgeDescription, setKnowledgeDescription] = useState(knowledgeDetails.description || '');
  const collections = [
    {
      name: 'database name • Pinecone',
      indices: ['index name 1', 'index name 2', 'index name 3']
    },
    {
      name: 'database name • Qdrant',
      indices: ['index name 4', 'index name 5']
    }
  ];
  const [selectedIndex, setSelectedIndex] = useState(collections[0].indices[0]);

  const uninstallKnowledge = () => {
    setDropdown(false);
  }

  const viewKnowledge = () => {
    setDropdown(false);
  }

  const editKnowledge = () => {
    setIsEditing(true);
    setDropdown(false);
  }

  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6" style={{overflowY:'scroll',height:'calc(100vh - 92px)',padding:'25px 20px'}}>
        {isEditing ?
        <KnowledgeForm internalId={internalId}
                       knowledgeName={knowledgeName}
                       setKnowledgeName={setKnowledgeName}
                       knowledgeDescription={knowledgeDescription}
                       setKnowledgeDescription={setKnowledgeDescription}
                       selectedIndex={selectedIndex}
                       setSelectedIndex={setSelectedIndex}
                       collections={collections}
                       isEditing={true}
                       setIsEditing={setIsEditing}
        /> :
        <div>
          <div className={styles.tools_container}>
            <div className={styles1.knowledge_wrapper} style={{width:'95%'}}>
              <div style={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                <div style={{ textAlign:'left', paddingRight:'10px', width: '95%' }}>
                  <div style={{fontSize:'17px',marginTop:'-3px'}}>{knowledgeName}</div>
                  <div className={styles.toolkit_description} style={!showDescription ? { overflow: 'hidden' } : {display:'block'}}>
                    {`${showDescription ? knowledgeDescription : knowledgeDescription.slice(0, 70)}`}
                    {knowledgeDescription.length > 70 && <span className={styles.show_more_button} onClick={() => setShowDescription(!showDescription)}>
                        {showDescription ? '...less' : '...more'}
                    </span>}
                  </div>
                </div>
              </div>
              <div style={{width:'5%'}}>
                <button className="secondary_button" style={{padding:'8px',height:'31px'}} onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
                  <Image width={14} height={14} src="/images/three_dots.svg" alt="run-icon"/>
                </button>
                {dropdown && <div onMouseEnter={() => setDropdown(true)} onMouseLeave={() => setDropdown(false)}>
                  <ul className="dropdown_container" style={{marginTop:'0',marginLeft:'-10px',width:'165px'}}>
                    {knowledgeDetails.source === 'Marketplace' ?
                      <li className="dropdown_item" onClick={viewKnowledge}>View in marketplace</li> :
                      <li className="dropdown_item" onClick={editKnowledge}>Edit details</li>}
                    <li className="dropdown_item" onClick={uninstallKnowledge}>Uninstall knowledge</li>
                  </ul>
                </div>}
              </div>
            </div>
          </div>
          {knowledgeDetails.source === 'Marketplace' && <div className={styles1.knowledge_wrapper} style={{width:'100%'}}>
            <div style={{width:'50%'}}>
              <div className={styles1.knowledge_info_box}>
                <label className={styles1.knowledge_label}>Installation Type</label>
                <div className={styles1.knowledge_info}>{knowledgeDetails.source}</div>
              </div>
              <div className={styles1.knowledge_info_box}>
                <label className={styles1.knowledge_label}>Model</label>
                <div className={styles1.knowledge_info}>text-embedding-ada-002</div>
              </div>
              <div className={styles1.knowledge_info_box}>
                <label className={styles1.knowledge_label}>Tokenizer</label>
                <div className={styles1.knowledge_info}>Tiktoken</div>
              </div>
              <div className={styles1.knowledge_info_box}>
                <label className={styles1.knowledge_label}>Chunk Size</label>
                <div className={styles1.knowledge_info}>256</div>
              </div>
              <div className={styles1.knowledge_info_box}>
                <label className={styles1.knowledge_label}>Vector Database</label>
                <div className={styles1.knowledge_info}>database name • Pinecone</div>
              </div>
            </div>
            <div style={{width:'50%'}}>
              <div className={styles1.knowledge_info_box}>
                <label className={styles1.knowledge_label}>Knowledge datatype</label>
                <div className={styles1.knowledge_info}>Text</div>
              </div>
              <div className={styles1.knowledge_info_box}>
                <label className={styles1.knowledge_label}>Text splitters</label>
                <div className={styles1.knowledge_info}>Fixed size</div>
              </div>
              <div className={styles1.knowledge_info_box}>
                <label className={styles1.knowledge_label}>Chunk overlap</label>
                <div className={styles1.knowledge_info}>20</div>
              </div>
              <div className={styles1.knowledge_info_box}>
                <label className={styles1.knowledge_label}>Dimension</label>
                <div className={styles1.knowledge_info}>1536</div>
              </div>
              <div className={styles1.knowledge_info_box}>
                <label className={styles1.knowledge_label}>Vector database index</label>
                <div className={styles1.knowledge_info}>index name</div>
              </div>
            </div>
          </div>}
          {knowledgeDetails.source === 'Custom' && <div className={styles1.knowledge_wrapper}>
            <div style={{width:'50%'}}>
              <div className={styles1.knowledge_info_box}>
                <label className={styles1.knowledge_label}>Installation Type</label>
                <div className={styles1.knowledge_info}>{knowledgeDetails.source}</div>
              </div>
              <div className={styles1.knowledge_info_box}>
                <label className={styles1.knowledge_label}>Vector database index</label>
                <div className={styles1.knowledge_info}>{selectedIndex}</div>
              </div>
            </div>
            <div style={{width:'50%'}}>
              <div className={styles1.knowledge_info_box}>
                <label className={styles1.knowledge_label}>Vector Database</label>
                <div className={styles1.knowledge_info}>database name • Pinecone</div>
              </div>
            </div>
          </div>}
        </div>}
      </div>
      <div className="col-3"></div>
    </div>
    <ToastContainer/>
  </>);
}