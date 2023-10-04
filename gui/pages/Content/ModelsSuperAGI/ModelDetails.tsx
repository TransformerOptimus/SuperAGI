import React, { useState, useContext, useEffect } from "react";
import Image from "next/image";
// import imagePath from "@/app/pages/imagePath";
// import ThemeContext from "@/app/ThemeContext";
import { ModelDetail, SetIsModelSelected } from "@/app/pages/Types/ModelsTypes";
import ModelsPlayground from "./ModelsPlayground";
import ModelsAPI from "./ModelsAPI";
import ModelsAbout from "./ModelsAbout";

export default function ModelDetails({ modelDetails, setIsModelSelected }: { modelDetails: ModelDetail, setIsModelSelected: SetIsModelSelected }) {
    const [selectedTab, setSelectedTab] = useState('playground');
    const context = useContext(ThemeContext);

    if (!context) {
        throw new Error("ThemeContext is undefined");
    }

    const { theme } = context;

    const tabs = [
        { key: 'playground', label: 'Playground', icon: 'joystick' },
        { key: 'api', label: 'API', icon: 'api' },
        { key: 'about', label: 'About', icon: 'about' },
    ];

    const handleTabClick = (tabKey: string) => {
        setSelectedTab(tabKey);
    };

	useEffect(() => {
		window.scrollTo(0, 0);
	}, []);

	// @ts-ignore
	return (
        <div id="model_details_page" className="vertical_container">
			<div className="horizontal_container gap_4 mb_16 cursor-pointer" // @ts-ignore
				 onClick={() => setIsModelSelected(false)}>
				<Image width={18} height={18}
					   src={theme === 'light' ? imagePath.backArrowLight : imagePath.backArrowDark} alt="back_arrow" />
				<span className="text_14 fw_400 text_color">Back</span>
			</div>
            <div className="horizontal_container gap_16 w-full">
                <Image src={modelDetails.image_link} alt={modelDetails.name} layout="fixed" width={118} height={94} />
                <div className="vertical_container w-full">
                    <span className="text_20 fw_500 text_color">{modelDetails.name}</span>
                    <div className="horizontal_container text_14 text_color_secondary mt_6">
                        <Image src={theme === 'light' ? imagePath.boltLight : imagePath.boltDark} alt="bolt_icon" width={16} height={16} />
                        <span>35.5k runs</span>
                    </div>
                    <span className="text_14 text_color mt_24">{modelDetails.description}</span>
                </div>
            </div>

            <div className="mt_24 border_bottom">
                <div className="horizontal_container gap_16">
                    {tabs.map((tab) => (
                        <div key={tab.key} className={selectedTab === tab.key ? 'model_tab_option_selected' : 'model_tab_option'}
                             onClick={() => handleTabClick(tab.key)}>
                            {selectedTab === tab.key ?
								// @ts-ignore
                                <Image src={theme === 'light' ? imagePath[`${tab.icon}LightSelected`] : imagePath[`${tab.icon}DarkSelected`]} alt={`${tab.key}_icon`} width={16} height={16} /> :
								// @ts-ignore
                                <Image src={theme === 'light' ? imagePath[`${tab.icon}LightUnselected`] : imagePath[`${tab.icon}DarkUnselected`]} alt={`${tab.key}_icon`} width={16} height={16} />}
                            <span>{tab.label}</span>
                        </div>
                    ))}
                </div>
            </div>

            <div className="mt_24">
                {selectedTab === 'playground' && <ModelsPlayground modelDetails={modelDetails}/>}
                {selectedTab === 'api' && // @ts-ignore
					<ModelsAPI api_documentation={modelDetails.api_documentation}/>}
                {selectedTab === 'about' && <ModelsAbout about_data={modelDetails.about}/>}
            </div>
        </div>
    );

}
