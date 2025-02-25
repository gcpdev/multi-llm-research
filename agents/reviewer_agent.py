from crewai import Agent, LLM
from crewai_tools import (SerperDevTool, WebsiteSearchTool)

scholar_search_tool = SerperDevTool(
    search_url="https://google.serper.dev/scholar",
)

rag_search_tool = WebsiteSearchTool()

def create_reviewer_agent(llm_service="openai", llm_model="chatgpt-4o-latest", custom_name=None, custom_instructions=None):
    llm = LLM(model=f"{llm_service}/{llm_model}")


    system_prompt = """You are a highly critical and meticulous reviewer from a top-tier, low-acceptance rate conference. Your task is to take the input, review it carefully, address all potential weaknesses, and produce as output a fully reviewed document with markdown formatting. Provide a comprehensive and detailed review, leaving no room for ambiguity or missing points. Produce full output, no abbreviations or 'like input' blocks."""
    if custom_instructions:
        system_prompt += f"\n\nUser Custom Instructions: {custom_instructions}"

    return Agent(
        role="Reviewer",
        goal="Provide rigorous and constructive reviews of research proposals and papers.",
        backstory="You are a respected reviewer known for your critical eye and commitment to maintaining high scientific standards.",
        verbose=True,
        allow_delegation=False,
        tools=[scholar_search_tool,rag_search_tool],
        llm=llm,
        name=custom_name if custom_name else "Review Agent",
        system_prompt=system_prompt
    )