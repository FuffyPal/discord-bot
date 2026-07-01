import asyncio
import sys


async def ping(ip: str = None, count: int = None):
    if sys.platform == "win32":
        command = ["ping", "-n", str(count), ip]
    else:
        command = ["ping", "-c", str(count), ip]

    proc = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return stdout.decode("utf-8") or stderr.decode("utf-8")