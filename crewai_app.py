from crewai import Agent, Task, Crew, LLM, Process
from crewai_tools import (SerperDevTool, WebsiteSearchTool)

# Define LLM models (replace with actual model lists from providers)
llm_models = {
    "openai": ["chatgpt-4o-latest", "o1", "o3-mini"],
    "anthropic": ["claude-3-5-sonnet-latest", "claude-3-5-haiku-latest"],
    "gemini": ["gemini-2.0-flash", "gemini-2.0-flash-lite-preview-02-05"] # Example model
}

scholar_search_tool = SerperDevTool(
    search_url="https://google.serper.dev/scholar",
    n_results=2,
)

rag_search_tool = WebsiteSearchTool()


def create_researcher_agent(llm_provider, llm_model, instruction_prompt, agent_name="Researcher"):
    llm = LLM(model=f"{llm_provider}/{llm_model}")

    system_prompt = f"You are a world-class scientific researcher. Research to the best the following topic: {instruction_prompt} Your goal is to produce a high-quality research proposal in markdown format."
    return Agent(
        role='Researcher',
        name=agent_name,
        llm=llm,
        goal=system_prompt,
        tools=[scholar_search_tool,rag_search_tool],
        backstory="You have a PhD and 10 years of experience in scientific research."
    )

def create_reviewer_agent(llm_provider, llm_model, instruction_prompt, agent_name="Reviewer"):
    llm = LLM(model=f"{llm_provider}/{llm_model}")

    system_prompt = f"You are a strict reviewer from a top-notch, low-acceptance rate conference. {instruction_prompt} Review the input carefully, address all points, and produce a fully reviewed document in markdown format. Provide a complete output, no abbreviations or placeholders."

    return Agent(
        role='Reviewer',
        name=agent_name,
        llm=llm,
        goal=system_prompt,
        tools=[scholar_search_tool,rag_search_tool],
        backstory="You are a highly critical and detail-oriented reviewer for top scientific conferences."
    )

def create_tasks(topic, agents):
    tasks = []
    for agent in agents:
        if agent.role == 'Researcher':
            task = Task(
                description=f"Develop a research proposal on the topic: {topic}. Format the output in markdown.",
                agent=agent
            )
        elif agent.role == 'Reviewer':
            task = Task(
                description=f"Review the research proposal on the topic: {topic}. Check if the actual state of the art and literature review was comprehensive enough. Provide a detailed review in markdown format.",
                agent=agent
            )
        tasks.append(task)
    return tasks

def run_workflow(topic, agent_configs, workflow_type="sequential"): # workflow_type could be "sequential" or "parallel"
    agents = []
    for config in agent_configs:
        if config['role'] == 'Researcher':
            agent = create_researcher_agent(config['llm_provider'], config['llm_model'], config['instruction_prompt'], config['agent_name'])
        elif config['role'] == 'Reviewer':
            agent = create_reviewer_agent(config['llm_provider'], config['llm_model'], config['instruction_prompt'], config['agent_name'])
        agents.append(agent)

    tasks = create_tasks(topic, agents)

    if workflow_type == "sequential":
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=2 # Show workflow progress
        )
        results = crew.kickoff() # For sequential, results are in order of tasks
        return results
    elif workflow_type == "parallel":
         crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.parallel, # For parallel execution
            verbose=2 # Show workflow progress
        )
         results = crew.kickoff() # For parallel, results order might not be guaranteed
         return results
    else:
        raise ValueError("Invalid workflow type")


if __name__ == '__main__':
    # Example usage (for testing backend logic)
    agent_configs = [
        {'role': 'Researcher', 'llm_provider': 'openai', 'llm_model': 'catgpt-4o-latest', 'instruction_prompt': 'Focus on novelty and methodology.', 'agent_name': 'Researcher 1'},
        {'role': 'Reviewer', 'llm_provider': 'gemini', 'llm_model': 'gemini-2.0-flash', 'instruction_prompt': 'Critique the proposal for feasibility and impact.', 'agent_name': 'Reviewer 1'}
    ]
    topic = "The impact of AI on climate change research"
    results = run_workflow(topic, agent_configs)
    print("Workflow Results:")
    for result in results:
        print(result)