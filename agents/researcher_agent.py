from crewai import Agent, LLM
from crewai_tools import (SerperDevTool, WebsiteSearchTool)

scholar_search_tool = SerperDevTool(
    search_url="https://google.serper.dev/scholar",
)

rag_search_tool = WebsiteSearchTool()


def create_researcher_agent(llm_service="openai", llm_model="chatgpt-4o-latest", custom_name=None, custom_instructions=None):
    llm = LLM(model=f"{llm_service}/{llm_model}")
    
    system_prompt = """You are an expert research scientist. Your goal is to perform high quality scientific research on the topic that the user inputs, providing the output as a research proposal with markdown format."""
    if custom_instructions:
        system_prompt += f"\n\nUser Custom Instructions: {custom_instructions}"

    return Agent(
        role="Researcher",
        goal="Conduct thorough scientific research and create compelling research proposals.",
        backstory="You are a seasoned researcher known for your meticulous approach and impactful proposals.",
        verbose=True,
        allow_delegation=True,
        tools=[scholar_search_tool,rag_search_tool],
        llm=llm,
        name=custom_name if custom_name else "Research Agent",
        system_prompt=system_prompt
    )