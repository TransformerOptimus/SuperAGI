import React, {useState, useEffect} from 'react';
import KnowledgeForm from "@/pages/Content/Knowledge/KnowledgeForm";

export default function AddKnowledge({internalId, sendKnowledgeData}) {
  const [knowledgeName, setKnowledgeName] = useState('');
  const [knowledgeDescription, setKnowledgeDescription] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(null);

  useEffect(() => {
    const knowledge_name = localStorage.getItem("knowledge_name_" + String(internalId))
    if (knowledge_name) {
      setKnowledgeName(knowledge_name);
    }

    const knowledge_description = localStorage.getItem("knowledge_description_" + String(internalId))
    if (knowledge_description) {
      setKnowledgeDescription(knowledge_description);
    }

    const knowledge_index = localStorage.getItem("knowledge_index_" + String(internalId))
    if (knowledge_index) {
      setSelectedIndex(JSON.parse(knowledge_index));
    }
  }, [internalId])

  return (<>
    <div className="row">
      <div className="col-3"></div>
      <div className="col-6 col-6-scrollable">
        <KnowledgeForm internalId={internalId}
                       knowledgeId={null}
                       knowledgeName={knowledgeName}
                       setKnowledgeName={setKnowledgeName}
                       knowledgeDescription={knowledgeDescription}
                       setKnowledgeDescription={setKnowledgeDescription}
                       selectedIndex={selectedIndex}
                       setSelectedIndex={setSelectedIndex}
                       isEditing={false}
                       setIsEditing={null}
                       sendKnowledgeData={sendKnowledgeData}
        />
      </div>
      <div className="col-3"></div>
    </div>
  </>)
}