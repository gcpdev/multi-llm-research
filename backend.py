import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import (SerperDevTool, WebsiteSearchTool)
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Research Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

scholar_search_tool = SerperDevTool(
    search_url="https://google.serper.dev/scholar"
)

rag_search_tool = WebsiteSearchTool()


# Define models for API
class AgentConfig(BaseModel):
    id: int
    name: str
    model: str
    role: str
    instructions: str

class WorkflowRequest(BaseModel):
    agents: List[AgentConfig]
    workflow: List[int]
    topic: str

class WorkflowResponse(BaseModel):
    result: str
    steps: List[Dict[str, Any]]

# Model provider configurations
def get_llm(model_id: str):
    """Initialize appropriate LLM based on the model identifier."""
    return LLM(model=f"{model_id}")

def create_researcher_agent(agent_config: AgentConfig):
    """Create a researcher agent based on configuration."""
    researcher_prompt = f"""
    You are an expert research scientist specialized in creating high-quality research proposals.
    
    You are an AI-powered research assistant specializing in helping researchers develop high-quality 
    research proposals for submission to top-tier conferences with low acceptance rates. Your role is 
    to assist users in structuring their proposals, refining their research questions, improving clarity, 
    and ensuring novelty and impact. You understand best practices in academic writing, conference-specific 
    expectations, and the latest trends in various scientific fields. You provide constructive feedback, 
    suggest improvements, and help users craft compelling abstracts, related work sections, methodology, 
    and expected results. Keep responses precise, insightful, and aligned with high-impact conference standards.

    Your proposal should include:
    Title
    1. Abstract
    2. Introduction and Background
    3. Literature Review
    4. Research Questions and Objectives
    5. Methodology
    6. Expected Outcomes and Significance
    7. Timeline and Resources
    8. References
    
    IMPORTANT: Format your entire response using markdown syntax, including proper headings, 
    lists, emphasis, and citations where appropriate.
    
    Additional instructions: {agent_config.instructions}
    """
    
    return Agent(
        role=f"Research Scientist: {agent_config.name}",
        goal=f"Create a comprehensive research proposal on the topic",
        backstory="You are a distinguished research scientist with expertise in creating high-quality research proposals.",
        verbose=True,
        allow_delegation=False,
        llm=get_llm(agent_config.model),
        tools=[scholar_search_tool,rag_search_tool]
    )

def create_reviewer_agent(agent_config: AgentConfig):
    """Create a reviewer agent based on configuration."""
    reviewer_prompt = f"""
"You are an AI-powered conference reviewer specializing in evaluating research proposals for submission to 
highly competitive, low-acceptance-rate conferences. Your role is to meticulously analyze the proposal’s structure,
novelty, impact, and literature review quality. You assess whether the proposal sufficiently covers all related
state-of-the-art research, ensuring that it accurately positions itself within the existing body of work.
For that you have access to tools like Google Scholar search, or any website search if needed.
Your review should be critical, highlighting weaknesses, missing references, and gaps in methodology or argumentation."

Review Process:

Literature Review Analysis – Check if the proposal references all key related work and critically analyze 
its coverage of state-of-the-art research. Identify missing or outdated citations.
Novelty & Impact Evaluation – Judge the originality and significance of the research. Does it contribute 
meaningfully to the field? Is it solving a real problem, or is it incremental?
Methodology & Feasibility – Examine whether the proposed approach is rigorous, realistic, and appropriately 
justified. Identify weaknesses in execution.
Clarity & Coherence – Review the structure, clarity, and logical flow of arguments. Suggest improvements in 
writing style and persuasiveness.
Constructive Rewrite – After completing the review, generate a new, improved version of the research proposal, 
addressing all identified shortcomings.

Output Format:

Provide a structured Markdown report output containing a rewritten version of the proposal, incorporating improvements.

Example Output Structure:
Title: [Improved title (if needed - or keep original)]

Abstract:
[Refined abstract that enhances clarity, impact, and novelty]

1. Introduction
[Clearer motivation, problem definition, and research objectives]

2. Related Work
[Expanded and corrected literature review with essential references]

3. Methodology
[Improved research approach, better justification, and feasibility discussion]

4. Expected Results & Contributions
[Stronger argument for impact, significance, and novelty]

5. Conclusion
[More compelling wrap-up, emphasizing importance and broader implications]

    IMPORTANT: You must provide a complete review, not just comments. Output the entire document
    with your review comments integrated in a professional markdown format.
    Never use abbreviations like "..." or "[like original]" - always provide the full content.
    
    Additional instructions: {agent_config.instructions}
    """
    
    return Agent(
        role=f"Academic Reviewer: {agent_config.name}",
        goal=f"Provide a critical, comprehensive review of the research proposal",
        backstory="You are a respected academic reviewer known for your thorough and insightful critiques.",
        verbose=True,
        allow_delegation=False,
        llm=get_llm(agent_config.model),
        tools=[scholar_search_tool,rag_search_tool]
    )

def create_task(agent, role, topic, previous_output=None):
    """Create a task for an agent based on their role."""
    if role == "researcher":
        description = f"""
        Research and create a comprehensive research proposal on the topic: "{topic}".
        
        """
    else:  # reviewer
        description = f"""
        Review the following research proposal critically:
        
        {previous_output}
        
        """
    
    return Task(
        description=description,
        agent=agent,
        expected_output="A comprehensive markdown-formatted document"
    )

@app.post("/run-workflow", response_model=WorkflowResponse)
async def run_workflow(request: WorkflowRequest = Body(...)):
    """Run a research workflow with the specified agents and configuration."""
    if not request.topic:
        raise HTTPException(status_code=400, detail="Research topic cannot be empty")
    
    if not request.workflow:
        raise HTTPException(status_code=400, detail="Workflow cannot be empty")
    
    # Validate that all agents in workflow exist in the agents list
    agent_ids = [agent.id for agent in request.agents]
    for workflow_id in request.workflow:
        if workflow_id not in agent_ids:
            raise HTTPException(status_code=400, detail=f"Agent with ID {workflow_id} not found")
    
    agents = {}
    for agent_config in request.agents:
        if agent_config.role == "researcher":
            agents[agent_config.id] = create_researcher_agent(agent_config)
        else:
            agents[agent_config.id] = create_reviewer_agent(agent_config)
    
    # Create tasks based on workflow
    tasks = []
    current_output = request.topic
    step_results = []
    
    for idx, agent_id in enumerate(request.workflow):
        agent_config = next((a for a in request.agents if a.id == agent_id), None)
        agent = agents[agent_id]
        
        # Create task based on agent role
        task = create_task(agent, agent_config.role, request.topic, current_output)
        tasks.append(task)
        
    # If this is the first task in workflow or we want to run sequentially
    # Execute the task immediately to get output for next task
    crew = Crew(
        agents=agents[agent_config.id],
        tasks=tasks,
        verbose=True,
        process=Process.sequential
    )
    
    result = crew.kickoff()
    current_output = result
    
    step_results.append({
        "agent_id": agent_id,
        "agent_name": agent_config.name,
        "role": agent_config.role,
        "model": agent_config.model,
        "output_preview": result[:100] + "..." if len(result) > 100 else result
    })
    
    return WorkflowResponse(result=current_output, steps=step_results)

@app.get("/")
async def root():
    return {"message": "Research Assistant API is running"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)