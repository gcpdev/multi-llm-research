import streamlit as st
# from crewai_app import llm_models, run_workflow # Assuming backend in crewai_app.py

st.title("Research Proposal & Paper Assistant")

# --- Left Panel - Agent Customization ---
with st.sidebar:
    st.header("Agent Customization")
    num_agents = st.slider("Number of Agents", 1, 5, 2) # Example slider

    agent_configs = []
    for i in range(num_agents):
        st.subheader(f"Agent {i+1}")
        agent_name = st.text_input(f"Agent Name (Optional)", f"Agent {i+1}", key=f"agent_name_{i}")
        agent_role = st.selectbox(f"Role", ["Researcher", "Reviewer"], key=f"agent_role_{i}")
        llm_provider = st.selectbox(f"LLM Provider", ["openai", "anthropic", "google_gemini"], key=f"llm_provider_{i}")
        model_options = llm_models.get(llm_provider, []) # Get models for selected provider
        llm_model = st.selectbox(f"Model", model_options, key=f"llm_model_{i}")
        instruction_prompt = st.text_area(f"Instruction Prompt", "", height=100, key=f"instruction_prompt_{i}")
        agent_configs.append({
            'agent_name': agent_name,
            'role': agent_role,
            'llm_provider': llm_provider,
            'llm_model': llm_model,
            'instruction_prompt': instruction_prompt
        })

    st.header("Workflow")
    workflow_type = st.selectbox("Workflow Type", ["sequential", "parallel"], index=0) # Example workflow type selection

# --- Right Panel - WYSIWYG Editor & Markdown Output ---
col1, col2 = st.columns(2)

with col1:
    st.header("Input Topic & Run Workflow")
    research_topic = st.text_input("Research Topic", "AI in Healthcare")
    if st.button("Run Workflow"):
        with st.spinner("Workflow Running..."): # Feedback during workflow
            output_results = run_workflow(research_topic, agent_configs, workflow_type) # Call backend function
            st.session_state.markdown_output = "\n\n".join(output_results) # Store output for display

with col2:
    st.header("Output (Markdown)")
    if "markdown_output" in st.session_state:
        st.markdown(st.session_state.markdown_output) # Display markdown output
    else:
        st.write("Workflow output will be displayed here.")