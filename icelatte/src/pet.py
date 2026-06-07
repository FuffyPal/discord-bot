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


def create_pet_command(name=None, status=False, eat=None):
    command = ["./bin/pet"]
    if name:
        command.extend(["--name", str(name)])
    if status:
        command.append("--status")
    if eat and 1 <= eat <= 4:
        command.extend(["--eat", str(eat)])
    return command


if __name__ == "__main__":
    call(command=["./bin/pet", "--status"])
