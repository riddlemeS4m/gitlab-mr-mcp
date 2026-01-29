# GitLab MR Creator MCP Server

A simple FastMCP server that creates GitLab merge requests from Cursor (or any MCP client).

## Setup

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your values
```

4. **Verify glab is installed and authenticated:**
```bash
glab auth status
```

## Running the Server

```bash
source venv/bin/activate
python -m fastmcp run server.py
```

## Adding to Cursor

Add this to your Cursor MCP settings (`~/.cursor/config.json` or similar):

```json
{
  "mcpServers": {
    "gitlab-mr": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "fastmcp", "run", "/path/to/server.py"],
      "env": {
        "GITLAB_USERNAME": "your_username",
        "PROJECT_DIR": "/path/to/your/project",
        "TARGET_BRANCH": "staging"
      }
    }
  }
}
```

Or use a simpler approach with a shell script wrapper that loads the .env.

## Usage in Cursor

Once configured, you can ask Cursor:
- "Create an MR titled 'Fix user login bug' with description 'Resolves issue with OAuth flow'"
- "Make a merge request for this feature"

Cursor will call the `create_merge_request` tool with the title and description parameters.

## What it Does

- Pushes your current branch to origin (sets upstream if needed)
- Creates a GitLab MR with:
  - Your specified title and description
  - Source: current branch
  - Target: staging (or configured branch)
  - Assignee: you
  - Delete source branch after merge enabled
