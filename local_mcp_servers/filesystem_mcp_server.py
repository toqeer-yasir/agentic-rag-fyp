import os
import shutil
import stat
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from fastmcp import FastMCP

mcp = FastMCP("File system")

@mcp.tool()
def file_read(filepath: str, lines: Optional[int] = None) -> str:
    """Read contents of a file"""
    try:
        path = Path(filepath)
        if not path.exists():
            return f"Error: File not found: {filepath}"
        if path.is_dir():
            return f"Error: Path is a directory: {filepath}"
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            if lines:
                content_lines = []
                for i, line in enumerate(f):
                    if i >= lines:
                        break
                    content_lines.append(line)
                return ''.join(content_lines)
            else:
                return f.read()[:10000]  # Limit to 10k chars
        
    except PermissionError:
        return f"Error: Permission denied reading file: {filepath}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def file_write(filepath: str, content: str, append: bool = False) -> str:
    """Write content to a file"""
    try:
        path = Path(filepath)
        mode = 'a' if append else 'w'
        
        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, mode, encoding='utf-8') as f:
            f.write(content)
        
        action = "appended to" if append else "written to"
        return f"Successfully {action} {filepath}"
        
    except PermissionError:
        return f"Error: Permission denied writing to: {filepath}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@mcp.tool()
def list_dir(path: str = ".", show_hidden: bool = False) -> str:
    """List contents of a directory"""
    try:
        dir_path = Path(path)
        if not dir_path.exists():
            return f"Error: Directory not found: {path}"
        if not dir_path.is_dir():
            return f"Error: Not a directory: {path}"
        
        items = []
        for item in sorted(dir_path.iterdir()):
            if not show_hidden and item.name.startswith('.'):
                continue
            
            if item.is_dir():
                items.append(f"[DIR]  {item.name}/")
            else:
                size = item.stat().st_size
                size_str = f"{size:,} bytes"
                if size > 1024*1024:
                    size_str = f"{size/(1024*1024):.1f} MB"
                elif size > 1024:
                    size_str = f"{size/1024:.1f} KB"
                items.append(f"[FILE] {item.name} ({size_str})")
        
        if not items:
            return f"Directory '{path}' is empty"
        
        return f"Contents of '{path}':\n" + "\n".join(items)
        
    except PermissionError:
        return f"Error: Permission denied accessing: {path}"
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@mcp.tool()
def file_info(filepath: str) -> str:
    """Get information about a file or directory"""
    try:
        path = Path(filepath)
        if not path.exists():
            return f"Error: Path does not exist: {filepath}"
        
        stat_info = path.stat()
        modified = datetime.fromtimestamp(stat_info.st_mtime)
        
        if path.is_dir():
            item_type = "Directory"
            size = "N/A"
        else:
            item_type = "File"
            size = stat_info.st_size
            size_str = f"{size:,} bytes"
            if size > 1024*1024:
                size_str = f"{size/(1024*1024):.1f} MB"
            elif size > 1024:
                size_str = f"{size/1024:.1f} KB"
        
        return f"""
File Information:
Path: {filepath}
Type: {item_type}
Size: {size_str if path.is_file() else 'N/A'}
Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}
Permissions: {oct(stat_info.st_mode)[-3:]}
Owner UID: {stat_info.st_uid}
Group GID: {stat_info.st_gid}
""".strip()
        
    except Exception as e:
        return f"Error getting file info: {str(e)}"

@mcp.tool()
def file_search(pattern: str, directory: str = ".", recursive: bool = True) -> str:
    """Search for files matching a pattern"""
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return f"Error: Directory not found: {directory}"
        
        matches = []
        if recursive:
            search_path = dir_path.rglob(pattern)
        else:
            search_path = dir_path.glob(pattern)
        
        for match in search_path:
            if match.is_file():
                matches.append(str(match.relative_to(dir_path)))
        
        if not matches:
            return f"No files found matching '{pattern}' in '{directory}'"
        
        if len(matches) > 50:
            matches = matches[:50]
            matches.append("... (showing first 50 matches)")
        
        return f"Found {len(matches)} files matching '{pattern}':\n" + "\n".join(matches)
        
    except Exception as e:
        return f"Error searching files: {str(e)}"

@mcp.tool()
def create_dir(path: str) -> str:
    """Create a new directory"""
    try:
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return f"Created directory: {path}"
        
    except PermissionError:
        return f"Error: Permission denied creating directory: {path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"

