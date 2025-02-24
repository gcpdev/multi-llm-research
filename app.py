import streamlit as st
import time
import json
import logging
import traceback
from crewai import Crew, Process
from agents import create_agent  # now imported from agents.py
from tasks import create_task  # imported from tasks.py

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('research_assistant')

# Set page config
st.set_page_config(layout="wide", page_title="Research Assistant")

openai_models = ["chatgpt-4o-latest", "o3-mini", "o1"]
anthropic_models = ["claude-3-5-haiku-latest", "claude-3-5-sonnet-latest"]
google_models = ["gemini-2.0-flash", "gemini-2.0-flash-lite-preview-02-05"]
xai_models = ["grok-2-latest"]

# Initialize session state
if "editor_content" not in st.session_state:
    st.session_state.editor_content = "# Research Document\n\nStart editing your document here or use the AI agents to generate content."
if "agents" not in st.session_state:
    st.session_state.agents = []
if "workflow_running" not in st.session_state:
    st.session_state.workflow_running = False
if "workflow_steps" not in st.session_state:
    st.session_state.workflow_steps = []
if "edit_agent_id" not in st.session_state:
    st.session_state.edit_agent_id = None
if "debug_output" not in st.session_state:
    st.session_state.debug_output = []

# CSS for better UI
st.markdown("""
<style>
    .agent-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .workflow-arrow {
        text-align: center;
        font-size: 24px;
        margin: 10px 0;
    }
    .main-header {
        font-size: 1.8rem;
        margin-bottom: 20px;
    }
    .panel-header {
        font-size: 1.4rem;
        margin-bottom: 15px;
    }
    .running-indicator {
        background-color: #ffecb3;
        padding: 20px;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 15px;
    }
    .debug-console {
        background-color: #282c34;
        color: #abb2bf;
        font-family: monospace;
        padding: 10px;
        border-radius: 5px;
        max-height: 200px;
        overflow-y: auto;
        margin-top: 20px;
    }
    .debug-line {
        margin: 2px 0;
        padding: 2px 5px;
    }
    .debug-info {
        color: #98c379;
    }
    .debug-error {
        color: #e06c75;
    }
    .debug-warning {
        color: #e5c07b;
    }
    .role-researcher {
        border-left: 5px solid #4caf50;
        padding-left: 10px;
    }
    .role-reviewer {
        border-left: 5px solid #2196f3;
        padding-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function for debug logging
def add_debug_log(message, level="info"):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.debug_output.append({
        "timestamp": timestamp,
        "message": message,
        "level": level
    })
    if level == "error":
        logger.error(message)
    elif level == "warning":
        logger.warning(message)
    else:
        logger.info(message)

# Create CrewAI crew from agents and workflow steps
def create_crew(workflow_steps, agents_config, document_content):
    add_debug_log("Creating CrewAI workflow")
    try:
        crew_agents = {}
        # Create agents from configuration using the refactored agents.py helper
        for agent_config in agents_config:
            add_debug_log(f"Setting up agent: {agent_config['name']} ({agent_config['role']})")
            agent = create_agent(agent_config)
            crew_agents[agent_config['id']] = agent

        # Create tasks for each workflow step using tasks.py helper
        tasks = []
        for idx, step in enumerate(workflow_steps):
            agent_config = next(a for a in agents_config if a['id'] == step['agent_id'])
            agent = crew_agents[agent_config['id']]
            add_debug_log(f"Creating task for step {idx+1}: {agent_config['name']}")
            add_debug_log(f"Agent: {agent}")
            add_debug_log(f"Agent repr: {repr(agent)}")
            task = create_task(idx, step, agent_config, agent, document_content, tasks)
            tasks.append(task)
        add_debug_log(list(crew_agents.values()))
        crew = Crew(
            agents=list(crew_agents.values()),
            tasks=tasks,
            verbose=True,
            process=Process.sequential
        )
        add_debug_log(f"CrewAI workflow created with {len(tasks)} tasks and {len(crew_agents)} agents")
        return crew
    except Exception as e:
        error_msg = f"Error creating CrewAI workflow: {str(e)}"
        add_debug_log(error_msg, "error")
        add_debug_log(traceback.format_exc(), "error")
        raise Exception(error_msg)

# Function to run workflow
def run_workflow():
    total_steps = len(st.session_state.workflow_steps)
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Clear previous debug logs for this run
        st.session_state.debug_output = []
        add_debug_log("Starting workflow execution")
        
        status_text.text("Setting up AI crew...")
        add_debug_log("Creating CrewAI setup")
        
        crew = create_crew(
            workflow_steps=st.session_state.workflow_steps,
            agents_config=st.session_state.agents,
            document_content=st.session_state.editor_content
        )
        
        status_text.text("Starting document processing...")
        progress_bar.progress(0.1)
        add_debug_log("Executing CrewAI workflow")
        
        # Execute the workflow with progress updates
        def progress_callback(task_id, agent_name, progress):
            progress_value = 0.1 + (progress * 0.9)
            progress_bar.progress(progress_value)
            status_text.text(f"Processing step {task_id+1}/{total_steps} with agent {agent_name}...")
            add_debug_log(f"Workflow progress: {int(progress * 100)}% on task {task_id+1}")
        
        add_debug_log("Starting workflow kickoff")
        result = crew.kickoff()
        
        add_debug_log(f"Workflow completed with result length: {len(result.raw)} characters")
        st.session_state.editor_content = result.raw
        progress_bar.progress(1.0)
        status_text.text("Workflow completed successfully!")
        add_debug_log("Workflow execution successful", "info")
    except Exception as e:
        error_msg = f"Error executing workflow: {str(e)}"
        progress_bar.progress(1.0)
        status_text.text(f"Error executing workflow: {str(e)}")
        st.error(f"Workflow failed: {str(e)}")
        add_debug_log(error_msg, "error")
        add_debug_log(traceback.format_exc(), "error")
    
    time.sleep(2)
    st.session_state.workflow_running = False
    st.rerun()

# Main header
st.markdown('<div class="main-header">Research Assistant Powered by CrewAI</div>', unsafe_allow_html=True)

# Create two columns for the layout
left_col, right_col = st.columns([1, 1])

with left_col:
    st.markdown('<div class="panel-header">Configure AI Agents & Workflow</div>', unsafe_allow_html=True)
    
    # Edit existing agent
    if st.session_state.edit_agent_id is not None:
        edit_idx = st.session_state.edit_agent_id
        if 0 <= edit_idx < len(st.session_state.agents):
            agent = st.session_state.agents[edit_idx]
            st.markdown(f"### Edit Agent #{edit_idx+1}")
            
            agent_name = st.text_input("Agent Name", value=agent['name'], key=f"edit_name_{edit_idx}")
            agent_role = st.selectbox(
                "Agent Role",
                ["Researcher", "Reviewer"],
                index=0 if agent.get('role', '') == "Researcher" else 1,
                key=f"edit_role_{edit_idx}"
            )
            agent_provider = st.selectbox(
                "LLM Provider",
                ["OpenAI", "Anthropic Claude", "Google Gemini", "Grok"],
                index=["OpenAI", "Anthropic Claude", "Google Gemini", "Grok"].index(agent['provider']),
                key=f"edit_provider_{edit_idx}"
            )
            
            if agent_provider == "OpenAI":
                models = openai_models
                default_idx = models.index(agent['model']) if agent['model'] in models else 0
                agent_model = st.selectbox("Model", models, index=default_idx, key=f"edit_model_{edit_idx}")
            elif agent_provider == "Anthropic Claude":
                models = anthropic_models
                default_idx = models.index(agent['model']) if agent['model'] in models else 0
                agent_model = st.selectbox("Model", models, index=default_idx, key=f"edit_model_{edit_idx}")
            elif agent_provider == "Google Gemini":
                models = google_models
                default_idx = models.index(agent['model']) if agent['model'] in models else 0
                agent_model = st.selectbox("Model", models, index=default_idx, key=f"edit_model_{edit_idx}")
            elif agent_provider == "Grok":
                models = xai_models
                default_idx = models.index(agent['model']) if agent['model'] in models else 0
                agent_model = st.selectbox("Model", models, index=default_idx, key=f"edit_model_{edit_idx}")
            
            # Use agent instructions already stored
            default_instructions = agent.get('instructions')
            agent_instructions = st.text_area(
                "Agent Instructions",
                value=default_instructions,
                height=150,
                key=f"edit_instructions_{edit_idx}"
            )
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Save Changes"):
                    st.session_state.agents[edit_idx] = {
                        "id": agent['id'],
                        "name": agent_name,
                        "role": agent_role,
                        "provider": agent_provider,
                        "model": agent_model,
                        "instructions": agent_instructions
                    }
                    st.session_state.edit_agent_id = None
                    add_debug_log(f"Updated agent: {agent_name} (ID: {agent['id']})")
                    st.rerun()
            with col2:
                if st.button("Cancel Editing"):
                    st.session_state.edit_agent_id = None
                    st.rerun()
    else:
        with st.expander("Add New Agent", expanded=len(st.session_state.agents) == 0):
            agent_name = st.text_input("Agent Name", value="Research Assistant")
            agent_role = st.selectbox(
                "Agent Role",
                ["Researcher", "Reviewer"]
            )
            agent_provider = st.selectbox(
                "LLM Provider",
                ["OpenAI", "Anthropic Claude", "Google Gemini", "Grok"]
            )
            
            if agent_provider == "OpenAI":
                agent_provider = "openai"
                agent_model = st.selectbox("Model", openai_models)
            elif agent_provider == "Anthropic Claude":
                agent_provider = "anthropic"
                agent_model = st.selectbox("Model", anthropic_models)
            elif agent_provider == "Google Gemini":
                agent_provider = "gemini"
                agent_model = st.selectbox("Model", google_models)
            elif agent_provider == "Grok":
                agent_provider = "xai"
                agent_model = st.selectbox("Model", xai_models)
            
            # Use default instructions from agents.py (via get_role_instructions in create_agent)
            from agents import get_role_instructions
            default_instructions = get_role_instructions(agent_role)
            agent_instructions = st.text_area(
                "Agent Instructions",
                value=default_instructions,
                height=150
            )
            
            if st.button("Add Agent") and len(st.session_state.agents) < 5:
                new_agent = {
                    "id": len(st.session_state.agents),
                    "name": agent_name,
                    "role": agent_role,
                    "provider": agent_provider,
                    "model": agent_model,
                    "instructions": agent_instructions
                }
                st.session_state.agents.append(new_agent)
                add_debug_log(f"Added new agent: {agent_name} ({agent_role})")
                st.rerun()
    
        if st.session_state.agents:
            st.markdown("### Configured Agents")
            for i, agent in enumerate(st.session_state.agents):
                role_class = "role-researcher" if agent.get('role') == "Researcher" else "role-reviewer"
                st.markdown(f"""
                <div class="agent-card {role_class}">
                    <strong>{agent['name']}</strong> ({agent['role']})
                    <p>Model: {agent['provider']} - {agent['model']}</p>
                    <p><em>{agent['instructions'][:100]}{'...' if len(agent['instructions']) > 100 else ''}</em></p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"Edit Agent #{i+1}"):
                        st.session_state.edit_agent_id = i
                        st.rerun()
                with col2:
                    if st.button(f"Remove Agent #{i+1}"):
                        st.session_state.agents.pop(i)
                        if st.session_state.workflow_steps:
                            filtered_steps = [step for step in st.session_state.workflow_steps 
                                              if step['agent_id'] < len(st.session_state.agents)]
                            st.session_state.workflow_steps = filtered_steps
                        add_debug_log(f"Removed agent ID {i}")
                        st.rerun()
    
        if len(st.session_state.agents) >= 2:
            st.markdown("### Workflow Configuration")
            st.info("Define the sequence of agents to process your research document")
            
            if st.button("Reset Workflow"):
                st.session_state.workflow_steps = []
                add_debug_log("Workflow configuration reset")
                st.rerun()
            
            if len(st.session_state.workflow_steps) < len(st.session_state.agents):
                step_num = len(st.session_state.workflow_steps) + 1
                st.markdown(f"**Step {step_num}:**")
                
                used_agent_ids = [step['agent_id'] for step in st.session_state.workflow_steps]
                available_agents = [a for a in st.session_state.agents if a['id'] not in used_agent_ids]
                agent_options = {f"{a['name']} ({a['role']})": a['id'] for a in available_agents}
                
                if agent_options:
                    selected_agent_label = st.selectbox(
                        "Select Agent",
                        list(agent_options.keys()),
                        key=f"step_{step_num}_agent"
                    )
                    selected_agent_id = agent_options[selected_agent_label]
                    selected_agent = next(a for a in st.session_state.agents if a['id'] == selected_agent_id)
                    
                    default_task = ""
                    if selected_agent['role'] == "Researcher":
                        default_task = "Research and develop a comprehensive proposal on the following topic:"
                    elif selected_agent['role'] == "Reviewer":
                        default_task = "Review the document critically and provide full document markdown formatted with improvements addressed."
                    
                    task_description = st.text_area(
                        "Task Description", 
                        value=default_task,
                        key=f"step_{step_num}_task",
                        height=100
                    )
                    
                    if st.button("Add to Workflow"):
                        st.session_state.workflow_steps.append({
                            "agent_id": selected_agent_id,
                            "task": task_description
                        })
                        add_debug_log(f"Added workflow step {step_num}: Agent {selected_agent['name']}")
                        st.rerun()
            
            if st.session_state.workflow_steps:
                st.markdown("### Current Workflow")
                for i, step in enumerate(st.session_state.workflow_steps):
                    agent = next(a for a in st.session_state.agents if a['id'] == step['agent_id'])
                    role_class = "role-researcher" if agent.get('role') == "Researcher" else "role-reviewer"
                    st.markdown(f"""
                    <div class="agent-card {role_class}">
                        <strong>Step {i+1}:</strong> {agent['name']} ({agent['role']})
                        <p><em>Task: {step['task'][:100]}{'...' if len(step['task']) > 100 else ''}</em></p>
                    </div>
                    """, unsafe_allow_html=True)
                    if i < len(st.session_state.workflow_steps) - 1:
                        st.markdown('<div class="workflow-arrow">↓</div>', unsafe_allow_html=True)
                
                if st.button("Run Workflow", type="primary", disabled=st.session_state.workflow_running):
                    st.session_state.workflow_running = True
                    add_debug_log("Workflow execution initiated")
                    st.rerun()

with right_col:
    st.markdown('<div class="panel-header">Document Editor</div>', unsafe_allow_html=True)
    
    if st.session_state.workflow_running:
        st.markdown("""
        <div class="running-indicator">
            <h3>🔄 Workflow Running...</h3>
            <p>AI agents are processing your document. Please wait.</p>
        </div>
        """, unsafe_allow_html=True)
        run_workflow()
    
    if not st.session_state.workflow_running:
        editor_content = st.text_area(
            "Edit your document (Markdown supported)",
            value=st.session_state.editor_content,
            height=500
        )
        if editor_content != st.session_state.editor_content:
            st.session_state.editor_content = editor_content
            add_debug_log("Document content updated by user")
        
        st.markdown("### Document Preview")
        st.markdown(st.session_state.editor_content)
        
        with st.expander("Debug Console", expanded=False):
            st.markdown('<div class="debug-console">', unsafe_allow_html=True)
            for log in st.session_state.debug_output:
                level_class = f"debug-{log['level']}"
                st.markdown(f'<div class="debug-line {level_class}">[{log["timestamp"]}] {log["message"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("Clear Debug Logs"):
                st.session_state.debug_output = []
                st.rerun()

