# =========================
# main.py
# =========================

import random
import sys
import json
import os
import subprocess
import readline  # For command history and tab completion

# ---------- FILE PATH ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")

# ---------- TERMINAL ----------
def terminal(user):

    hostname = "ArunCode.com"

    # Current directory reference (starts at root)
    cwd = user["fs"]
    path_stack = ["~"]

    # Store file contents
    if "file_contents" not in user:
        user["file_contents"] = {}

    # ---------- Readline Setup ----------
    def completer(text, state):
        # Autocomplete folders and files in cwd
        options = [i for i in list(cwd["folders"].keys()) + cwd["files"] if i.startswith(text)]
        if state < len(options):
            return options[state]
        else:
            return None

    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

    def prompt():
        path = "/".join(path_stack)
        symbol = "#" if user["sudo"] == "True" else "$"
        return f"{user['username']}@{hostname}/{user['usertype']}:{path} {symbol} "

    # Recursive tree printer
    def print_tree(directory, prefix=""):
        for folder in directory["folders"]:
            print(prefix + folder + "/")
            print_tree(directory["folders"][folder], prefix + "  ")
        for file in directory["files"]:
            print(prefix + file)

    try:
        while True:
            command = input(prompt()).strip()

            # ---------- whoami ----------
            if command == "whoami":
                print(user["username"])

            # ---------- exit ----------
            elif command == "exit":
                break

            # ---------- clear ----------
            elif command == "clear":
                os.system('clear')

            # ---------- ls ----------
            elif command == "ls":
                items = list(cwd["folders"].keys()) + cwd["files"]
                print("  ".join(items) if items else "(directory empty)")

            # ---------- pwd ----------
            elif command == "pwd":
                print("/".join(path_stack))

            # ---------- tree ----------
            elif command == "tree":
                print_tree(cwd)

            # ---------- cd ----------
            elif command.startswith("cd"):
                parts = command.split()
                if len(parts) == 1 or parts[1] == "~":
                    cwd = user["fs"]
                    path_stack[:] = ["~"]
                elif parts[1] == "..":
                    if len(path_stack) > 1:
                        path_stack.pop()
                        cwd = user["fs"]
                        for p in path_stack[1:]:
                            cwd = cwd["folders"][p]
                elif parts[1] in cwd["folders"]:
                    cwd = cwd["folders"][parts[1]]
                    path_stack.append(parts[1])
                else:
                    print("cd: no such directory")

            # ---------- touch ----------
            elif command.startswith("touch "):
                name = command.split(" ", 1)[1]
                if not name.endswith(".txt"):
                    name += ".txt"
                if name not in cwd["files"]:
                    cwd["files"].append(name)
                    user["file_contents"][name] = ""

            # ---------- rm ----------
            elif command.startswith("rm "):
                parts = command.split()
                if len(parts) == 2:
                    name = parts[1]
                    if not name.endswith(".txt"):
                        name += ".txt"
                    if name in cwd["files"]:
                        cwd["files"].remove(name)
                        if name in user["file_contents"]:
                            del user["file_contents"][name]
                    elif name in cwd["folders"]:
                        print(f"rm: cannot remove '{name}': is a directory")
                    else:
                        print(f"rm: cannot remove '{name}': No such file")
                elif len(parts) == 3 and parts[1] == "-r":
                    folder = parts[2]
                    if folder in cwd["folders"]:
                        del cwd["folders"][folder]
                    else:
                        print(f"rm: cannot remove '{folder}': No such directory")
                else:
                    print("rm: missing operand or invalid syntax")

            # ---------- makir ----------
            elif command.startswith("makir "):
                name = command.split(" ", 1)[1]
                if name not in cwd["folders"]:
                    cwd["folders"][name] = {"files": [], "folders": {}}

            # ---------- nano ----------
            elif command.startswith("nano "):
                name = command.split(" ", 1)[1]
                if not name.endswith(".txt"):
                    name += ".txt"

                if name not in cwd["files"]:
                    cwd["files"].append(name)
                    user["file_contents"][name] = ""

                temp_file = f"/tmp/{user['username']}_{name}"
                with open(temp_file, "w") as f:
                    f.write(user["file_contents"].get(name, ""))

                subprocess.run(["nano", temp_file])

                # Save back content
                with open(temp_file, "r") as f:
                    user["file_contents"][name] = f.read()

            # ---------- cat ----------
            elif command.startswith("cat "):
                name = command.split(" ", 1)[1]
                if not name.endswith(".txt"):
                    name += ".txt"
                if name in cwd["files"]:
                    print(user["file_contents"].get(name, ""))
                else:
                    print(f"cat: {name}: No such file")

            # ---------- cp ----------
            elif command.startswith("cp "):
                parts = command.split()
                if len(parts) == 3:
                    src, dest = parts[1], parts[2]
                    if not src.endswith(".txt"):
                        src += ".txt"
                    if not dest.endswith(".txt"):
                        dest += ".txt"
                    if src in cwd["files"]:
                        if dest not in cwd["files"]:
                            cwd["files"].append(dest)
                        user["file_contents"][dest] = user["file_contents"].get(src, "")
                    else:
                        print(f"cp: cannot stat '{src}': No such file")
                else:
                    print("cp: missing operand or invalid syntax")

            # ---------- mv ----------
            elif command.startswith("mv "):
                parts = command.split()
                if len(parts) == 3:
                    src, dest = parts[1], parts[2]
                    if not src.endswith(".txt"):
                        src += ".txt"
                    if not dest.endswith(".txt"):
                        dest += ".txt"
                    if src in cwd["files"]:
                        if dest not in cwd["files"]:
                            cwd["files"].append(dest)
                        user["file_contents"][dest] = user["file_contents"].get(src, "")
                        cwd["files"].remove(src)
                        if src in user["file_contents"]:
                            del user["file_contents"][src]
                    elif src in cwd["folders"]:
                        cwd["folders"][dest] = cwd["folders"].pop(src)
                    else:
                        print(f"mv: cannot stat '{src}': No such file or directory")
                else:
                    print("mv: missing operand or invalid syntax")

            # ---------- ping ----------
            elif command.startswith("ping "):
                target = command.split(" ", 1)[1]
                try:
                    subprocess.run(["ping", "-c", "4", target])
                except FileNotFoundError:
                    print("ping: command not found")

            # ---------- sudo ----------
            elif command == "sudo":
                print("usage: sudo [command]")

            # ---------- unknown ----------
            else:
                print(f"{command}: command not found")

    except KeyboardInterrupt:
        print("\nReturning to main menu...")


