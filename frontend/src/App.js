import React, { useState, useEffect } from 'react';
import { PlusCircle, Trash2, ArrowRight, Check, Edit, Play, Coffee, AlertCircle, UserCheck, Eye } from 'lucide-react';

const ResearchAssistantApp = () => {
  const [agents, setAgents] = useState([
    { 
      id: 1, 
      name: 'Research Expert', 
      model: 'anthropic/claude-3-7-sonnet', 
      role: 'researcher',
      instructions: 'Perform high quality scientific research on the given topic and provide a comprehensive research proposal with clear methodology, literature review, and expected outcomes.',
      isRunning: false,
      isComplete: false
    }
  ]);
  
  const [workflow, setWorkflow] = useState([1]);
  const [markdownContent, setMarkdownContent] = useState('# Research Proposal\n\nStart by providing a topic in the input field and configuring your AI research agents.');
  const [isRunning, setIsRunning] = useState(false);
  const [userInput, setUserInput] = useState('');
  const [activeAgent, setActiveAgent] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');

  const availableModels = [
    { value: 'anthropic/claude-3-7-sonnet', label: 'Claude 3.7 Sonnet' },
    { value: 'anthropic/claude-3-opus', label: 'Claude 3 Opus' },
    { value: 'openai/o3-mini', label: 'OpenAI O3 mini' },
    { value: 'openai/chatgpt-4o-turbo', label: 'OpenAI GPT-4 Turbo' },
    { value: 'gemini/gemini-flash-2.0', label: 'Google Gemini Flash 2.0' },
    { value: 'xai/grok-2', label: 'Grok-2' }
  ];

  const runWorkflow = async () => {
    if (!userInput.trim()) {
      setStatusMessage("Please enter a research topic first");
      setTimeout(() => setStatusMessage(""), 3000);
      return;
    }
    
    setIsRunning(true);
    setMarkdownContent('# Research Workflow In Progress\n\nPlease wait while the AI agents process your request...');
    
    // Reset all agents
    setAgents(agents.map(agent => ({
      ...agent,
      isRunning: false,
      isComplete: false
    })));
    
    try {
      const response = await fetch('http://localhost:8000/run-workflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agents: agents.map(agent => ({
            id: agent.id,
            name: agent.name,
            model: agent.model,
            role: agent.role,
            instructions: agent.instructions
          })),
          workflow: workflow,
          topic: userInput
        })
      });
      
      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Update the UI with results
      setMarkdownContent(data.result);
      
      // Update agent status based on steps
      const updatedAgents = [...agents];
      data.steps.forEach(step => {
        const agentIndex = updatedAgents.findIndex(a => a.id === step.agent_id);
        if (agentIndex !== -1) {
          updatedAgents[agentIndex].isComplete = true;
        }
      });
      
      setAgents(updatedAgents);
      setStatusMessage("Workflow completed successfully!");
      
    } catch (error) {
      console.error("Error running workflow:", error);
      setStatusMessage(`Error: ${error.message}`);
    } finally {
      setIsRunning(false);
      setTimeout(() => setStatusMessage(""), 5000);
    }
  };

  const addAgent = () => {
    if (agents.length < 5) {
      const newId = Math.max(...agents.map(agent => agent.id), 0) + 1;
      setAgents([...agents, {
        id: newId,
        name: `Agent ${newId}`,
        model: 'anthropic/claude-3-7-sonnet',
        role: 'researcher',
        instructions: 'Perform high quality scientific research on the given topic.',
        isRunning: false,
        isComplete: false
      }]);
    }
  };

  const removeAgent = (id) => {
    setAgents(agents.filter(agent => agent.id !== id));
    setWorkflow(workflow.filter(agentId => agentId !== id));
  };

  const updateAgent = (id, field, value) => {
    setAgents(agents.map(agent => 
      agent.id === id ? { ...agent, [field]: value } : agent
    ));
  };

  const addToWorkflow = (agentId) => {
    if (!workflow.includes(agentId)) {
      setWorkflow([...workflow, agentId]);
    }
  };

  const removeFromWorkflow = (index) => {
    const newWorkflow = [...workflow];
    newWorkflow.splice(index, 1);
    setWorkflow(newWorkflow);
  };

  const moveInWorkflow = (index, direction) => {
    if ((direction === -1 && index > 0) || (direction === 1 && index < workflow.length - 1)) {
      const newWorkflow = [...workflow];
      const temp = newWorkflow[index];
      newWorkflow[index] = newWorkflow[index + direction];
      newWorkflow[index + direction] = temp;
      setWorkflow(newWorkflow);
    }
  };

  const handleRunWorkflow = () => {
    if (!userInput.trim()) {
      setStatusMessage("Please enter a research topic first");
      setTimeout(() => setStatusMessage(""), 3000);
      return;
    }
    
    if (workflow.length === 0) {
      setStatusMessage("Please add at least one agent to the workflow");
      setTimeout(() => setStatusMessage(""), 3000);
      return;
    }
    
    setIsRunning(true);
    setMarkdownContent('# Research Workflow In Progress\n\nPlease wait while the AI agents process your request...');
    
    // Reset all agents
    setAgents(agents.map(agent => ({
      ...agent,
      isRunning: false,
      isComplete: false
    })));
    
    runWorkflow(agents, workflow, userInput);
  };

  // Component to render markdown
  const MarkdownRenderer = ({ markdown }) => {
    const createMarkup = () => {
      // Convert markdown to HTML (simplified version)
      let html = markdown
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/\*\*(.*)\*\*/gm, '<strong>$1</strong>')
        .replace(/\*(.*)\*/gm, '<em>$1</em>')
        .replace(/- (.*)/gm, '<li>$1</li>')
        .replace(/\n\n/gm, '<br /><br />');
      
      // Convert numbered lists
      let counter = 0;
      html = html.replace(/^\d+\. (.*$)/gm, (match) => {
        counter++;
        return `<div>${counter}. ${match.substr(match.indexOf('.') + 2)}</div>`;
      });
      
      return {__html: html};
    };
    
    return <div className="prose" dangerouslySetInnerHTML={createMarkup()} />;
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-indigo-700 text-white p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">Research Paper Assistant</h1>
          {statusMessage && (
            <div className="bg-indigo-600 px-4 py-2 rounded-full flex items-center">
              {isRunning ? <Coffee className="animate-spin mr-2" size={18} /> : <Check className="mr-2" size={18} />}
              <span>{statusMessage}</span>
            </div>
          )}
        </div>
      </header>
      
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Agent Configuration */}
        <div className="w-1/2 p-4 overflow-y-auto bg-white shadow-md border-r">
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-4">Research Topic</h2>
            <div className="flex">
              <input
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="Enter your research topic here..."
                className="flex-1 p-2 border rounded-l"
                disabled={isRunning}
              />
              <button 
                onClick={handleRunWorkflow} 
                disabled={isRunning || workflow.length === 0}
                className="bg-green-600 text-white p-2 rounded-r flex items-center"
              >
                {isRunning ? <Coffee className="animate-spin" size={18} /> : <Play size={18} />}
                <span className="ml-2">{isRunning ? 'Running...' : 'Run Workflow'}</span>
              </button>
            </div>
          </div>
          
          <div className="mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Research Agents</h2>
              <button 
                onClick={addAgent} 
                disabled={agents.length >= 5 || isRunning}
                className={`text-white p-2 rounded flex items-center ${agents.length >= 5 ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'}`}
              >
                <PlusCircle size={18} />
                <span className="ml-2">Add Agent</span>
              </button>
            </div>
            
            {agents.map(agent => (
              <div 
                key={agent.id} 
                className={`mb-4 p-4 border rounded-lg ${agent.isRunning ? 'bg-blue-50 border-blue-300 animate-pulse' : agent.isComplete ? 'bg-green-50 border-green-300' : 'bg-white'}`}
              >
                <div className="flex justify-between items-center mb-3">
                  <div className="flex items-center">
                    <input
                      type="text"
                      value={agent.name}
                      onChange={(e) => updateAgent(agent.id, 'name', e.target.value)}
                      className="font-semibold bg-transparent border-b border-gray-300 focus:border-blue-500 focus:outline-none"
                      disabled={isRunning}
                    />
                    {agent.isRunning && <Coffee className="ml-2 animate-spin text-blue-600" size={16} />}
                    {agent.isComplete && <Check className="ml-2 text-green-600" size={16} />}
                  </div>
                  <div className="flex">
                    <button 
                      onClick={() => addToWorkflow(agent.id)} 
                      disabled={workflow.includes(agent.id) || isRunning}
                      className={`p-1 rounded mr-2 ${workflow.includes(agent.id) ? 'bg-gray-200 text-gray-500' : 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'}`}
                      title="Add to workflow"
                    >
                      <ArrowRight size={16} />
                    </button>
                    <button 
                      onClick={() => removeAgent(agent.id)} 
                      disabled={isRunning}
                      className="p-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
                      title="Remove agent"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-3 mb-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Model</label>
                    <select
                      value={agent.model}
                      onChange={(e) => updateAgent(agent.id, 'model', e.target.value)}
                      className="w-full p-2 border rounded"
                      disabled={isRunning}
                    >
                      {availableModels.map(model => (
                        <option key={model.value} value={model.value}>{model.label}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                    <select
                      value={agent.role}
                      onChange={(e) => updateAgent(agent.id, 'role', e.target.value)}
                      className="w-full p-2 border rounded"
                      disabled={isRunning}
                    >
                      <option value="researcher">Researcher</option>
                      <option value="reviewer">Reviewer</option>
                    </select>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Instructions</label>
                  <textarea
                    value={agent.instructions}
                    onChange={(e) => updateAgent(agent.id, 'instructions', e.target.value)}
                    className="w-full p-2 border rounded h-20 text-sm"
                    disabled={isRunning}
                  />
                </div>
              </div>
            ))}
          </div>
          
          <div>
            <h2 className="text-xl font-semibold mb-4">Workflow</h2>
            {workflow.length === 0 ? (
              <div className="p-4 border border-dashed rounded-lg text-center text-gray-500">
                <AlertCircle className="mx-auto mb-2" size={24} />
                <p>Add agents to your workflow to start</p>
              </div>
            ) : (
              <div className="border rounded-lg overflow-hidden">
                {workflow.map((agentId, index) => {
                  const agent = agents.find(a => a.id === agentId);
                  if (!agent) return null;
                  
                  return (
                    <div 
                      key={index} 
                      className={`p-3 flex items-center justify-between border-b last:border-b-0 ${activeAgent === agentId ? 'bg-blue-50' : (agent.isComplete ? 'bg-green-50' : 'bg-white')}`}
                    >
                      <div className="flex items-center">
                        <span className="bg-gray-200 rounded-full w-6 h-6 flex items-center justify-center text-sm mr-3">
                          {index + 1}
                        </span>
                        <div>
                          <div className="font-medium">{agent.name}</div>
                          <div className="text-xs text-gray-500 flex items-center">
                            {agent.role === 'researcher' ? 
                              <Edit className="mr-1" size={12} /> : 
                              <Eye className="mr-1" size={12} />
                            }
                            {agent.role}
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex">
                        <button 
                          onClick={() => moveInWorkflow(index, -1)} 
                          disabled={index === 0 || isRunning}
                          className={`p-1 rounded mr-1 ${index === 0 || isRunning ? 'bg-gray-100 text-gray-400' : 'bg-gray-200 hover:bg-gray-300'}`}
                        >
                          ↑
                        </button>
                        <button 
                          onClick={() => moveInWorkflow(index, 1)} 
                          disabled={index === workflow.length - 1 || isRunning}
                          className={`p-1 rounded mr-1 ${index === workflow.length - 1 || isRunning ? 'bg-gray-100 text-gray-400' : 'bg-gray-200 hover:bg-gray-300'}`}
                        >
                          ↓
                        </button>
                        <button 
                          onClick={() => removeFromWorkflow(index)}
                          disabled={isRunning}
                          className="p-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
        
        {/* Right Panel - WYSIWYG Editor */}
        <div className="w-1/2 p-4 overflow-y-auto bg-gray-50 relative">
          <div className="mb-4 flex justify-between items-center">
            <h2 className="text-xl font-semibold">Document Editor</h2>
            <div className="flex space-x-2">
              <UserCheck size={20} className="text-indigo-600" />
              <span className="text-sm text-gray-600">Using CrewAI for enhanced research</span>
            </div>
          </div>
          
          <div className={`bg-white border rounded-lg shadow-sm p-6 min-h-[calc(100vh-160px)] ${isRunning ? 'opacity-75' : ''}`}>
            {isRunning ? (
              <div className="absolute inset-0 flex items-center justify-center z-10">
                <div className="text-center">
                  <Coffee className="animate-spin mx-auto mb-4 text-indigo-600" size={40} />
                  <p className="text-lg font-medium">Workflow in progress...</p>
                  <p className="text-gray-600">{statusMessage}</p>
                </div>
              </div>
            ) : null}
            
            <div className={`prose max-w-none ${isRunning ? 'pointer-events-none' : ''}`}>
              <MarkdownRenderer markdown={markdownContent} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResearchAssistantApp;