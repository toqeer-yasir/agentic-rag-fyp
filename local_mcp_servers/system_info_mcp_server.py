import psutil
import platform
import socket
import datetime
import subprocess
from typing import List, Optional
from fastmcp import FastMCP

mcp = FastMCP("System info.")

@mcp.tool()
def system_overview() -> str:
    """Get comprehensive system overview"""
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        
        # Memory
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk
        disk = psutil.disk_usage('/')
        
        # System info
        system = platform.system()
        release = platform.release()
        version = platform.version()
        machine = platform.machine()
        
        # Uptime
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        
        # Network
        net_io = psutil.net_io_counters()
        
        return f"""
System Overview:

Operating System:
  System: {system} {release}
  Version: {version}
  Architecture: {machine}

CPU:
  Usage: {cpu_percent}%
  Cores: {cpu_count} logical
  Frequency: {cpu_freq.current:.0f} MHz (max: {cpu_freq.max:.0f} MHz)

Memory:
  Used: {mem.percent}% ({mem.used//1024//1024} MB / {mem.total//1024//1024} MB)
  Available: {mem.available//1024//1024} MB
  Swap: {swap.percent}% used

Disk (/):
  Used: {disk.percent}% ({disk.used//1024//1024//1024} GB / {disk.total//1024//1024//1024} GB)
  Free: {disk.free//1024//1024//1024} GB

Network:
  Sent: {net_io.bytes_sent//1024//1024} MB
  Received: {net_io.bytes_recv//1024//1024} MB

System Uptime: {uptime.days} days, {uptime.seconds//3600} hours
Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}
""".strip()
        
    except Exception as e:
        return f"Error getting system overview: {str(e)}"

@mcp.tool()
def cpu_info() -> str:
    """Get CPU information and usage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        cpu_count_logical = psutil.cpu_count(logical=True)
        cpu_count_physical = psutil.cpu_count(logical=False)
        cpu_freq = psutil.cpu_freq()
        
        result = f"CPU Information:\n"
        result += f"  Physical cores: {cpu_count_physical}\n"
        result += f"  Logical cores: {cpu_count_logical}\n"
        result += f"  Current frequency: {cpu_freq.current:.0f} MHz\n"
        result += f"  Max frequency: {cpu_freq.max:.0f} MHz\n\n"
        result += f"CPU Usage per core:\n"
        
        for i, percent in enumerate(cpu_percent):
            result += f"  Core {i+1}: {percent}%\n"
        
        result += f"\nTotal CPU usage: {sum(cpu_percent)/len(cpu_percent):.1f}%"
        
        return result
        
    except Exception as e:
        return f"Error getting CPU info: {str(e)}"

@mcp.tool()
def memory_info() -> str:
    """Get detailed memory usage information"""
    try:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return f"""
Memory Information:

