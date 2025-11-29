# 📧 Digital Declutter Assistant
### Google x Kaggle Agent Intensive Course - Capstone Project

![Project Status](https://img.shields.io/badge/Status-Complete-success)
![Tech Stack](https://img.shields.io/badge/Stack-React_|_FastAPI_|_Gemini_|_MCP-blue)

A smart, AI-powered assistant that bridges the gap between your **Gmail Inbox** and **Notion Task Manager**. Built with Google's Agent Development Kit (ADK) and Gemini 2.5 Flash Lite, it autonomously triages emails, summarizes threads, and creates actionable tasks in Notion.

---

## 🎯 Problem Statement
In the modern digital workflow, important tasks often get buried in a flood of emails. Users struggle to:
1.  **Filter Noise**: Distinguish between critical updates and promotional spam.
2.  **Bridge Context**: Manually copying information from emails to task managers (like Notion) is tedious and error-prone.
3.  **Maintain Focus**: Switching context between email and project management tools kills productivity.

## 💡 Solution
The **Digital Declutter Assistant** is an intelligent agent that lives in a chat interface. It acts as a concierge for your digital life:
*   **Intelligent Triage**: Fetches and summarizes emails, highlighting what's actually important based on your preferences.
*   **Actionable Workflows**: Converts emails into Notion tasks with a single command (or autonomously).
*   **Context Awareness**: Remembers your rules (e.g., "Always mark emails from 'Boss' as important") across sessions.

---

## 🎓 Course Learnings Applied
This project demonstrates key concepts from the **Google x Kaggle Agent Intensive Course**:

*   **Reasoning Loops**: The agent uses a "Fetch -> Analyze -> Plan -> Execute" loop to handle complex user requests (e.g., "Find the email from John and create a task for it").
*   **Tool Use (Function Calling)**:
    *   **Custom Tools**: Built bespoke Python tools for Gmail API interactions (Fetch, Label, Trash).
    *   **Model Context Protocol (MCP)**: Implemented a **Python-based MCP Server** to integrate with Notion, demonstrating the future of standardized tool interoperability.
*   **Human-in-the-Loop**: The agent is designed to ask for confirmation before taking destructive actions (like deleting emails) or when requirements are ambiguous.
*   **Multi-Modal Inputs**: The underlying Gemini model can process rich text and context from emails to generate high-quality summaries.

---

## 🏗️ Architecture

The application follows a modern **Client-Server** architecture:

1.  **Frontend**:
    *   **React + Vite**: A fast, responsive Single Page Application (SPA).
    *   **Tailwind CSS**: Styled to mimic the clean, familiar aesthetic of Gmail.
    *   **Chat Interface**: Real-time interaction with the agent.

2.  **Backend**:
    *   **FastAPI (Python)**: Hosts the Agent and exposes a REST API (`/chat`).
    *   **Google ADK**: Manages the agent's lifecycle, session state, and tool execution.
    *   **Lazy Initialization**: Optimized startup to handle MCP server connections robustly.

3.  **Integrations**:
    *   **Gmail API**: Direct integration via Google Client Library.
    *   **Notion API**: Integrated via a custom **Python MCP Server** (`mcp_server_notion.py`).

---

## 🚀 Setup Guide

Since this project handles sensitive data (emails, tasks), all credentials are **gitignored**. Follow these steps to set up your local environment.

### Prerequisites
*   Python 3.10+
*   Node.js & npm
*   Google Cloud Project with **Gmail API** enabled.
*   Notion Integration Token.

### 1. Clone the Repository
```bash
git clone https://github.com/ayush2599/Digital-Declutter-Assistant.git
cd Digital-Declutter-Assistant
```

### 2. Backend Configuration
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key
NOTION_API_KEY=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id
```

**Gmail Credentials:**
1.  Download your OAuth 2.0 Client ID JSON from Google Cloud Console.
2.  Save it as `digital_declutter/credentials.json`.
3.  *Note: On first run, the app will open a browser to authenticate you and generate `digital_declutter/token.json`.*

### 3. Install Dependencies

**Backend:**
```bash
pip install -r digital_declutter/requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 4. Run the Application

**Step 1: Start the Backend**
Open a terminal in the root directory:
```bash
python backend/server.py
```
*Wait for the server to start on `http://127.0.0.1:8000`.*

**Step 2: Start the Frontend**
Open a new terminal in the `frontend` directory:
```bash
npm run dev
```
*The app will open at `http://localhost:5173`.*

---

## 🎮 How to Use

1.  **Fetch Emails**:
    > "Fetch my emails from the last 3 days."
    > "Show me unread emails from 'Zerodha'."

2.  **Create Tasks**:
    > "Create a task in Notion for the email about the project deadline."
    > "Add a task 'Buy Groceries' with description 'Milk, Eggs, Bread'."

3.  **Manage Rules**:
    > "Emails from 'HR' are always important."
    > "Archive all newsletters from 'Marketing'."

---

## 📂 Project Structure
```
├── backend/
│   └── server.py           # FastAPI Server & Agent Runner
├── digital_declutter/
│   ├── agent.py            # Agent Logic & Prompt Design
│   ├── tools/              # Custom Gmail Tools
│   └── preferences.py      # User Preference Management
├── frontend/               # React Application
├── mcp_server_notion.py    # Python MCP Server for Notion
├── mcp_config.json         # MCP Configuration
└── requirements.txt        # Python Dependencies
```

---

*Built with ❤️ by Ayush for the Google x Kaggle Agent Intensive Course.*
