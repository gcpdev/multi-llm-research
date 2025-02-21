# Research Assistant Powered by Multi-LLM Agents

## Overview

This Streamlit application is a Research Assistant that leverages AI agents to help you create and refine research documents. It allows you to configure AI agents with different roles (Researcher, Reviewer) powered by various Large Language Models (LLMs) from providers like OpenAI, Anthropic Claude, Google Gemini, and Grok. You can define a workflow by sequencing these agents to process your document, enhancing its quality through automated research and review steps.

## Features

*   **Agent Configuration:**
    *   Define multiple AI agents with distinct roles (Researcher, Reviewer, or custom).
    *   Choose from various LLM providers: OpenAI, Anthropic Claude, Google Gemini, and Grok.
    *   Select specific models offered by each provider.
    *   Customize agent instructions to fine-tune their behavior.
*   **Workflow Definition:**
    *   Create a sequential workflow by adding steps, each assigned to a configured agent.
    *   Define specific tasks for each agent in the workflow.
    *   Reset and reconfigure workflows easily.
*   **Document Editor:**
    *   Markdown-supported text editor for creating and modifying research documents.
    *   Real-time document preview to visualize Markdown formatting.
*   **Debug Console:**
    *   Detailed debug console to track the application's execution, including timestamps, messages, and error levels.
    *   Clear debug logs for each workflow run.
*   **Multi-LLM Support:**
    *   Experiment with different LLM providers and models to find the best performance for your research tasks.
*   **Agent Roles:**
    *   **Researcher:**  Generates comprehensive research proposals with standard academic sections.
    *   **Reviewer:** Critically reviews documents, providing feedback and suggestions for improvement in Markdown format.

## Directory Structure
```
gcpdev-multi-llm-research/
├── agents.py         # Defines AI agents and their configurations
├── app.py            # Streamlit application code (UI and workflow logic)
├── requirements.txt  # Python dependencies
└── tasks.py          # Defines tasks for AI agents in the workflow
```
*   **`agents.py`**: Contains functions for creating and configuring AI agents. This file handles the integration with different LLM providers and defines agent roles and instructions.
*   **`app.py`**:  The main Streamlit application file. It sets up the user interface, manages application state, defines the workflow execution logic, and integrates with the agent and task modules.
*   **`requirements.txt`**: Lists all Python packages required to run the application. This file is used by `pip` to install the necessary dependencies.
*   **`tasks.py`**: Defines functions for creating tasks that are assigned to agents in the workflow. Tasks specify the instructions and context for each agent's step in the document processing pipeline.

## Setup Instructions

Follow these steps to set up the Research Assistant application:

1.  **Clone the repository:**
    ```bash
    git clone [repository_url]
    cd gcpdev-multi-llm-research
    ```
    *(Replace `[repository_url]` with the actual URL of your repository)*

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Linux/macOS
    .venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Environment Variables:**
    The application requires API keys for the LLM providers you intend to use. You need to set these as environment variables. You can do this by creating a `.env` file in the repository root or by setting them directly in your shell environment.

    **Required Environment Variables:**

    *   `OPENAI_API_KEY`:  API key for OpenAI models (e.g., ChatGPT). Get it from [OpenAI API Keys](https://platform.openai.com/api-keys).
    *   `ANTHROPIC_API_KEY`: API key for Anthropic Claude models. Get it from [Anthropic Console](https://console.anthropic.com/).
    *   `GOOGLE_GEMINI_API_KEY`: API key for Google Gemini models. Get it from [Google AI Studio](https://makersuite.google.com/app/apikey).
    *   `GROK_API_KEY`: API key for Grok models (xAI). Instructions for accessing Grok API can be found on [Grok API Documentation](https://x.ai/api).

    **Example `.env` file:**
    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ANTHROPIC_API_KEY=your_anthropic_api_key_here
    GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key_here
    GROK_API_KEY=your_grok_api_key_here
    ```

5.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
    This command will start the Streamlit app, and you can access it in your browser, usually at `http://localhost:8501`.

## Usage Instructions

1.  **Configure AI Agents:**
    *   In the left sidebar under "Configure AI Agents & Workflow", you can add new agents or edit existing ones.
    *   For each agent, specify:
        *   **Agent Name:** A descriptive name for the agent.
        *   **Agent Role:** Select a role ("Researcher" or "Reviewer").
        *   **LLM Provider:** Choose the LLM provider (OpenAI, Anthropic Claude, Google Gemini, Grok).
        *   **Model:** Select a specific model from the chosen provider.
        *   **Agent Instructions:**  Customize the agent's instructions (optional, defaults are provided based on the role).
    *   You can add up to 5 agents.
    *   Edit or remove agents using the buttons below the agent configurations.

2.  **Define Workflow:**
    *   After configuring at least two agents, the "Workflow Configuration" section will appear.
    *   Click "Reset Workflow" to clear any existing workflow steps.
    *   For each step in the workflow:
        *   Select an agent from the "Select Agent" dropdown (only agents not yet used in the workflow are available).
        *   Enter a "Task Description" for the selected agent.
        *   Click "Add to Workflow" to add the step to the workflow sequence.
    *   The "Current Workflow" section will display the configured steps.

3.  **Edit Document:**
    *   In the right sidebar under "Document Editor", you'll find a Markdown editor.
    *   Start writing or paste your research document into the editor.
    *   The "Document Preview" below the editor will render your document in Markdown format.

4.  **Run Workflow:**
    *   Once you have configured agents, defined a workflow, and have content in the document editor, click the "Run Workflow" button in the left sidebar.
    *   A progress indicator will appear, and the debug console (expandable at the bottom of the right sidebar) will show execution logs.
    *   After the workflow is completed, the document editor will be updated with the processed content from the AI agents.

5.  **Review and Iterate:**
    *   Review the updated document in the editor and preview.
    *   You can further edit the document manually or re-run the workflow with the same or modified configurations.
    *   Use the debug console to troubleshoot or understand the workflow execution.

## Environment Variables

*   **`OPENAI_API_KEY`**
*   **`ANTHROPIC_API_KEY`**
*   **`GOOGLE_GEMINI_API_KEY`**
*   **`GROK_API_KEY`**

    **Note:** Ensure you have set up accounts and obtained API keys from the respective LLM providers to use their models within this application.

## License

[MIT License]

## Contact

[Gustavo Publio]
[linkedin.com/in/gustavopublio](https://www.linkedin.com/in/gustavopublio/)

---

This README provides a starting point. You can customize it further to include more details, screenshots, or advanced usage instructions as needed.
