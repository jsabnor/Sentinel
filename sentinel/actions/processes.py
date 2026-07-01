import logging

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

log = logging.getLogger("sentinel.actions.processes")


class ProcessController:
    def __init__(self):
        if not HAS_PSUTIL:
            log.warning("psutil not installed. Process management limited.")

    def list_processes(self) -> str:
        if not HAS_PSUTIL:
            return "psutil not installed."

        try:
            processes = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    info = proc.info
                    processes.append((
                        info["cpu_percent"] or 0,
                        info["memory_percent"] or 0,
                        info["pid"],
                        info["name"] or "unknown",
                    ))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            processes.sort(key=lambda x: x[0], reverse=True)

            lines = ["PID     CPU%   MEM%   Name"]
            lines.append("-" * 60)
            for cpu, mem, pid, name in processes[:30]:
                lines.append(f"{pid:<7} {cpu:>5.1f}  {mem:>5.2f}  {name}")

            return f"Top 30 processes by CPU:\n" + "\n".join(lines)
        except Exception as e:
            return f"Error listing processes: {e}"

    def kill(self, pid: int = None, name: str = None) -> str:
        if not HAS_PSUTIL:
            return "psutil not installed."

        try:
            if pid:
                proc = psutil.Process(pid)
                proc_name = proc.name()
                proc.terminate()
                proc.wait(timeout=5)
                return f"Terminated process: {proc_name} (PID {pid})."

            if name:
                killed = 0
                for proc in psutil.process_iter(["pid", "name"]):
                    try:
                        if proc.info["name"] and name.lower() in proc.info["name"].lower():
                            proc.terminate()
                            proc.wait(timeout=5)
                            killed += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                return f"Terminated {killed} process(es) matching '{name}'."

            return "Must specify pid or name."
        except psutil.NoSuchProcess:
            return f"Process not found."
        except psutil.AccessDenied:
            return f"Access denied - cannot terminate process."
        except Exception as e:
            return f"Error killing process: {e}"

    def system_info(self) -> str:
        if not HAS_PSUTIL:
            return "psutil not installed."

        try:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            lines = [
                f"CPU Usage: {cpu}%",
                f"Memory: {mem.percent}% used ({mem.used / (1024**3):.1f} / {mem.total / (1024**3):.1f} GB)",
                f"Disk: {disk.percent}% used ({disk.used / (1024**3):.1f} / {disk.total / (1024**3):.1f} GB)",
                f"CPU Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical",
                f"Boot time: {psutil.boot_time()}",
            ]
            return "\n".join(lines)
        except Exception as e:
            return f"Error getting system info: {e}"
