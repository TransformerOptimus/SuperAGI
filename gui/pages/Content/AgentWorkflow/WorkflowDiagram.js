import { useEffect } from 'react';
import yaml from 'js-yaml';
import mermaid from 'mermaid';
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";



export default function WorkflowDiagram({yamlContent}) {

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

    function convertYamlToMermaid(yamlContent) {
        if (yamlContent && yamlContent !== '') {
            const parsedData = yaml.load(yamlContent);
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

                const sanitizedStepName = step.name.replace(/\s+/g, '');
                mermaidString += `${sanitizedStepName}[${label}]\n`;

                // Define next steps based on the 'next' property
                if (typeof step.next === 'string') {
                    const sanitizedNextName = step.next.replace(/\s+/g, '');
                    mermaidString += `${sanitizedStepName} --> ${sanitizedNextName}\n`;
                    linkIndex++;
                } else if (typeof step.next === 'object' && Array.isArray(step.next)) {
                    step.next.forEach(nextStep => {
                        mermaidString += `${step.name} -->|${nextStep.output}| ${nextStep.step}\n`;
                        // mermaidString += `linkStyle ${linkIndex} stroke:#2E294B,stroke-width:4px;\n`;
                        linkIndex++;
                    });
                } else if (typeof step.next === 'object') {
                    // For conditional branching
                    if (step.next.next_step) {
                        mermaidString += `${step.name} --> ${step.next.next_step}\n`;
                        // mermaidString += `linkStyle ${linkIndex} stroke:#2E294B,stroke-width:4px;\n`;
                        linkIndex++;
                    }
                    if (step.next.exit_step) {
                        mermaidString += `${step.name} --> ${step.next.exit_step}\n`;
                        // mermaidString += `linkStyle ${linkIndex} stroke:#2E294B,stroke-width:4px;\n`;
                        linkIndex++;
                    }
                }
            });

            return mermaidString;
        }
    }
    function handleDragStart(event) {
        event.dataTransfer.setData('text/plain', mermaidContent);
    }


    const mermaidContent = convertYamlToMermaid(yamlContent);

    return (
        <div >
                <div >
                    <div className="mermaid"  style={{
                        padding: '20px',
                        border: '1px dashed #ccc',
                        cursor: 'grab', // Change cursor style on drag
                    }}
                         draggable // Enable drag-and-drop on the div
                         onDragStart={handleDragStart} // Event handler for drag start
                    >
                        {mermaidContent}
                    </div>
                </div>
        </div>
    );
}


