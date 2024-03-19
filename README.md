# Signal

For Developers: Streamline Your Workflow with AI

## Pain Point

As developers, we're all too familiar with the constant juggling between Slack messages and the nagging question: "Did I reply? Is there something urgent I need to reply to?" On top of that, there's the inefficiency of higher-ups asking for project updates that are readily available in Jira. These distractions hinder our focus and productivity.

## Our Solution

We're building an open-source Python-based solution that employs a Retrieval-Augmented Generation (RAG) pipeline with OpenAI agents to address these exact challenges.

Our project aims to:

- Equip an agent with Jira and Slack tools to automatically manage communications and highlight urgent messages.
- Leverage cutting-edge AI tools from OpenAI to streamline workflows and enhance decision-making processes.

## Getting Started

### Prerequisites

- GitHub Codespaces or a local development environment with Python.
- VSCode (recommended for ease of use with Codespaces).

### Setup

1.**Clone the repository:**

Clone the repository to your local machine or directly in GitHub Codespaces.

```bash
git clone https://github.com/your-repository/Signal.git
```

2.**Environment Setup:**

The environment setup is automated through a post_create.sh script in the devcontainer, which prepares the Conda environment named venv.

3.**Activate the Conda Environment:**

After the devcontainer setup completes, you should open a new terminal in VSCode and activate the environment:

```bash
source activate venv
```

This step ensures that you are working within the context of the project's specified dependencies and Python version.

4.**Using VSCode Tasks:**

Access and run tasks configured in .vscode/tasks.json from the VSCode Command Palette.

5.**Developing in Codespaces:**

- For Codespaces users, the .devcontainer/devcontainer.json file automates the environment setup.
- Open the project in Codespaces for automatic configuration.

### Running the Project

Execute main.py to run the project, either through the terminal or using the VSCode launcher.

### Join Us

Ready to make a difference? Join us in developing this game-changing tool. Whether you're contributing code, ideas, or feedback, your input is invaluable. Let's revolutionize the way we manage our workflows and communicate within our teams. Join the project now!
