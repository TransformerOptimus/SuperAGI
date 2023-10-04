import React, {useContext, useEffect, useState} from "react";
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
// import ThemeContext from "@/app/ThemeContext";
import {DataType, ModelsInputPlaygroundProps, Parameters} from "@/pages/Types/ModelsTypes";
import {getModelLogsById, runModel} from "@/app/api/DashboardService";
import { toast } from 'react-toastify';
import { ToastContainer } from 'react-toastify';

export default function ModelsInputPlayground({data, model_id, setModelResult, setModelLogs}: ModelsInputPlaygroundProps) {
	const parameters: {[key: string]: DataType} = {};
	data && data.forEach(item => {
		if (item.show_in_ui) {
			parameters[item.param_name] = item;
		}
	});

	const [promptValue, setPromptValue] = useState("")
	const [maxTokens, setMaxTokens] = useState(parameters['max_new_tokens'] ? parameters['max_new_tokens'].default_value : "")
	const [topP, setTopP] = useState(parameters['top_p'] ? Number(parameters['top_p'].default_value) : 0)
	const [topK, setTopK] = useState(parameters['top_k'] ? Number(parameters['top_k'].default_value) : 0)
	const [temperature, setTemperature] = useState(parameters['temperature'] ? Number(parameters['temperature'].default_value) : 0)
	const [repetitionPenalty, setRepetitionPenalty] = useState(parameters['repetition_penalty'] ? Number(parameters['repetition_penalty'].default_value) : 0)
	const [stopSequence, setStopSequence] = useState(parameters['stop'] ? parameters['stop'].default_value : "")

	// const context = useContext(ThemeContext);

	// if (!context) {
	// 	throw new Error("ThemeContext is undefined");
	// }

	// const { theme, toggleTheme } = context;

	const handleSliderChange = (setter: React.Dispatch<React.SetStateAction<number>>) => (value: number) => {
		setter(value);
	};

	const trackStyle = false ?
		{ backgroundColor: 'black' } :
		{ backgroundColor: 'white' };

	const handleStyle = false ?
		{ borderColor: 'black', backgroundColor: 'black' } :
		{ borderColor: 'white', backgroundColor: 'white' };

	const railStyle = false ?
		{ backgroundColor: 'gray' } :
		{ backgroundColor: 'rgba(255, 255, 255, 0.10)' };

	useEffect(() => {
		getModelLogs().then().catch()
	}, [])

	async function runModels () {
		// @ts-ignore
		const parameters: Parameters = {};
		data && data.forEach(item => {
			if (item.show_in_ui) {
				switch (item.param_name) {
					case 'max_new_tokens':
						parameters['max_new_tokens'] = Number(maxTokens);
						break;
					case 'top_p':
						parameters['top_p'] = topP;
						break;
					case 'top_k':
						parameters['top_k'] = topK;
						break;
					case 'temperature':
						parameters['temperature'] = temperature;
						break;
					case 'repetition_penalty':
						parameters['repetition_penalty'] = repetitionPenalty;
						break;
					case 'stop':
						parameters['stop'] = [stopSequence];
						break;
					default:
						// @ts-ignore
						parameters[item.param_name] = item.default_value;
				}
			} else {
				// @ts-ignore
				parameters[item.param_name] = item.default_value;
			}
		});

		parameters['best_of'] = 1;
		const config_data = {
			"inputs": promptValue,
			"parameters": parameters
		};
		// @ts-ignore
		const responsePromise = runModel(model_id, config_data);
		toast.promise(responsePromise,
			{pending: 'Running...', success: 'Output Successfully Rendered', error: 'Error while Running the Model'}, {position: toast.POSITION.BOTTOM_RIGHT});
		const response = await responsePromise;
		if(response) {
			const data = response.data
			// @ts-ignore
			setModelResult(data.choices[0].message)
			getModelLogs().then().catch()
		}
	}

	async function getModelLogs () {
		const response = await getModelLogsById(model_id);
		if(response) {
			// @ts-ignore
			setModelLogs(response.data)
		}
	}

	return (
		<div id="models_input_playground">
			<div className="mt_24">
				<span className="text_13 fw_500 text_color">Prompt</span>
				<textarea className="textarea_primary" value={promptValue} placeholder="Enter Value here"
						  onChange={(event) => setPromptValue(event.target.value)} />
				<span className="text_13 text_color_secondary">Prompt to send to the model.</span>
			</div>

			{parameters['max_new_tokens'] &&
				<div className="mt_24">
					<span className="text_13 fw_500 text_color">Max Token</span>
					<input type="number" className="text_field_primary" value={maxTokens} placeholder="Enter Value here"
						// @ts-ignore
						   onChange={(event) => setMaxTokens(parseInt(event.target.value, 10))} />
					<span className="text_13 text_color_secondary">The maximum length in tokens to be used for the output.</span>
				</div>}

			{parameters['top_p'] && (
				<div className="mt_24">
					<span className="text_13 fw_500 text_color">Top P</span>
					<div className="horizontal_container items-center gap_8 w-full">
						<input type="number" min="0" max="1" step="0.01" className="text_field_primary" style={{width: '10%'}}
							   value={topP} onChange={(event) => setTopP(parseFloat(event.target.value))} />
						<Slider min={Number(parameters['top_p'].range_lower_bound)} max={Number(parameters['top_p'].range_upper_bound)} step={Number(parameters['top_p'].range_upper_bound)/100} value={topP} // @ts-ignore
								onChange={handleSliderChange(setTopP)}
								trackStyle={trackStyle} handleStyle={handleStyle} railStyle={railStyle} className="w-11/12" />
					</div>
					<span className="text_13 text_color_secondary">Output will be sampled from the top p percentage of most probable tokens. Increasing top p value gives more likely tokens.</span>
				</div>
			)}

			{parameters['top_k'] && (
				<div className="mt_24">
					<span className="text_13 fw_500 text_color">Top K</span>
					<div className="horizontal_container items-center gap-2 w-full">
						<input type="number" min="0" max="1" step="0.01" className="text_field_primary" style={{width: '10%'}}
							   value={topK} onChange={(event) => setTopK(parseFloat(event.target.value))} />
						<Slider min={Number(parameters['top_k'].range_lower_bound)} max={100} step={1} value={topK} // @ts-ignore
							onChange={handleSliderChange(setTopK)}
								trackStyle={trackStyle} handleStyle={handleStyle} railStyle={railStyle} className="w-11/12" />
					</div>
					<span className="text_13 text_color_secondary">Output will be sampled from the top k probable tokens. Increasing top k value gives more likely tokens.</span>
				</div>
			)}

			{parameters['temperature'] && (
				<div className="mt_24">
					<span className="text_13 fw_500 text_color">Temperature</span>
					<div className="horizontal_container items-center gap-2 w-full">
						<input type="number" min="0" max="1" step="0.01" className="text_field_primary" style={{width: '10%'}}
							   value={temperature} onChange={(event) => setTemperature(parseFloat(event.target.value))} />
						<Slider min={Number(parameters['temperature'].range_lower_bound)} max={Number(parameters['temperature'].range_upper_bound)} step={Number(parameters['top_p'].range_upper_bound)/100} value={temperature} // @ts-ignore
								onChange={handleSliderChange(setTemperature)}
								trackStyle={trackStyle} handleStyle={handleStyle} railStyle={railStyle} className="w-11/12" />
					</div>
					<span className="text_13 text_color_secondary">Controlling the randomness of the output. Increasing temperature increases randomness, and 0 is deterministic.</span>
				</div>
			)}

			{parameters['repetition_penalty'] &&
				<div className="mt_24">
					<span className="text_13 fw_500 text_color">Repetition Penalty</span>
					<input type="number" className="text_field_primary" value={repetitionPenalty} placeholder="Enter Value here"
						   onChange={(event) => setRepetitionPenalty(parseInt(event.target.value, 10))} />
					<span className="text_13 text_color_secondary">Penalty for repeating tokens in output. Increasing penalty implies lesser repeated tokens, and 1 implies no penalty.</span>
				</div>}

			{parameters['stop'] &&
				<div className="mt_24">
					<span className="text_13 fw_500 text_color">Stop Sequence</span>
					<input type="text" className="text_field_primary" value={stopSequence} placeholder="Enter Value here"
						   onChange={(event) => setStopSequence(event.target.value)} />
					<span className="text_13 text_color_secondary">{'Output generation will be paused on the given stop sequence. For example, if  ‘<!>,<stop>,<0>’ are given, then the generation will be stopped as soon as ‘!’ or ‘stop’ or ‘0’ are generated in the output.'}</span>
				</div>}

			<div className="horizontal_container w-full sticky bg_color justify-end mt_20 mb_20 bottom-0 gap_8 pt-2 pb-2 z_2">
				<button className="secondary_button">Reset</button>
				<button className="primary_button" onClick={() => runModels()}>Run Model</button>
			</div>
			<ToastContainer />
		</div>
	);
}
