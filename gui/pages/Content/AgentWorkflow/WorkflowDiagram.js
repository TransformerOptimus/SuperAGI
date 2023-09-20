import { useEffect } from 'react';
import yaml from 'js-yaml';
import mermaid from 'mermaid';

export default function WorkflowDiagram({yamlContent}) {

    useEffect(() => {
        mermaid.initialize({
            startOnLoad: false,
        });
        mermaid.init(undefined, document.querySelectorAll('.mermaid'));
    }, []);

    function convertYamlToMermaid(yamlContent) {
        const parsedData = yaml.load(yamlContent);
        const steps = parsedData.steps;

        let mermaidString = 'graph TD\n';
        let linkIndex = 0;

        steps.forEach(step => {
            mermaidString += `${step.name}[${step.instruction}]\n`;

            // Define next steps based on the 'next' property
            if (typeof step.next === 'string') {
                mermaidString += `${step.name} --> ${step.next}\n`;
                mermaidString += `linkStyle ${linkIndex} stroke:#2E294B,stroke-width:4px;\n`;
                linkIndex++;
            } else if (typeof step.next === 'object' && Array.isArray(step.next)) {
                step.next.forEach(nextStep => {
                    mermaidString += `${step.name} -->|${nextStep.output}| ${nextStep.step}\n`;
                    mermaidString += `linkStyle ${linkIndex} stroke:#2E294B,stroke-width:4px;\n`;
                    linkIndex++;
                });
            } else if (typeof step.next === 'object') {
                // For conditional branching
                if (step.next.next_step) {
                    mermaidString += `${step.name} --> ${step.next.next_step}\n`;
                    mermaidString += `linkStyle ${linkIndex} stroke:#2E294B,stroke-width:4px;\n`;
                    linkIndex++;
                }
                if (step.next.exit_step) {
                    mermaidString += `${step.name} --> ${step.next.exit_step}\n`;
                    mermaidString += `linkStyle ${linkIndex} stroke:#2E294B,stroke-width:4px;\n`;
                    linkIndex++;
                }
            }
        });

        return mermaidString;
    }

    const mermaidContent = convertYamlToMermaid(yamlContent);

    return (
        <div>
            <div className="mermaid">
                {mermaidContent}
            </div>
        </div>
    );
}


