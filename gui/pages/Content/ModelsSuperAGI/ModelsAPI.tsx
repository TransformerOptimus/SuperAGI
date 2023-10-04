import React, {useState, useRef, useContext} from "react";
import Image from "next/image";
// import imagePath from "@/app/pages/imagePath";
// import ThemeContext from "@/app/ThemeContext";
import {ApiDocumentation} from "@/app/pages/Types/ModelsTypes";

export default function ModelsAPI({api_documentation}: {api_documentation: ApiDocumentation}) {
    const textRefs = useRef([]);
    // const context = useContext(ThemeContext);
    const [isHovered, setIsHovered] = useState(false);

    // if (!context) {
    //     throw new Error("ThemeContext is undefined");
    // }
    //
    // const { theme, toggleTheme } = context;

    const handleCopy = async (index: number) => {
        try {
            // @ts-ignore
            await navigator.clipboard.writeText(textRefs.current[index].textContent);
            alert("Text copied to clipboard");
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
    };

    const apiData = [
        {text: 'First, copy your API token and authenticate by setting it as an environment variable', value: 'export SUPERAGI_API_TOKEN=*************************************'},
        {text: 'Then, call the HTTP API directly with cURL:', value: api_documentation.curl_example}
    ]

    return (
        <div id="models_api">
            {apiData.map((data, index) => {

                return (
                    <div key={index}>
                        <span className="text_14 text_color mt_24">{data.text}</span>
                        <div className="output_field_fit space_mono mt_16 mb_16"
                             onMouseEnter={() => setIsHovered(true)}
                             onMouseLeave={() => setIsHovered(false)}
                            // @ts-ignore
                             ref={el => textRefs.current[index] = el}
                             style={{position: 'relative'}}>
                            {isHovered && (
                                <div className="copy_image" onClick={() => handleCopy(index)}>
                                    <Image src={imagePath.copyIconLight}
                                           alt="copy" width={16} height={16} />
                                </div>
                            )}
                            {data.value}
                        </div>
                    </div>
                )
            })}
        </div>
    )
}