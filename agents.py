import os
import time
import logging
import traceback
from crewai import LLM

# Set up a module logger
logger = logging.getLogger(__name__)

def add_debug_log(message, level="info"):
    timestamp = time.strftime("%H:%M:%S")
    if level == "error":
        logger.error(f"[{timestamp}] {message}")
    elif level == "warning":
        logger.warning(f"[{timestamp}] {message}")
    else:
        logger.info(f"[{timestamp}] {message}")

def get_role_instructions(role):
    if role == "Researcher":
        return (
            "You are an expert academic researcher with deep knowledge in your domain.\n"
            "Your task is to perform high-quality scientific research on the given topic.\n"
            "Produce a comprehensive research proposal with the following sections:\n"
            "1. Title\n"
            "2. Abstract (concise summary of the research)\n"
            "3. Introduction (background, motivation, problem statement)\n"
            "4. Literature Review (critical evaluation of existing work)\n"
            "5. Research Questions and Objectives\n"
            "6. Methodology (detailed research approach)\n"
            "7. Expected Results and Contributions\n"
            "8. Timeline and Milestones\n"
            "9. References (in proper academic format)\n\n"
            "Format your output using proper Markdown syntax with appropriate headings, bullet points, and emphasis.\n"
            "Be thorough, precise, and maintain academic rigor throughout your work."
        )
    elif role == "Reviewer":
        return (
            "You are a strict academic reviewer from a top-tier, highly selective conference or journal.\n"
            "Your task is to thoroughly review the given document with the highest academic standards.\n"
            "Provide a comprehensive review covering:\n"
            "1. Overall Assessment (strengths and weaknesses)\n"
            "2. Technical Quality and Methodology\n"
            "3. Clarity of Presentation\n"
            "4. Significance and Originality\n"
            "5. Detailed Comments on Each Section\n"
            "6. Recommendations for Improvement\n\n"
            "Your output must be a fully reviewed document with embedded comments and suggestions.\n"
            "Use Markdown formatting effectively - headings for sections, italics for emphasis, etc.\n"
            "You MUST produce the complete reviewed document with your version, addressing all your points.\n"
            "Do NOT use abbreviations, summaries, or 'like input' placeholders."
        )
    else:
        return "You are a helpful research assistant. Your task is to help create high-quality research content."

def get_llm_from_provider(provider_name, model_name=None, **kwargs):
    """
    Retrieve an LLM instance from the specified provider.

    Args:
        provider_name (str): The name of the LLM provider (e.g., 'openai', 'anthropic', 'google').
        api_key (str): The API key for authenticating with the provider.
        model_name (str, optional): The specific model to use. Defaults to the provider's default model.
        **kwargs: Additional keyword arguments for LLM configuration.

    Returns:
        LLM: An instance of the configured LLM.
    """

    # Initialize the LLM based on the provider
    if provider_name.lower() == 'openai':
        llm_config = {
          'api_key': os.getenv("OPENAI_API_KEY"),
          'model': model_name,
          **kwargs
        }
        llm = LLM(provider='openai', **llm_config)
    elif provider_name.lower() == 'anthropic':
        llm_config = {
          'api_key': os.getenv("ANTHROPIC_API_KEY"),
          'model': model_name,
          **kwargs
        }
        llm = LLM(provider='anthropic', **llm_config)
    elif provider_name.lower() == 'google':
        llm_config = {
          'api_key': os.getenv("GOOGLE_GEMINI_API_KEY"),
          'model': model_name,
          **kwargs
        }
        llm = LLM(provider='google', **llm_config)
    elif provider_name.lower() == 'xai':
        llm_config = {
          'api_key': os.getenv("GROK_API_KEY"),
          'model': model_name,
          **kwargs
        }
        llm = LLM(provider='grok', **llm_config)
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")

    return llm

def create_agent(agent_config):
    """
    Creates and returns a CrewAI Agent using the given configuration.
    """
    from crewai import Agent  # assuming Agent class is provided by crewai
    llm = get_llm_from_provider(
        provider_name=agent_config['provider'],
        model_name=agent_config['model']
    )
    agent = Agent(
        role=agent_config['role'],
        goal=f"Help improve research documents as a {agent_config['role']}",
        backstory=f"You are an expert {agent_config['role']} with deep knowledge in academic writing and research methodologies.",
        verbose=True,
        llm=llm,
        tools=[],
        allow_delegation=False
    )
    add_debug_log(f"Agent '{agent_config['name']}' created successfully")
    return agent

