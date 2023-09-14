import React, {useEffect, useState} from "react";

export default function ModelReadMe({modelDetails}) {
    const [isLoading, setIsLoading] = useState(true)
    const [loadingText, setLoadingText] = useState("Loading ReadMe");

    return (
        <div id="model_readme" className="overflowY_scroll">
            <div className="row">
            </div>
            {isLoading && <div className="loading_container h_75vh"><div className="signInInfo loading_text">{loadingText}</div></div>}
        </div>
    )
}