# app.py
import streamlit as st
from agents.researcher_agent import create_researcher_agent
from agents.reviewer_agent import create_reviewer_agent
from tasks.research_tasks import create_research_proposal_task
from tasks.review_tasks import create_review_task
from crewai import Crew, Process

# --- Configuration ---
#llm_config_openai = {"service": "openai", "model": "gpt-4-turbo-preview"} # Load from llm_config.yaml
#llm_config_gemini = {"service": "google_gemini", "model": "gemini-pro"} # Load from llm_config.yaml

st.set_page_config(layout="wide") # Set layout to wisöde for full width

# --- UI Layout ---
st.title("Research Proposal & Paper Writer")

col1, col2 = st.columns([1, 3]) # Left panel (agents), Right panel (editor/output)

with col1:
    st.header("Agent Customization")
    agent_count = st.slider("Number of Agents", 1, 5, 2) # Example: Slider for agent count
    agent_configurations = []
    for i in range(agent_count):
        st.subheader(f"Agent {i+1}")
        agent_type = st.selectbox(f"Agent Type {i+1}", ["Researcher", "Reviewer"], key=f"agent_type_{i}")
        agent_name = st.text_input(f"Agent Name {i+1}", f"{agent_type} {i+1}", key=f"agent_name_{i}")
        llm_service = st.selectbox(f"LLM Service {i+1}", ["openai", "anthropic", "gemini"], key=f"llm_service_{i}")
        llm_model = st.text_input(f"LLM Model {i+1}", "default", key=f"llm_model_{i}") # Model selection per service
        custom_prompt = st.text_area(f"Custom Prompt {i+1}", "", height=100, key=f"custom_prompt_{i}")
        agent_configurations.append({
            "type": agent_type,
            "name": agent_name,
            "llm_service": llm_service,
            "llm_model": llm_model,
            "custom_prompt": custom_prompt
        })

    st.header("Workflow")
    workflow_description = st.text_area("Workflow Instructions (e.g., 'Researcher -> Reviewer')", "") # Simple workflow input

with col2:
    st.header("Output Editor")
    if 'output_text' not in st.session_state:
        st.session_state['output_text'] = ""
    user_input_text = st.text_area("WYSIWYG Editor (Markdown Output)", st.session_state['output_text'], height=400)

    if st.button("Run Workflow"):
        st.session_state['output_text'] = "Workflow Running...\n(Details to be implemented)" # Basic feedback
        st.spinner("Running Workflow...")

        # --- Agent and Task Creation based on UI config ---
        agents_list = []
        for config in agent_configurations:
            if config["type"] == "Researcher":
                agents_list.append(create_researcher_agent(
                    llm_service=config["llm_service"],
                    llm_model=config["llm_model"],
                    custom_name=config["name"],
                    custom_instructions=config["custom_prompt"]
                ))
            elif config["type"] == "Reviewer":
                agents_list.append(create_reviewer_agent(
                    llm_service=config["llm_service"],
                    llm_model=config["llm_model"],
                    custom_name=config["name"],
                    custom_instructions=config["custom_prompt"]
                ))

        # --- Task Creation and Workflow Logic (Simplified Example) ---
        research_topic = "The impact of AI on scientific research methodologies" # Example - get from UI
        researcher_agent = next((agent for agent in agents_list if agent.role == "Researcher"), None)
        reviewer_agent = next((agent for agent in agents_list if agent.role == "Reviewer"), None)

        if researcher_agent and reviewer_agent:
            research_task = create_research_proposal_task(researcher_agent, research_topic)
            review_task = create_review_task(reviewer_agent, research_task.output)

            proposal_crew = Crew(
                agents=[researcher_agent, reviewer_agent],
                tasks=[research_task, review_task],
                process=Process.sequential, # Basic sequential workflow
                verbose=True # Show detailed process
            )

            # --- Run Crew and Display Output ---
            final_output = proposal_crew.kickoff()
            st.session_state['output_text'] = final_output.raw # Store output for editor display
        else:
            st.error("Please ensure you have at least one Researcher and one Reviewer agent configured for this workflow.")


    st.markdown(st.session_state['output_text'], unsafe_allow_html=True) # Display markdown output