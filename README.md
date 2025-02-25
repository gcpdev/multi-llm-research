# Multi-LLM Research Assistant with CrewAI - setup Instructions

This application consists of a Python backend using CrewAI and a React frontend. Here's how to set up and run both components.

## Backend Setup

1. **Create a virtual environment and install dependencies**:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

2. **Create a `.env` file** with your API keys:

```
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
```

3. **Run the FastAPI backend**:

```bash
uvicorn backend:app --reload
```

The API will be available at http://localhost:8000.

## Frontend Setup

1. **Create a new React app** (if not already done):

```bash
npx create-react-app frontend
cd frontend
```

2. **Install additional dependencies**:

```bash
npm install lucide-react
```

3. **Replace the contents of `frontend/src/App.js`** with the React component code `frontend.tsx`.

4. **Start the React development server**:

```bash
npm start
```

The UI will be available at http://localhost:3000.

## Using the Application

1. Enter a research topic in the input field
2. Configure up to 5 AI agents:
   - Assign names, models, and roles
   - Provide specific instructions
3. Build your workflow by adding agents in sequence
4. Click "Run Workflow" to start the process
5. View the results in the document editor

## System Architecture

This application follows a client-server architecture:

1. The **React frontend** provides the user interface for configuring agents and workflows
2. The **FastAPI backend** handles workflow execution using CrewAI
3. **CrewAI** orchestrates the agents to perform research and review tasks
4. **LangChain** integrations connect to various LLM providers (OpenAI, Anthropic, Google)

## Extending the Application

You can extend this application by:

1. Adding more agent roles (e.g., editor, fact-checker)
2. Implementing file upload/download for research papers
3. Adding collaboration features
4. Integrating with reference management systems