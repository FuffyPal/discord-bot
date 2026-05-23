import subprocess
import sys

def ping(ip: str = None, count: int = None):
    if sys.platform == "win32":
        command = ["ping", "-n", str(count), ip]
    else:
        command = ["ping", "-c", str(count), ip]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode("utf-8")