Physical Memory:
  Total: {mem.total//1024//1024} MB
  Available: {mem.available//1024//1024} MB
  Used: {mem.used//1024//1024} MB ({mem.percent}%)
  Free: {mem.free//1024//1024} MB

Swap Memory:
  Total: {swap.total//1024//1024} MB
  Used: {swap.used//1024//1024} MB ({swap.percent}%)
  Free: {swap.free//1024//1024} MB

Memory Details:
  Active: {mem.active//1024//1024} MB
  Inactive: {mem.inactive//1024//1024} MB
  Buffers: {mem.buffers//1024//1024} MB
  Cached: {mem.cached//1024//1024} MB
  Shared: {mem.shared//1024//1024} MB
""".strip()
        
    except Exception as e:
        return f"Error getting memory info: {str(e)}"

@mcp.tool()
def disk_info(path: str = "/") -> str:
    """Get disk usage for a specific path"""
    try:
        disk = psutil.disk_usage(path)
        disk_io = psutil.disk_io_counters()
        
        return f"""
Disk Information ({path}):

Usage:
  Total: {disk.total//1024//1024//1024} GB
  Used: {disk.used//1024//1024//1024} GB ({disk.percent}%)
  Free: {disk.free//1024//1024//1024} GB

I/O Statistics:
  Read count: {disk_io.read_count:,}
  Write count: {disk_io.write_count:,}
  Bytes read: {disk_io.read_bytes//1024//1024} MB
  Bytes written: {disk_io.write_bytes//1024//1024} MB
""".strip()
        
    except Exception as e:
        return f"Error getting disk info: {str(e)}"

@mcp.tool()
def process_list(count: int = 10, sort_by: str = "cpu") -> str:
    """List running processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                proc_info = proc.info
                proc_info['cpu_percent'] = proc_info['cpu_percent'] or 0
                proc_info['memory_percent'] = proc_info['memory_percent'] or 0
                processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if sort_by == "cpu":
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            sort_name = "CPU usage"
        else:  # memory
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            sort_name = "memory usage"
        
        result = f"Top {count} processes by {sort_name}:\n"
        result += "PID      Name                          CPU%   Memory%  Status\n"
        result += "-" * 60 + "\n"
        
        for proc in processes[:count]:
            pid = str(proc['pid']).ljust(8)
            name = (proc['name'][:25] + '...' if len(proc['name']) > 25 else proc['name']).ljust(28)
            cpu = f"{proc['cpu_percent']:5.1f}".ljust(6)
            mem = f"{proc['memory_percent']:6.2f}".ljust(8)
            status = proc['status']
            result += f"{pid}{name}{cpu}{mem}{status}\n"
        
        return result
        
    except Exception as e:
        return f"Error listing processes: {str(e)}"

@mcp.tool()
def network_info() -> str:
    """Get network interface information"""
    try:
        interfaces = psutil.net_if_addrs()
        io_counters = psutil.net_io_counters(pernic=True)
        
        result = "Network Information:\n\n"
        
        for iface, addrs in interfaces.items():
            result += f"Interface: {iface}\n"
            
            if iface in io_counters:
                io = io_counters[iface]
                result += f"  Sent: {io.bytes_sent//1024} KB, Received: {io.bytes_recv//1024} KB\n"
            
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    result += f"  IPv4: {addr.address}\n"
                elif addr.family == socket.AF_INET6:
                    result += f"  IPv6: {addr.address}\n"
                elif addr.family == psutil.AF_LINK:
                    result += f"  MAC: {addr.address}\n"
            
            result += "\n"
        
        # Add public IP info if possible
        try:
            import requests
            public_ip = requests.get('https://api.ipify.org', timeout=5).text
            result += f"Public IP: {public_ip}\n"
        except:
            result += "Public IP: Could not determine\n"
        
        return result.strip()
        
    except Exception as e:
        return f"Error getting network info: {str(e)}"

@mcp.tool()
def service_status(service_name: str) -> str:
    """Check status of a systemd service"""
    try:
        result = subprocess.run(
            ['systemctl', 'status', service_name, '--no-pager'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return f"Service '{service_name}' status:\n{result.stdout}"
        else:
            return f"Service '{service_name}' status:\n{result.stderr or result.stdout}"
        
    except FileNotFoundError:
        return "Error: systemctl command not found (not running systemd?)"
    except subprocess.TimeoutExpired:
        return f"Error: Timeout checking service '{service_name}'"
    except Exception as e:
        return f"Error checking service status: {str(e)}"

@mcp.tool()
def system_uptime() -> str:
    """Get system uptime information"""
    try:
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        
        uptime_str = ""
        if uptime.days > 0:
            uptime_str += f"{uptime.days} day{'s' if uptime.days != 1 else ''}, "
        
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        seconds = uptime.seconds % 60
        
        uptime_str += f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        return f"""
System Uptime:
  Boot time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}
  Uptime: {uptime_str}
  Days: {uptime.days}
""".strip()
        
    except Exception as e:
        return f"Error getting uptime: {str(e)}"

@mcp.tool()
def hardware_info() -> str:
    """Get hardware information"""
    try:
        result = "Hardware Information:\n\n"
        
        # CPU info
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpu_info = f.read()
                model_lines = [line for line in cpu_info.split('\n') if 'model name' in line]
                if model_lines:
                    cpu_model = model_lines[0].split(':')[1].strip()
                    result += f"CPU Model: {cpu_model}\n"
        except:
            pass
        
        # Memory info
        try:
            with open('/proc/meminfo', 'r') as f:
                mem_info = f.read()
                total_lines = [line for line in mem_info.split('\n') if 'MemTotal' in line]
                if total_lines:
                    mem_total = total_lines[0].split(':')[1].strip()
                    result += f"Total Memory: {mem_total}\n"
        except:
            pass
        
        # Disk info
        try:
            result += "\nDisk Information:\n"
            partitions = psutil.disk_partitions()
            for partition in partitions:
                if partition.fstype:
                    usage = psutil.disk_usage(partition.mountpoint)
                    result += f"  {partition.device} -> {partition.mountpoint} ({partition.fstype})\n"
                    result += f"    Total: {usage.total//1024//1024//1024} GB, "
                    result += f"Used: {usage.percent}%, Free: {usage.free//1024//1024//1024} GB\n"
        except:
            pass
        
        return result.strip()
        
    except Exception as e:
        return f"Error getting hardware info: {str(e)}"


if __name__ == "__main__":
    mcp.run()