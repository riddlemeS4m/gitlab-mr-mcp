import os
import subprocess
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("gitlab-mr-creator")

@mcp.tool()
def health_check() -> str:
    """
    Checks if the MCP server and dependencies are working correctly.
    
    Returns:
        Status message indicating server health and configuration
    """
    issues = []
    
    # Check environment variables
    username = os.getenv("GITLAB_USERNAME")
    project_dir = os.getenv("PROJECT_DIR")
    target_branch = os.getenv("TARGET_BRANCH", "staging")
    
    if not username:
        issues.append("❌ GITLAB_USERNAME not set")
    else:
        issues.append(f"✓ GITLAB_USERNAME: {username}")
    
    if not project_dir:
        issues.append("❌ PROJECT_DIR not set")
    else:
        if os.path.exists(project_dir):
            issues.append(f"✓ PROJECT_DIR: {project_dir}")
        else:
            issues.append(f"❌ PROJECT_DIR does not exist: {project_dir}")
    
    issues.append(f"✓ TARGET_BRANCH: {target_branch}")
    
    # Check if glab is available
    try:
        result = subprocess.run(
            ["glab", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            issues.append("✓ glab authenticated")
        else:
            issues.append("❌ glab not authenticated")
    except FileNotFoundError:
        issues.append("❌ glab command not found")
    except Exception as e:
        issues.append(f"❌ glab check failed: {str(e)}")
    
    # Check git availability
    try:
        subprocess.run(
            ["git", "--version"],
            capture_output=True,
            check=True,
            timeout=5
        )
        issues.append("✓ git available")
    except:
        issues.append("❌ git not available")
    
    return "GitLab MR Creator - Health Check\n" + "\n".join(issues)

@mcp.tool()
def create_merge_request(title: str, description: str) -> str:
    """
    Creates a GitLab merge request for the current branch.
    
    Args:
        title: The title of the merge request
        description: The description/body of the merge request
    
    Returns:
        A message indicating success or failure with the MR URL
    """
    try:
        # Get config from environment
        username = os.getenv("GITLAB_USERNAME")
        project_dir = os.getenv("PROJECT_DIR")
        target_branch = os.getenv("TARGET_BRANCH", "staging")
        
        if not username or not project_dir:
            return "Error: GITLAB_USERNAME and PROJECT_DIR must be set in .env"
        
        # Change to project directory
        os.chdir(project_dir)
        
        # Get current branch name
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True
        )
        source_branch = result.stdout.strip()
        
        if not source_branch:
            return "Error: Could not determine current branch"
        
        # Push branch and set upstream if needed
        push_result = subprocess.run(
            ["git", "push", "-u", "origin", source_branch],
            capture_output=True,
            text=True
        )
        
        if push_result.returncode != 0:
            return f"Error pushing branch: {push_result.stderr}"
        
        # Create merge request using glab
        mr_result = subprocess.run(
            [
                "glab", "mr", "create",
                "--title", title,
                "--description", description,
                "--source-branch", source_branch,
                "--target-branch", target_branch,
                "--assignee", username,
                "--remove-source-branch",
                "--draft",
                "--yes"  # Skip confirmation
            ],
            capture_output=True,
            text=True
        )
        
        if mr_result.returncode != 0:
            return f"Error creating MR: {mr_result.stderr}"
        
        return f"Successfully created merge request!\n\n{mr_result.stdout}"
        
    except subprocess.CalledProcessError as e:
        return f"Command failed: {e.stderr if e.stderr else str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