# ---------- MAIN ----------
def main():

    while True:
        try:
            print("\n1) Login")
            print("2) Create Account")
            print("3) Guest")
            print("4) Exit")

            choice = input(">>> ")

            # ---------- LOGIN ----------
            if choice == "1":
                u = input("user: ")
                p = input("pass: ")

                with open(DATA_FILE, "r") as f:
                    accounts = json.load(f)

                user = next(
                    (a for a in accounts if a["username"] == u and a["password"] == p),
                    None
                )

                if user:
                    terminal(user)
                    with open(DATA_FILE, "w") as f:
                        json.dump(accounts, f, indent=4)
                else:
                    print("ERROR: Invalid credentials")

            # ---------- CREATE ----------
            elif choice == "2":
                u = input("Choose Username: ")
                p = input("Choose Password: ")
                t = input("User Type: ")

                with open(DATA_FILE, "r") as f:
                    accounts = json.load(f)

                if any(a["username"] == u for a in accounts):
                    print("ERROR: Username exists")
                else:
                    accounts.append({
                        "username": u,
                        "password": p,
                        "sudo": "False",
                        "usertype": t,
                        "fs": {"files": [], "folders": {}}
                    })
                    with open(DATA_FILE, "w") as f:
                        json.dump(accounts, f, indent=4)
                    print("Account created")

            # ---------- GUEST ----------
            elif choice == "3":
                guest = {
                    "username": "guest" + str(random.randint(1000, 9999)),
                    "sudo": "False",
                    "usertype": "Guest",
                    "fs": {"files": [], "folders": {}}
                }
                terminal(guest)

            # ---------- EXIT ----------
            elif choice == "4":
                sys.exit()

        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()


# ---------- ENTRY ----------
if __name__ == "__main__":
    main()
