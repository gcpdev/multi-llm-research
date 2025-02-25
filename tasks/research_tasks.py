from crewai import Task

def create_research_proposal_task(agent, research_topic):
    return Task(
        description=f"""
        Conduct comprehensive research on the topic: '{research_topic}'.
        Your goal is to produce a detailed research proposal in markdown format.
        The proposal should include:
        - A clear and concise research question.
        - Background and significance of the research.
        - Literature review summarizing relevant prior work.
        - Proposed methodology and approach.
        - Expected outcomes and impact.
        - Timeline and resources required.

        Ensure the proposal is well-structured, scientifically sound, and persuasive.
        """,
        expected_output="A research proposal with proper references, formated in markdown.",
        agent=agent
    )
