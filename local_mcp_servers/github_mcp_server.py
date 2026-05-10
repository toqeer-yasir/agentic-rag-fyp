import os
import sys
import tempfile
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("GitHub")

try:
    from github import Github, GithubException
    import git
except ImportError:
    print("Error: Required packages not installed.")
    print("Run: pip install PyGithub gitpython python-dotenv fastmcp")
    sys.exit(1)

GITHUB_TOKEN = os.getenv("GITHUB_PAT")
if not GITHUB_TOKEN:
    print("Error: GITHUB_PERSONAL_ACCESS_TOKEN not found in .env file")
    sys.exit(1)

try:
    g = Github(GITHUB_TOKEN)
    user = g.get_user()
    print(f"✅ Connected to GitHub as: {user.login}")
except Exception as e:
    print(f"❌ Failed to connect to GitHub: {e}")
    sys.exit(1)


# ==================== EXPLORE GITHUB (READ-ONLY) ====================

@mcp.tool()
def github_search_users(query: str, limit: int = 8) -> List[Dict[str, Any]]:
    """Search for GitHub users by username, name, or email."""
    try:
        users = []
        for github_user in g.search_users(query)[:limit]:
            try:
                full_user = g.get_user(github_user.login)
                users.append({
                    "username": full_user.login,
                    "name": full_user.name or "Not set",
                    "bio": full_user.bio or "No bio",
                    "company": full_user.company or "Not set",
                    "location": full_user.location or "Not set",
                    "followers": full_user.followers,
                    "public_repos": full_user.public_repos,
                    "avatar_url": full_user.avatar_url,
                    "profile_url": full_user.html_url
                })
            except:
                continue
        return users
    except Exception as e:
        return [{"error": f"Failed to search users: {str(e)}"}]


@mcp.tool()
def github_get_user_profile(username: str) -> Dict[str, Any]:
    """Get profile information of any GitHub user."""
    try:
        target_user = g.get_user(username)
        return {
            "username": target_user.login,
            "name": target_user.name or "Not set",
            "bio": target_user.bio or "No bio",
            "company": target_user.company or "Not set",
            "location": target_user.location or "Not set",
            "followers": target_user.followers,
            "following": target_user.following,
            "public_repos": target_user.public_repos,
            "created_at": target_user.created_at.strftime("%Y-%m-%d"),
            "avatar_url": target_user.avatar_url,
            "profile_url": target_user.html_url
        }
    except GithubException as e:
        return {"error": f"User '{username}' not found"}
    except Exception as e:
        return {"error": f"Failed to get user profile: {str(e)}"}


