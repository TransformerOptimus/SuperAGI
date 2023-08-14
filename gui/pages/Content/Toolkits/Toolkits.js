import React from 'react';
import Image from "next/image";
import {createInternalId, returnToolkitIcon, excludedToolkits} from "@/utils/utils";

export default function Toolkits({sendToolkitData, toolkits, env}) {
  return (
    <>
      <div className="container">
        <p className="text_14 mt_8 mb_12 ml_8">Toolkits</p>
        {toolkits && toolkits.length > 0 ? (
          <div className="vertical_selection_scroll">
          {toolkits.map((tool, index) =>
              tool.name !== null && !excludedToolkits().includes(tool.name) && (
                <div key={index} className="item_box mb_10" onClick={() => sendToolkitData(tool)}>
                  <div className="row">
                    <div className="col-12">
                      <div className="item_container padding_5">
                         <Image className="image_class bg_black" width={30} height={30}
                             src={returnToolkitIcon(tool.name)}
                             alt="tool-icon"/>
                        <div className="ml_8">
                          <div className="item_name">{tool.name}</div>
                          <div className="item_publisher">by SuperAGI</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )
          )}
          </div>
        ) : (
          <div className="form_label mt_20 horizontal_container justify_center">No Toolkits found</div>
        )}
      </div>
    </>
  );
}
