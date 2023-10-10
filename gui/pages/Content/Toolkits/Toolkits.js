import React from 'react';
import Image from "next/image";
import {createInternalId, returnToolkitIcon, excludedToolkits} from "@/utils/utils";

export default function Toolkits({sendToolkitData, toolkits, env, not_configured_toolkits}) {
  return (
    <>
      <div className="container">
        <p className="text_14 mt_8 mb_12 ml_8">Toolkits</p>
        {env !== 'PROD' && <div className="w_100 mb_10">
          <button className="secondary_button w_100" onClick={() => sendToolkitData({
            id: -2,
            name: "new tool",
            contentType: "Add_Toolkit",
            internalId: createInternalId()
          })}>
            + Add Tool
          </button>
        </div>}
        {toolkits && toolkits.length > 0 ? (
          <div className={`${env === "PROD" ? 'h_calc_add40' : 'h_80vh'} overflowY_scroll`}>
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
                          <div className="flex-row">
                            <div className="item_publisher">by SuperAGI</div>
                              {env === 'DEV' && not_configured_toolkits.some(nc_tool => nc_tool.name === tool.name) &&
                              <div className="tooltip-container ml_8">
                                <Image width={16} height={16} src="/images/icon_error.svg" alt="error-icon" />
                                <span className="tooltip-text">Toolkit is not configured. Please configure now.</span>
                              </div>
                              }
                          </div>
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