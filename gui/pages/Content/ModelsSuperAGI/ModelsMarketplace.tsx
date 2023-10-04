import React, {useEffect, useState} from "react";
import Image from "next/image";
// import imagePath from "@/app/pages/imagePath";
// import ThemeContext from "@/app/ThemeContext";
import ModelsDetails from "./ModelDetails";
import ModelDetails from "./ModelDetails";
import { ModelDetail, SetIsModelSelected } from "@/app/pages/Types/ModelsTypes";
import {getAllModels} from "@/app/api/DashboardService";

export default function ModelsMarketplace () {
	// @ts-ignore
    const [selectedModel, setSelectedModel] = useState<ModelDetail>({image: '', model: '', text: '',})
    const [isModelSelected, setIsModelSelected] = useState(false);
	const [marketplaceModels, setMarketplaceModels] = useState([]);

	useEffect(() => {
		getModels().then().catch()
	}, []);

	async function getModels() {
		const response = await getAllModels();
		if(response) {
			const data = response.data
			setMarketplaceModels(data)
			console.log(data)
		}
	}

    async function modelSelected (index: number) {
        setSelectedModel(marketplaceModels[index])
        setIsModelSelected(true)
    }

    return (
        <div id="models_marketplace" className="w-full">
            {!isModelSelected ? (
                <div>
                    <span className="text_24 fw_500 text_color">Explore Models</span>
                    <div className="marketplaceGrid3 mt_24 pb-6">
                        {marketplaceModels.map((model, index) => (
                            <div className="model_container" key={index} onClick={() => modelSelected(index)}>
                                <div className="model_image_container">
                                    <Image // @ts-ignore
										src={model.image_link} alt={model.name} layout="responsive" width={500} height={145}/>
                                </div>
                                <div className="vertical_container p_16">
                                    <span // @ts-ignore
										className="text_20 fw_500 text_color">{model.name}</span>
                                    <span // @ts-ignore
										className="text_14 fw_500 text_color mt_16 ellipse_1">{model.description}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
				// @ts-ignore
            ) : <ModelDetails modelDetails={selectedModel} setIsModelSelected={setIsModelSelected} />}
        </div>
    );
}
