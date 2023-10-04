import React, {useContext, useState} from "react";
import Image from "next/image";
import imagePath from "@/app/pages/imagePath";
import {ModelLog} from "@/app/pages/Types/LogsTypes";
import ThemeContext from "@/app/ThemeContext";

export default function ModelsOutputPlayground({result, logs}: {result: String, logs: ModelLog[]}) {
	const [showLogs, setShowLogs] = useState(false)
	const context = useContext(ThemeContext);

	if (!context) {
		throw new Error("ThemeContext is undefined");
	}

	const { theme } = context;

	function toggleLogs () {
		setShowLogs(!showLogs)
	}

    return (
        <div id="models_output_playground">
            <div className="output_field text_14 text_color mt_24" dangerouslySetInnerHTML={{ __html: result.replace(/\n/g, '<br />') }}/>
            <div className="mt_24">
				<div onClick={() => toggleLogs()} className="horizontal_container gap_8 cursor-pointer">
					<Image width={12} height={12} src={showLogs ? (theme === 'light' ? imagePath.logsOpenLight : imagePath.logsOpenDark) : (theme === 'light' ? imagePath.logsClosedLight : imagePath.logsClosedDark)} alt="down_arrow" />
					<span className="text_12 text_color underline">Show Logs</span>
				</div>
				{showLogs ?
					<div className="output_field mt_8">
						{ logs.slice().reverse().map((log, index) => (
							<div className="horizontal_container gap_16 text_12 mb_8" key={index}>
								<span className="text_log flex-none">24 July 2023</span>
								<div className="vertical_divider" />
								<span className="text_error">{log.status === 'FAILURE' ? 'ERROR' : 'SUCCESS'}</span>
								<div className="vertical_divider" />
								<span className="text_color">{log.text}</span>
							</div>
						))}
					</div> : null }
            </div>
        </div>
    )
}
