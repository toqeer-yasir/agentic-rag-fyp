import os
import subprocess
import signal
import shlex
from typing import Optional
from fastmcp import FastMCP

mcp = FastMCP("Shell")

@mcp.tool()
def shell(command: str, timeout: int = 60) -> str:
    """
    Execute any shell command.
    
    You can use this for ANY terminal operation:
    - File operations: ls, cp, mv, rm, find, grep
    - Git: clone, pull, push, commit
    - Package management: apt, pip, npm
    - System: ps, systemctl, df, free
    - Python: python script.py,
    
    Args:
        command: Any shell command to execute
        timeout: Maximum execution time in seconds
    """
    dangerous = [
        "rm -rf /", "rm -rf /*", "dd if=", "mkfs", 
        ":(){ :|:& };:", "chmod 777 /", "> /dev/sd"
    ]
    
    for d in dangerous:
        if d in command.lower():
            return f"Security Error: Command blocked - contains dangerous pattern: {d}"
    
    try:
        proc = subprocess.Popen(
            command,
            shell=True,
            executable="/bin/bash",
            cwd=os.getcwd(),
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True
        )
        
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except:
                pass
            stdout, stderr = proc.communicate()
            return f"Timeout Error: Command took too long (> {timeout}s)\n\nOutput:\n{stdout}\n\nError:\n{stderr}"
        
        response = []
        response.append(f"Command: {command}")
        response.append(f"Exit Code: {proc.returncode}")
        response.append(f"Success: {'Yes' if proc.returncode == 0 else 'No'}")
        
        if stdout:
            response.append(f"\nOutput:\n{stdout.rstrip()}")
        
        if stderr:
            response.append(f"\nError Output:\n{stderr.rstrip()}")
        
        return "\n".join(response)
        
    except Exception as e:
        return f"Execution Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()