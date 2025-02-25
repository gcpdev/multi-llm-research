from crewai import Agent, Task, Crew, LLM, Process
from crewai_tools import (SerperDevTool, WebsiteSearchTool)

# Define LLM models (replace with actual model lists from providers)
llm_models = {
    "openai": ["chatgpt-4o-latest", "o1", "o3-mini"],
    "anthropic": ["claude-3-7-sonnet-latest", "claude-3-5-haiku-latest"],
    "gemini": ["gemini-2.0-flash-thinking-exp","gemini-2.0-flash"] # Example model
}

scholar_search_tool = SerperDevTool(
    search_url="https://google.serper.dev/scholar",
    n_results=10,
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
                description=f"Develop a research proposal on the topic: {topic}.",
                expected_output="Format the output in markdown. It should contain a detailed research plan to the user topic.",
                agent=agent
            )
        elif agent.role == 'Reviewer':
            task = Task(
                description=f"Review the research proposal on the topic: {topic}. Check if the actual state of the art and literature review was comprehensive enough.",
                expected_output="A detailed reviewed version of the input in markdown format, addressing all review points.",
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
            verbose=True # Show workflow progress
        )
        results = crew.kickoff() # For sequential, results are in order of tasks
        return results.raw
    elif workflow_type == "parallel":
         crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.parallel, # For parallel execution
            verbose=True # Show workflow progress
        )
         results = crew.kickoff() # For parallel, results order might not be guaranteed
         return results.raw
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