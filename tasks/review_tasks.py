from crewai import Task

def create_review_task(agent, document_to_review):
    return Task(
        description=f"""
        Carefully review the following research document:

        {document_to_review}

        As a strict conference reviewer, identify strengths and weaknesses, areas for improvement, and potential issues.
        Provide a detailed review document in markdown format, addressing all points comprehensively.
        Ensure the review is constructive, critical, and helps improve the quality of the research.
        """,
        expected_output="A fully-reviewed proposal addressing your review points, formated in markdown. Do not include the ```markdown line at the beginning.",
        agent=agent
    )