@mcp.tool()
def file_delete(path: str) -> str:
    """Delete a file or directory"""
    try:
        target = Path(path)
        if not target.exists():
            return f"Error: Path does not exist: {path}"
        
        if target.is_file():
            target.unlink()
            return f"Deleted file: {path}"
        else:
            return f"Target is not a file"
        
    except PermissionError:
        return f"Error: Permission denied deleting: {path}"
    except Exception as e:
        return f"Error deleting path: {str(e)}"

@mcp.tool()
def dir_delete(path: str) -> str:
    """Delete a file or directory"""
    try:
        target = Path(path)
        if not target.exists():
            return f"Error: Path does not exist: {path}"
        
        if target.is_dir():
            shutil.rmtree(target)
            return f"Deleted directory: {path}"
        else:
            return f"Target is not a directory"
        
    except PermissionError:
        return f"Error: Permission denied deleting: {path}"
    except Exception as e:
        return f"Error deleting path: {str(e)}"

@mcp.tool()
def file_copy(source: str, destination: str) -> str:
    """Copy a file or directory"""
    try:
        src = Path(source)
        dst = Path(destination)
        
        if not src.exists():
            return f"Error: Source not found: {source}"
        
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            return f"Copied directory: {source} -> {destination}"
        else:
            shutil.copy2(src, dst)
            return f"Copied file: {source} -> {destination}"
        
    except PermissionError:
        return f"Error: Permission denied copying: {source}"
    except Exception as e:
        return f"Error copying: {str(e)}"

@mcp.tool()
def file_move(source: str, destination: str) -> str:
    """Move or rename a file or directory"""
    try:
        src = Path(source)
        dst = Path(destination)
        
        if not src.exists():
            return f"Error: Source not found: {source}"
        
        shutil.move(str(src), str(dst))
        return f"Moved: {source} -> {destination}"
        
    except PermissionError:
        return f"Error: Permission denied moving: {source}"
    except Exception as e:
        return f"Error moving: {str(e)}"

@mcp.tool()
def current_path() -> str:
    """Get current working directory"""
    try:
        return f"Current directory: {Path.cwd()}"
    except Exception as e:
        return f"Error getting current directory: {str(e)}"

@mcp.tool()
def dir_stats(path: str = ".") -> str:
    """Get statistics about files in a directory"""
    try:
        dir_path = Path(path)
        if not dir_path.exists():
            return f"Error: Directory not found: {path}"
        
        file_count = 0
        dir_count = 0
        total_size = 0
        
        for item in dir_path.rglob('*'):
            if item.is_file():
                file_count += 1
                total_size += item.stat().st_size
            elif item.is_dir():
                dir_count += 1
        
        size_str = f"{total_size:,} bytes"
        if total_size > 1024*1024*1024:
            size_str = f"{total_size/(1024*1024*1024):.1f} GB"
        elif total_size > 1024*1024:
            size_str = f"{total_size/(1024*1024):.1f} MB"
        elif total_size > 1024:
            size_str = f"{total_size/1024:.1f} KB"
        
        return f"""
Directory Statistics:
Location: {path}
Files: {file_count}
Directories: {dir_count}
Total Size: {size_str}
""".strip()
        
    except Exception as e:
        return f"Error getting directory stats: {str(e)}"

@mcp.tool()
def find_large_file(directory: str = ".", min_size_mb: int = 10) -> str:
    """Find files larger than specified size"""
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return f"Error: Directory not found: {directory}"
        
        min_bytes = min_size_mb * 1024 * 1024
        large_files = []
        
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                size = file_path.stat().st_size
                if size > min_bytes:
                    size_mb = size / (1024 * 1024)
                    large_files.append((file_path, size_mb))
        
        if not large_files:
            return f"No files larger than {min_size_mb} MB found in '{directory}'"
        
        large_files.sort(key=lambda x: x[1], reverse=True)
        result = [f"Files larger than {min_size_mb} MB:"]
        
        for file_path, size_mb in large_files[:10]:
            rel_path = file_path.relative_to(dir_path)
            result.append(f"  {rel_path} ({size_mb:.1f} MB)")
        
        if len(large_files) > 10:
            result.append(f"... and {len(large_files) - 10} more files")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"Error finding large files: {str(e)}"

@mcp.tool()
def file_tail(filepath: str, lines: int = 10) -> str:
    """Show last lines of a file"""
    try:
        path = Path(filepath)
        if not path.exists():
            return f"Error: File not found: {filepath}"
        if path.is_dir():
            return f"Error: Path is a directory: {filepath}"
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
        
        if lines > len(all_lines):
            lines = len(all_lines)
        
        return ''.join(all_lines[-lines:])
        
    except Exception as e:
        return f"Error reading file tail: {str(e)}"

if __name__ == "__main__":
    mcp.run()