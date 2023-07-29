import React from 'react';
import Image from "next/image";
import 'react-toastify/dist/ReactToastify.css';
import {createInternalId} from "@/utils/utils";

export default function Agents({sendAgentData, agents}) {
  return (<>
      <div className="container">
        <p className="text_14 mt_8 mb_12 ml_8">Agents</p>
        <div className="w_100 mb_10">
          <button className="secondary_button w_100" onClick={() => sendAgentData({
            id: -1,
            name: "new agent",
            contentType: "Create_Agent",
            internalId: createInternalId()
          })}>
            + Create Agent
          </button>
        </div>

        {agents && agents.length > 0 ? <div className="vertical_selection_scroll w_100">
          {agents.map((agent, index) => (
            <div key={index}>
              <div className="agent_box w_100" onClick={() => sendAgentData(agent)}>
                {agent?.is_running && <Image width={14} height={14} className="mix_blend_mode" src="/images/loading.gif" alt="active-icon"/>}
                <div className="text_ellipsis"><span className="agent_text text_ellipsis">{agent.name}</span></div>
                {agent?.is_scheduled && <Image className="ml_4" width={17} height={17} src="/images/event_repeat.svg" alt="check-icon"/>}
              </div>
            </div>
          ))}
        </div> : <div className="form_label mt_20 horizontal_container justify_center">No Agents found</div>}
      </div>
    </>
  );
}
