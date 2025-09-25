export type ScriptLoadArgs = {
  script_name: string;
};

export type Script = {
  name: string;
  description: string;
  stages: Array<{
    name: string;
    prompt: string;
    questions?: string[];
    actions?: string[];
  }>;
  output_format?: string;
  interactive_elements?: string[];
};

export async function scriptLoadTool(args: ScriptLoadArgs): Promise<{ script: Script; instructions: string }> {
  // Fetch the script from the backend
  const res = await fetch(`http://localhost:8000/scripts/${args.script_name}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`Failed to load script '${args.script_name}': ${res.status} ${JSON.stringify(err)}`);
  }
  
  const script: Script = await res.json();
  
  // Generate dynamic instructions based on the script
  const instructions = generateScriptInstructions(script);
  
  return { script, instructions };
}

function generateScriptInstructions(script: Script): string {
  let instructions = `\n\n## 🎯 ACTIVE SCRIPT: ${script.name}\n\n${script.description}\n\n`;
  
  instructions += `### 📋 SCRIPT STRUCTURE:\n`;
  script.stages.forEach((stage, index) => {
    instructions += `${index + 1}. **${stage.name.toUpperCase()}**: ${stage.prompt}\n`;
    if (stage.questions && stage.questions.length > 0) {
      instructions += `   - Key questions: ${stage.questions.join(', ')}\n`;
    }
    if (stage.actions && stage.actions.length > 0) {
      instructions += `   - Available actions: ${stage.actions.join(', ')}\n`;
    }
  });
  
  if (script.output_format) {
    instructions += `\n### 📄 OUTPUT FORMAT: ${script.output_format}\n`;
  }
  
  if (script.interactive_elements && script.interactive_elements.length > 0) {
    instructions += `\n### 🎮 INTERACTIVE ELEMENTS: ${script.interactive_elements.join(', ')}\n`;
  }
  
  instructions += `\n### 🎯 SCRIPT EXECUTION GUIDELINES:\n`;
  instructions += `- **YOU ARE NOW FOLLOWING THIS SCRIPT**: Use this as your primary guidance for the conversation\n`;
  instructions += `- **STAGE-BY-STAGE APPROACH**: Guide the user through each stage naturally and conversationally\n`;
  instructions += `- **DON'T RUSH**: Let the user explore and engage with each stage fully\n`;
  instructions += `- **ADAPT WHEN NEEDED**: Use the script as a framework, but adapt to the user's needs and interests\n`;
  instructions += `- **CAPTURE CONTENT**: Save important content in markdown files as you progress\n`;
  instructions += `- **STAY ENCOURAGING**: Be supportive and positive throughout the process\n`;
  instructions += `- **CURRENT STAGE**: Start with the first stage and progress naturally\n`;
  
  instructions += `\n### 💡 IMPORTANT: This script is now your primary behavior guide. Follow its structure and prompts to help the user achieve their goals.\n`;
  
  return instructions;
}

export async function listAvailableScripts(): Promise<string[]> {
  const res = await fetch('http://localhost:8000/scripts', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`Failed to list scripts: ${res.status} ${JSON.stringify(err)}`);
  }
  
  return await res.json();
}
