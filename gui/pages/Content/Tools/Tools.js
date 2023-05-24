import React, {useState} from 'react';
import ToolList from './ToolList';
import ToolCreate from './ToolCreate';

export default function Tools() {
  const [sectionSelected, setSelection] = useState('list_tool');

  const handleSelectionEvent = (data) => {
    setSelection(data)
  };

  return (
    <>
      {/*{sectionSelected === 'list_tool' && <ToolList onSelectEvent={handleSelectionEvent} />}*/}
      {/*{sectionSelected === 'create_tool' && <ToolCreate onSelectEvent={handleSelectionEvent}/>}*/}
    </>
  );
}