@mcp.tool()
def github_get_user_repositories(username: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get repositories of any GitHub user."""
    try:
        target_user = g.get_user(username)
        repos = []
        for repo in target_user.get_repos()[:limit]:
            repos.append({
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description or "No description",
                "private": repo.private,
                "language": repo.language or "Not specified",
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "updated_at": repo.updated_at.strftime("%Y-%m-%d"),
                "url": repo.html_url
            })
        return repos
    except Exception as e:
        return [{"error": f"Failed to get user repositories: {str(e)}"}]


@mcp.tool()
def github_get_repository_details(owner: str, repo_name: str) -> Dict[str, Any]:
    """Get details of any public repository."""
    try:
        repo = g.get_repo(f"{owner}/{repo_name}")
        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description or "No description",
            "owner": repo.owner.login,
            "private": repo.private,
            "language": repo.language or "Not specified",
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "open_issues": repo.open_issues_count,
            "default_branch": repo.default_branch,
            "updated_at": repo.updated_at.strftime("%Y-%m-%d"),
            "url": repo.html_url,
            "clone_url": repo.clone_url
        }
    except GithubException as e:
        return {"error": f"Repository '{owner}/{repo_name}' not found"}
    except Exception as e:
        return {"error": f"Failed to get repository details: {str(e)}"}


@mcp.tool()
def github_browse_repository_files(owner: str, repo_name: str, path: str = "") -> List[Dict[str, Any]]:
    """Browse files and directories in a repository."""
    try:
        repo = g.get_repo(f"{owner}/{repo_name}")
        contents = repo.get_contents(path)
        
        if isinstance(contents, list):
            return [{
                "name": item.name,
                "path": item.path,
                "type": item.type,
                "size": f"{item.size:,} bytes" if item.size else "N/A",
                "url": item.html_url
            } for item in contents]
        else:
            return [{
                "name": contents.name,
                "path": contents.path,
                "type": contents.type,
                "size": f"{contents.size:,} bytes" if contents.size else "N/A",
                "content": contents.decoded_content.decode('utf-8')[:2000] + "..." 
                          if contents.type == "file" and contents.size < 50000 else "[Content preview not available]",
                "url": contents.html_url
            }]
    except GithubException as e:
        return [{"error": f"Cannot access '{path}' in '{owner}/{repo_name}'"}]
    except Exception as e:
        return [{"error": f"Failed to browse files: {str(e)}"}]


@mcp.tool()
def github_search_repositories(query: str, limit: int = 8) -> List[Dict[str, Any]]:
    """Search for repositories on GitHub."""
    try:
        repos = []
        for repo in g.search_repositories(query)[:limit]:
            repos.append({
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description or "No description",
                "owner": repo.owner.login,
                "language": repo.language or "Not specified",
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "updated_at": repo.updated_at.strftime("%Y-%m-%d"),
                "url": repo.html_url
            })
        return repos
    except Exception as e:
        return [{"error": f"Failed to search repositories: {str(e)}"}]


# ==================== MY PROFILE & REPOSITORIES ====================

@mcp.tool()
def github_get_my_profile() -> Dict[str, Any]:
    """Get your GitHub profile information."""
    try:
        return {
            "username": user.login,
            "name": user.name or "Not set",
            "email": user.email or "Not public",
            "bio": user.bio or "No bio",
            "location": user.location or "Not set",
            "company": user.company or "Not set",
            "public_repos": user.public_repos,
            "followers": user.followers,
            "following": user.following,
            "avatar_url": user.avatar_url,
            "profile_url": user.html_url
        }
    except Exception as e:
        return {"error": f"Failed to get profile: {str(e)}"}


@mcp.tool()
def github_list_my_repositories(limit: int = 15) -> List[Dict[str, Any]]:
    """List repositories in your GitHub account."""
    try:
        repos = []
        for repo in user.get_repos()[:limit]:
            repos.append({
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description or "No description",
                "private": repo.private,
                "language": repo.language or "Not specified",
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "updated_at": repo.updated_at.strftime("%Y-%m-%d"),
                "url": repo.html_url
            })
        return repos
    except Exception as e:
        return [{"error": f"Failed to list repositories: {str(e)}"}]


# ==================== LOCAL GIT OPERATIONS ====================

@mcp.tool()
def git_check_status(local_path: str) -> Dict[str, Any]:
    """Check the status of a local git repository."""
    try:
        if not os.path.exists(local_path):
            return {"error": f"Local path does not exist: {local_path}"}
        
        if not os.path.exists(os.path.join(local_path, '.git')):
            return {"error": f"Not a git repository: {local_path}"}
        
        repo = git.Repo(local_path)
        
        # Get detailed status
        status_output = repo.git.status()
        
        # Get current branch
        try:
            current_branch = repo.active_branch.name
        except:
            current_branch = "DETACHED HEAD"
        
        # Get changes
        staged_files = []
        unstaged_files = []
        untracked_files = list(repo.untracked_files)[:10]
        
        # Parse status for staged/unstaged
        if repo.is_dirty():
            diff_staged = repo.git.diff('--cached', '--name-only')
            diff_unstaged = repo.git.diff('--name-only')
            
            staged_files = diff_staged.split('\n') if diff_staged else []
            unstaged_files = diff_unstaged.split('\n') if diff_unstaged else []
        
        return {
            "local_path": local_path,
            "is_git_repo": True,
            "current_branch": current_branch,
            "has_uncommitted_changes": repo.is_dirty(),
            "has_untracked_files": len(untracked_files) > 0,
            "staged_files": [f for f in staged_files if f][:10],
            "unstaged_files": [f for f in unstaged_files if f][:10],
            "untracked_files": untracked_files,
            "status_summary": status_output[:300] + "..." if len(status_output) > 300 else status_output
        }
    except Exception as e:
        return {"error": f"Failed to check git status: {str(e)}"}


@mcp.tool()
def git_add_files(local_path: str, files: List[str]) -> Dict[str, Any]:
    """Add specific files to the staging area."""
    try:
        if not os.path.exists(local_path) or not os.path.exists(os.path.join(local_path, '.git')):
            return {"error": f"Not a git repository: {local_path}"}
        
        repo = git.Repo(local_path)
        
        # Validate files exist
        valid_files = []
        for file in files:
            file_path = os.path.join(local_path, file)
            if os.path.exists(file_path):
                valid_files.append(file)
            else:
                return {"error": f"File does not exist: {file}"}
        
        if not valid_files:
            return {"error": "No valid files to add"}
        
        # Add files
        for file in valid_files:
            repo.git.add(file)
        
        return {
            "success": True,
            "local_path": local_path,
            "files_added": valid_files,
            "message": f"Successfully added {len(valid_files)} file(s) to staging area"
        }
    except Exception as e:
        return {"error": f"Failed to add files: {str(e)}"}


@mcp.tool()
def git_commit_changes(local_path: str, commit_message: str) -> Dict[str, Any]:
    """Commit staged changes with a message."""
    try:
        if not os.path.exists(local_path) or not os.path.exists(os.path.join(local_path, '.git')):
            return {"error": f"Not a git repository: {local_path}"}
        
        repo = git.Repo(local_path)
        
        # Check if there are staged changes
        diff_staged = repo.git.diff('--cached', '--name-only')
        if not diff_staged:
            return {"error": "No staged changes to commit. Use git_add_files first."}
        
        # Create commit
        repo.index.commit(commit_message)
        
        # Get commit info
        latest_commit = repo.head.commit
        staged_files = diff_staged.split('\n')
        
        return {
            "success": True,
            "local_path": local_path,
            "commit_sha": latest_commit.hexsha[:7],
            "commit_message": latest_commit.message,
            "author": f"{latest_commit.author.name} <{latest_commit.author.email}>",
            "committed_at": latest_commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "files_committed": [f for f in staged_files if f][:10],
            "message": f"Successfully committed {len(staged_files)} file(s)"
        }
    except Exception as e:
        return {"error": f"Failed to commit changes: {str(e)}"}


@mcp.tool()
def git_push_changes(local_path: str, branch: str = None) -> Dict[str, Any]:
    """Push committed changes to remote repository."""
    try:
        if not os.path.exists(local_path) or not os.path.exists(os.path.join(local_path, '.git')):
            return {"error": f"Not a git repository: {local_path}"}
        
        repo = git.Repo(local_path)
        
        # Get current branch if not specified
        if not branch:
            try:
                branch = repo.active_branch.name
            except:
                return {"error": "Not on a branch. Please specify a branch to push to."}
        
        # Check if there are commits to push
        try:
            repo.git.fetch()
            ahead = repo.git.rev_list(f'origin/{branch}..{branch}', count=True)
            if not ahead or int(ahead) == 0:
                return {"message": f"No new commits to push on branch '{branch}'"}
        except:
            pass
        
        # Push to remote
        origin = repo.remotes.origin
        push_info = origin.push(branch)
        
        return {
            "success": True,
            "local_path": local_path,
            "branch": branch,
            "pushed_to": "origin",
            "message": f"Successfully pushed changes to remote branch '{branch}'"
        }
    except Exception as e:
        return {"error": f"Failed to push changes: {str(e)}"}


@mcp.tool()
def git_pull_changes(local_path: str, branch: str = None) -> Dict[str, Any]:
    """Pull latest changes from remote repository."""
    try:
        if not os.path.exists(local_path) or not os.path.exists(os.path.join(local_path, '.git')):
            return {"error": f"Not a git repository: {local_path}"}
        
        repo = git.Repo(local_path)
        
        # Get current branch if not specified
        if not branch:
            try:
                branch = repo.active_branch.name
            except:
                return {"error": "Not on a branch. Please specify a branch to pull from."}
        
        # Pull from remote
        origin = repo.remotes.origin
        before_commit = repo.head.commit.hexsha[:7] if repo.head.commit else "No commits"
        pull_info = origin.pull(branch)
        after_commit = repo.head.commit.hexsha[:7] if repo.head.commit else "No commits"
        
        changes_pulled = len(pull_info)
        
        return {
            "success": True,
            "local_path": local_path,
            "branch": branch,
            "pulled_from": "origin",
            "before_commit": before_commit,
            "after_commit": after_commit,
            "changes_pulled": changes_pulled,
            "message": f"Successfully pulled {changes_pulled} change(s) from remote"
        }
    except Exception as e:
        return {"error": f"Failed to pull changes: {str(e)}"}


@mcp.tool()
def git_create_branch(local_path: str, new_branch: str, from_branch: str = None) -> Dict[str, Any]:
    """Create a new branch in local repository."""
    try:
        if not os.path.exists(local_path) or not os.path.exists(os.path.join(local_path, '.git')):
            return {"error": f"Not a git repository: {local_path}"}
        
        repo = git.Repo(local_path)
        
        # Get source branch
        if not from_branch:
            try:
                from_branch = repo.active_branch.name
            except:
                return {"error": "Not on a branch. Please specify a source branch."}
        
        # Check if branch already exists
        if new_branch in [b.name for b in repo.branches]:
            return {"error": f"Branch '{new_branch}' already exists"}
        
        # Create new branch
        repo.git.branch(new_branch, from_branch)
        
        return {
            "success": True,
            "local_path": local_path,
            "new_branch": new_branch,
            "from_branch": from_branch,
            "message": f"Created branch '{new_branch}' from '{from_branch}'",
            "next_step": f"To switch to this branch: git switch {new_branch}"
        }
    except Exception as e:
        return {"error": f"Failed to create branch: {str(e)}"}


@mcp.tool()
def git_switch_branch(local_path: str, branch_name: str) -> Dict[str, Any]:
    """Switch to a different branch in local repository."""
    try:
        if not os.path.exists(local_path) or not os.path.exists(os.path.join(local_path, '.git')):
            return {"error": f"Not a git repository: {local_path}"}
        
        repo = git.Repo(local_path)
        
        # Check if branch exists
        if branch_name not in [b.name for b in repo.branches]:
            return {"error": f"Branch '{branch_name}' does not exist"}
        
        # Switch branch
        repo.git.checkout(branch_name)
        
        return {
            "success": True,
            "local_path": local_path,
            "branch": branch_name,
            "message": f"Switched to branch '{branch_name}'"
        }
    except Exception as e:
        return {"error": f"Failed to switch branch: {str(e)}"}


@mcp.tool()
def git_show_history(local_path: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Show commit history of local repository."""
    try:
        if not os.path.exists(local_path) or not os.path.exists(os.path.join(local_path, '.git')):
            return [{"error": f"Not a git repository: {local_path}"}]
        
        repo = git.Repo(local_path)
        commits = []
        
        for commit in repo.iter_commits(max_count=limit):
            commits.append({
                "sha": commit.hexsha[:7],
                "message": commit.message.strip(),
                "author": commit.author.name,
                "date": commit.committed_datetime.strftime("%Y-%m-%d %H:%M"),
                "files_changed": len(commit.stats.files) if commit.stats else 0
            })
        
        return commits
    except Exception as e:
        return [{"error": f"Failed to show history: {str(e)}"}]


# ==================== GITHUB DIRECT OPERATIONS ====================

@mcp.tool()
def github_create_file(
    repo_full_name: str,
    file_path: str,
    content: str,
    commit_message: str,
    branch: str = "main"
) -> Dict[str, Any]:
    """Create a new file in your GitHub repository."""
    try:
        repo = g.get_repo(repo_full_name)
        
        # Verify ownership
        if repo.owner.login != user.login:
            return {
                "error": "This is not your repository. You can only create files in your own repositories.",
                "owner": repo.owner.login,
                "you": user.login
            }
        
        # Check if file already exists
        try:
            existing = repo.get_contents(file_path, ref=branch)
            return {
                "error": f"File '{file_path}' already exists in repository.",
                "suggestion": "Use github_update_file to update existing file."
            }
        except:
            pass
        
        # Create file
        result = repo.create_file(
            path=file_path,
            message=commit_message,
            content=content,
            branch=branch
        )
        
        return {
            "success": True,
            "action": "created",
            "file": file_path,
            "commit_sha": result["commit"].sha[:7],
            "commit_url": result["commit"].html_url,
            "branch": branch,
            "repository": repo.full_name,
            "message": f"Created file '{file_path}' in repository"
        }
    except Exception as e:
        return {"error": f"Failed to create file: {str(e)}"}


@mcp.tool()
def github_update_file(
    repo_full_name: str,
    file_path: str,
    content: str,
    commit_message: str,
    branch: str = "main"
) -> Dict[str, Any]:
    """Update an existing file in your GitHub repository."""
    try:
        repo = g.get_repo(repo_full_name)
        
        # Verify ownership
        if repo.owner.login != user.login:
            return {
                "error": "This is not your repository. You can only update files in your own repositories.",
                "owner": repo.owner.login,
                "you": user.login
            }
        
        # Get existing file
        existing_file = repo.get_contents(file_path, ref=branch)
        
        # Update file
        result = repo.update_file(
            path=file_path,
            message=commit_message,
            content=content,
            sha=existing_file.sha,
            branch=branch
        )
        
        return {
            "success": True,
            "action": "updated",
            "file": file_path,
            "commit_sha": result["commit"].sha[:7],
            "commit_url": result["commit"].html_url,
            "branch": branch,
            "repository": repo.full_name,
            "message": f"Updated file '{file_path}' in repository"
        }
    except GithubException as e:
        if "Not Found" in str(e):
            return {"error": f"File '{file_path}' not found in repository."}
        return {"error": f"Failed to update file: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to update file: {str(e)}"}


@mcp.tool()
def github_create_repository(
    name: str,
    description: str = "",
    private: bool = False
) -> Dict[str, Any]:
    """Create a new repository in your GitHub account."""
    try:
        # Check if repository already exists
        try:
            existing = g.get_repo(f"{user.login}/{name}")
            return {"error": f"Repository '{name}' already exists in your account."}
        except:
            pass
        
        # Create repository
        repo = user.create_repo(
            name=name,
            description=description,
            private=private,
            auto_init=True  # Initialize with README
        )
        
        return {
            "success": True,
            "name": repo.name,
            "full_name": repo.full_name,
            "private": repo.private,
            "url": repo.html_url,
            "clone_url": repo.clone_url,
            "message": f"Created repository '{name}' in your GitHub account"
        }
    except GithubException as e:
        return {"error": f"Failed to create repository: {e.data.get('message', str(e))}"}
    except Exception as e:
        return {"error": f"Failed to create repository: {str(e)}"}


# ==================== UTILITY TOOLS ====================

@mcp.tool()
def find_local_repositories(search_path: str = ".") -> List[Dict[str, Any]]:
    """Find all local git repositories in a directory."""
    try:
        if not os.path.exists(search_path):
            return [{"error": f"Path does not exist: {search_path}"}]
        
        repos = []
        
        for root, dirs, files in os.walk(search_path):
            if '.git' in dirs:
                git_dir = os.path.join(root, '.git')
                if os.path.exists(os.path.join(git_dir, 'HEAD')):
                    try:
                        repo = git.Repo(root)
                        current_branch = None
                        try:
                            current_branch = repo.active_branch.name
                        except:
                            current_branch = "DETACHED_HEAD"
                        
                        repos.append({
                            "path": root,
                            "name": os.path.basename(root),
                            "branch": current_branch,
                            "has_changes": repo.is_dirty(),
                            "commit_count": len(list(repo.iter_commits())) if repo.head.commit else 0
                        })
                    except:
                        repos.append({
                            "path": root,
                            "name": os.path.basename(root),
                            "branch": "UNKNOWN",
                            "has_changes": False,
                            "commit_count": 0
                        })
        
        return repos
    except Exception as e:
        return [{"error": f"Failed to find repositories: {str(e)}"}]


# ==================== MAIN ====================

if __name__ == "__main__":
    print(f"Connected as: {user.login}")
    mcp.run()