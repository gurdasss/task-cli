import subprocess
import os


def clear_screen():
    subprocess.call("cls" if os.name == "nt" else "clear", shell=True)


if __name__ == "__main__":
    while True:
        current_input = input("task-cli> ")
        # TODO: Need to handle EOF chars

        if current_input == "cls":
            clear_screen()
        elif current_input == "exit":
            break
