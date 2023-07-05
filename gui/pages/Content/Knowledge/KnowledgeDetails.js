import React, {useState} from 'react';
import styles1 from './Knowledge.module.css'
import {ToastContainer, toast} from "react-toastify";
import styles from "@/pages/Content/Toolkits/Tool.module.css";
import Image from "next/image";

export default function KnowledgeDetails({knowledgeDetails}) {
  const [showDescription,setShowDescription] = useState(false)

  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6" style={{overflowY:'scroll',height:'calc(100vh - 92px)',padding:'25px 20px'}}>
        <div className={styles.tools_container}>
          <div className={styles1.knowledge_wrapper} style={{width:'95%'}}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ textAlign:'left', paddingRight:'10px' }}>
                <div style={{fontSize:'17px',marginTop:'-3px'}}>{knowledgeDetails.name}</div>
                <div className={styles.toolkit_description} style={!showDescription ? { overflow: 'hidden' } : {display:'block'}}>
                  {`${showDescription ? knowledgeDetails.description : knowledgeDetails.description.slice(0, 80)}`}
                  {knowledgeDetails.description.length > 80 && <span className={styles.show_more_button} onClick={() => setShowDescription(!showDescription)}>
                      {showDescription ? '...less' : '...more'}
                  </span>}
                </div>
              </div>
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
              <div className={styles1.knowledge_info}>index name</div>
            </div>
          </div>
          <div style={{width:'50%'}}>
            <div className={styles1.knowledge_info_box}>
              <label className={styles1.knowledge_label}>Vector Database</label>
              <div className={styles1.knowledge_info}>database name • Pinecone</div>
            </div>
          </div>
        </div>}
      </div>
      <div className="col-3"></div>
    </div>
    <ToastContainer/>
  </>);
}