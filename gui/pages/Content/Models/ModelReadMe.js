import React, {useEffect, useState} from "react";
import {fetchModelReadme} from "@/pages/api/DashboardService";
import Image from "next/image";

export default function ModelReadMe({modelDetails}) {
    const [isLoading, setIsLoading] = useState(true)
    const [loadingText, setLoadingText] = useState("Loading ReadMe")
    const [readmeContent, setReadmeContent] = useState(null)
    const [contentType, setContentType] = useState("python")
    const [allReadmeContent, setAllReadmeContent] = useState(null)

    useEffect(() => {
        fetchAllReadmeContent().then().catch()
    }, [])

    async function fetchAllReadmeContent() {
        const response = await fetchModelReadme(modelDetails.id);
        if(response) {
            setAllReadmeContent(response.data);
            filterReadmeContent(response.data);
        }
    }

    function filterReadmeContent(data) {
        const filteredData = data.filter(item => item.language === contentType);
        setReadmeContent(filteredData);
    }

    async function handleSelection(code_language) {
        setContentType(code_language)
        filterReadmeContent(allReadmeContent)
    }

    return (
        <div id="model_readme" className="display_column_container overflowY_scroll color_white">
            <div className="horizontal_container gap_4 pb_8 bb_white">
                <button className={contentType === 'python' ? 'tab_button_selected' : 'tab_button'} onClick={() => handleSelection("python")}>
                    <Image width={18} height={18} src="/images/python_logo.svg" alt="python_logo" />Python</button>
                <button className={contentType === 'javascript' ? 'tab_button_selected' : 'tab_button'} onClick={() => handleSelection("javascript")}>
                    <Image width={18} height={18} src="/images/javascript_logo.svg" alt="javascript_logo" />Javascript</button>
            </div>
            {readmeContent && <div dangerouslySetInnerHTML={{ __html: readmeContent[0].content }} />}
            {/*{isLoading && <div className="loading_container h_75vh"><div className="signInInfo loading_text">{loadingText}</div></div>}*/}
        </div>
    )
}