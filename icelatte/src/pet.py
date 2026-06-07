import subprocess


def call(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )

        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print(
            f"An error occurred while running the application! Error Code: {e.returncode}"
        )
        print(f"Error Details: {e.stderr}")


if __name__ == "__main__":
    call(command=["./bin/pet", "--status"])
