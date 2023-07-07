import React, {useState, useEffect} from 'react';
import KnowledgeForm from "@/pages/Content/Knowledge/KnowledgeForm";

export default function AddKnowledge({internalId}) {
  const [knowledgeName, setKnowledgeName] = useState('');
  const [knowledgeDescription, setKnowledgeDescription] = useState('');
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

  useEffect(() => {
    const knowledge_name = localStorage.getItem("knowledge_name_" + String(internalId))
    if(knowledge_name) {
      setKnowledgeName(knowledge_name);
    }

    const knowledge_description = localStorage.getItem("knowledge_description_" + String(internalId))
    if(knowledge_description) {
      setKnowledgeDescription(knowledge_description);
    }

    const knowledge_index = localStorage.getItem("knowledge_index_" + String(internalId))
    if(knowledge_index) {
      setSelectedIndex(knowledge_index);
    }
  }, [internalId])

  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6" style={{overflowY:'scroll',height:'calc(100vh - 92px)',padding:'25px 20px'}}>
        <KnowledgeForm internalId={internalId}
                       collections={collections}
                       knowledgeName={knowledgeName}
                       setKnowledgeName={setKnowledgeName}
                       knowledgeDescription={knowledgeDescription}
                       setKnowledgeDescription={setKnowledgeDescription}
                       selectedIndex={selectedIndex}
                       setSelectedIndex={setSelectedIndex}
                       isEditing={false}
                       setIsEditing={null}
        />
      </div>
      <div className="col-3"></div>
    </div>
  </>)
}