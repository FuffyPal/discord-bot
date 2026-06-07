import subprocess


def call(command):
    try:
        command_result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        result = command_result.stdout
        return result

    except subprocess.CalledProcessError as e:
        print(
            f"An error occurred while running the application! Error Code: {e.returncode}"
        )
        print(f"Error Details: {e.stderr}")
        err_1 = {e.returncode}
        err_2 = {e.stderr}
        return err_1, err_2


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
    call(command=["./bin/pet", "--status"])
