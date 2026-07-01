import asyncio


async def call(command):
    try:
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            print(f"An error occurred while running the application! Error Code: {proc.returncode}")
            print(f"Error Details: {stderr.decode('utf-8')}")
            return f"Error {proc.returncode}: {stderr.decode('utf-8')}"

        return stdout.decode("utf-8")

    except Exception as e:
        print(f"Exception: {e}")
        return str(e)


def create_pet_command(name=None, status=False, eat=None, user_id=123):
    command = ["./bin/pet", "--savefile", f"./database/{user_id}.json"]
    if name:
        command.extend(["--name", str(name)])
    if eat and 1 <= eat <= 4:
        command.extend(["--eat", str(eat)])
    if status:
        command.append("--status")
    return command


if __name__ == "__main__":
    import asyncio
    asyncio.run(call(command=["./bin/pet", "--status"]))
