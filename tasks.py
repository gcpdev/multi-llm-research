from crewai import Task

from agents import get_role_instructions

def create_task(step_idx, step, agent_config, agent, document_content, tasks):
    """
    Creates and returns a CrewAI Task for the given workflow step.
    """

    # Determine the context for the task as a list of strings.
    if step_idx == 0:
        context = [str(document_content)]  # Ensure this is a list of strings
    else:
        # Get the output from the previous task
        previous_task = tasks[step_idx - 1]

        # Ensure the previous task's output is a string
        if hasattr(previous_task, 'output'):
            context = [str(previous_task.output)]  # Convert to string if necessary
        else:
            context = [str(previous_task)]  # Fallback to string representation

    base_instructions = get_role_instructions(agent_config['role'])

    task_description = f"""
    TASK: {step['task']}

    ROLE INSTRUCTIONS:
    {base_instructions}

    ADDITIONAL INSTRUCTIONS:
    1. Focus specifically on the task description above.
    2. Maintain markdown formatting throughout.
    3. Provide comprehensive output with proper academic structure.
    """

    task = Task(
        description=task_description,
        agent=agent,
        expected_output="A well-formatted markdown document based on the task instructions",
        context=context  # Ensure this is a list of strings
    )
    return task
