import { useEffect, useRef } from 'react';
import yaml from 'js-yaml';
import mermaid from 'mermaid';

export default function WorkflowDiagram({yamlContent}) {
    console.log('kdnsdkdsd')

    const mermaidContent = convertYamlToMermaid(yamlContent);
    const mermaidContainerRef = useRef(null);


    useEffect(() => {
        mermaid.initialize({
            startOnLoad: false,
            theme: 'base',
            themeVariables: {'primaryColor': '#2E294B',
            'primaryTextColor': '#fff',
            'primaryBorderColor': '#595181',
            'lineColor': '#2E294B',
            'secondaryColor': '#006100',
            'tertiaryColor': '#fff'},
            flowchart: {
                htmlLabels: true // This allows the use of HTML in the label.
            }
        });
        mermaid.init(undefined, document.querySelectorAll('.mermaid'));
    }, []);

    useEffect(() => {
        if (mermaidContainerRef.current) {
            // Clear the container
            mermaidContainerRef.current.innerHTML = '';

            // Create a new node to contain mermaid content
            const mermaidNode = document.createElement('div');
            mermaidNode.className = 'mermaid';
            mermaidNode.textContent = mermaidContent;

            // Append the new node to the container
            mermaidContainerRef.current.appendChild(mermaidNode);

            // Reinitialize mermaid
            mermaid.init(undefined, mermaidNode);
        }
    }, [yamlContent]);

    function convertYamlToMermaid(yamlContent1) {
        if (yamlContent1 && yamlContent1 !== '') {
            const parsedData = yaml.load(yamlContent1);
            console.log(parsedData)
            const steps = parsedData.steps;

            let mermaidString = 'graph TD\n';
            let linkIndex = 0;

            steps.forEach(step => {
                let label = step.instruction ? `<div style="padding: 8px">${step.instruction}</div>` : ''; // Use instruction if available, else empty string

                if (step.type === 'LOOP') {
                    label = '<div style="border: 1px solid #777 !important; background: #444 !important; padding: 8px ">LOOP</div>';
                }

                if (step.type === 'IF' || step.type === 'CONDITION') {
                    label = step.instruction ? `<div style="border: 1px solid #777 !important; background: #444 !important; padding: 8px ">${step.instruction}</div>` : '';
                }

                const sanitizedStepName = step.name.split(" ").join("");
                mermaidString += `${sanitizedStepName}[${label}]\n`;

                // Define next steps based on the 'next' property
                if (typeof step.next === 'string') {
                    const sanitizedNextName = step.next.split(" ").join("");
                    mermaidString += `${sanitizedStepName} --> ${sanitizedNextName}\n`;
                    linkIndex++;
                } else if (typeof step.next === 'object' && Array.isArray(step.next)) {
                    step.next.forEach(nextStep => {
                        const sanitizedOutput = nextStep.output.split(" ").join("");
                        const sanitizedStep = nextStep.step.split(" ").join("");
                        mermaidString += `${step.name} -->|${sanitizedOutput}| ${sanitizedStep}\n`;
                        linkIndex++;
                    });
                } else if (typeof step.next === 'object') {
                    // For conditional branching
                    if (step.next.next_step) {
                        const sanitizedNextStep = step.next.next_step.split(" ").join("");
                        mermaidString += `${step.name} --> ${sanitizedNextStep}\n`;
                        linkIndex++;
                    }
                    if (step.next.exit_step) {
                        const sanitizedNextStep = step.next.next_step.split(" ").join("");
                        mermaidString += `${step.name} --> ${sanitizedNextStep}\n`;
                        linkIndex++;
                    }
                }
            });
            mermaidString += 'linkStyle default stroke-width: 4px;\n';
            return mermaidString;
        }
    }

    return (
        <div >
                <div ref={mermaidContainerRef}>
                    <div className="mermaid padding_20">
                        {mermaidContent}
                    </div>
                </div>
        </div>
    );
}


