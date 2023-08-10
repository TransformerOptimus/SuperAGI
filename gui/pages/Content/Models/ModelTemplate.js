import React, {useEffect, useState} from 'react';
import Image from "next/image";

export default function ModelTemplate({env, template}){
    const [isInstalled, setIsInstalled] = useState(false);

    return (
        <div id="model_template">
            <div className="color_white">hello</div>
        </div>
    )
}