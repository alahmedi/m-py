#!/usr/bin/env python3

import os
import sys
import shlex
import time
import hashlib
import readline
import signal
import platform
import getpass
hostname = platform.node()
user = getpass.getuser()

DEF_FILE = "/tmp/m_file"
UNDO_STACK = []
REDO_STACK = []


# ---------------- Core helpers ----------------

def load():
    if not os.path.exists(DEF_FILE):
        print("m: no file defined (use `def <path>`)")
        return None
    with open(DEF_FILE) as f:
        return f.read().strip()


def save_def(path):
    with open(DEF_FILE, "w") as f:
        f.write(path)


def hash_file(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------- Commands ----------------

def snapshot(path):
    if path and os.path.exists(path):
        with open(path) as f:
            UNDO_STACK.append(f.read())
    else:
        UNDO_STACK.append("")
    REDO_STACK.clear()


def restore(content, path):
    with open(path, "w") as f:
        f.write(content)


def cmd_def(args):
    if not args:
        print("usage: def <path>")
        return
    save_def(args[0])


def cmd_deldef(args):
    if os.path.exists(DEF_FILE):
        os.remove(DEF_FILE)


def cmd_checkdef(args):
    path = load()
    if path:
        print(path)

def cmd_add(args):
    path = load()
    if not path:
        return

    snapshot(path)

    if os.path.exists(path):
        with open(path) as f:
            line_no = sum(1 for _ in f) + 1
    else:
        line_no = 1

    with open(path, "a") as f:
        f.write(" ".join(args) + " ")

    print(f"added on line {line_no}")

def cmd_check(args):
    path = load()
    if not path:
        return
    if os.path.exists(path):
        with open(path) as f:
            print(f.read(), end="")


def cmd_dl(args):
    path = load()

    snapshot(path)

    if not path or not os.path.exists(path):
        return
    with open(path) as f:
        lines = f.readlines()
    if lines:
        lines.pop()
        with open(path, "w") as f:
            f.writelines(lines)


def cmd_dsl(args):

    snapshot(path)

    if not args:
        return
    path = load()
    if not path:
        return
    idx = int(args[0]) - 1
    with open(path) as f:
        lines = f.readlines()
    if 0 <= idx < len(lines):
        del lines[idx]
        with open(path, "w") as f:
            f.writelines(lines)


def cmd_rsl(args):

    snapshot(path)
    
    if len(args) < 2:
        return
    path = load()
    if not path:
        return
    idx = int(args[0]) - 1
    with open(path) as f:
        lines = f.readlines()
    if 0 <= idx < len(lines):
        lines[idx] = " ".join(args[1:]) + "\n"
        with open(path, "w") as f:
            f.writelines(lines)


def cmd_rl(args):

    snapshot(path)

    if not args:
        return
    path = load()
    if not path:
        return
    with open(path) as f:
        lines = f.readlines()
    if lines:
        lines[-1] = " ".join(args) + "\n"
        with open(path, "w") as f:
            f.writelines(lines)


def cmd_cl(args):
    if not args:
        return
    path = load()
    if not path:
        return
    idx = int(args[0]) - 1
    with open(path) as f:
        lines = f.readlines()
    if 0 <= idx < len(lines):
        print(lines[idx], end="")


def cmd_addaft(args):
    if len(args) < 2:
        return
    path = load()
    snapshot(path)
    if not path:
        return
    idx = int(args[0])
    with open(path) as f:
        lines = f.readlines()
    lines.insert(idx, " ".join(args[1:]) + "\n")
    with open(path, "w") as f:
        f.writelines(lines)


def cmd_nl(args):
    path = load()
    snapshot(path)
    if not path:
        return
    with open(path, "a") as f:
        f.write("\n")
    print("m: new line added!")


def cmd_delfile(args):
    path = load()
    snapshot(path)
    if not path:
        return
    ans = input("m: are you sure you want to delete? (y/n) ")
    if ans.lower() == "y":
        os.remove(path)
        print("m: deleted!")
    else:
        print("m: deletn't!")


def cmd_watch(args):
    if not args:
        return
    path = args[0]
    prev = None

    def handler(sig, frame):
        print()
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)

    while True:
        if os.path.exists(path):
            h = hash_file(path)
            if h != prev:
                os.system("clear")
                with open(path) as f:
                    for i, line in enumerate(f, 1):
                        print(f"{i:4}: {line}", end="")
                prev = h
        time.sleep(1)

def cmd_undo(args):
    path = load()
    if not path:
        return
    if not UNDO_STACK:
        print("m: nothing to undo")
        return

    with open(path) as f:
        REDO_STACK.append(f.read())

    restore(UNDO_STACK.pop(), path)


def cmd_redo(args):
    path = load()
    if not path:
        return
    if not REDO_STACK:
        print("m: nothing to redo")
        return

    with open(path) as f:
        UNDO_STACK.append(f.read())

    restore(REDO_STACK.pop(), path)

def cmd_ls(args):
    os.system("ls")

def cmd_cd(args):
    os.system(f"cd {args[0]}")

def cmd_pwd(args):
    os.system("pwd")


def cmd_help(args):
    print("""\
welcome to M 2.6.0! this is a lightweight and easy to use text editor.

commands:
  def <path>        define file
  deldef            delete file definition
  checkdef          show file definition
  add <text>        add line
  addaft <n> <txt>  add after line
  addtl             add to last line
  rl <txt>          replace last line
  rsl <n> <txt>     replace selected line
  dl                delete last line
  dsl <n>           delete selected line
  cl <n>            check line
  nl                new line
  check             show file
  delfile           delete file
  undo              undo last change
  redo              redo last undone change
  watch <path>      live view
  exit / quit       leave M
""")


# ---------------- REPL ----------------

COMMANDS = {
    "def": cmd_def,
    "deldef": cmd_deldef,
    "checkdef": cmd_checkdef,
    "add": cmd_add,
    "check": cmd_check,
    "dl": cmd_dl,
    "dsl": cmd_dsl,
    "rsl": cmd_rsl,
    "rl": cmd_rl,
    "cl": cmd_cl,
    "addaft": cmd_addaft,
    "nl": cmd_nl,
    "delfile": cmd_delfile,
    "watch": cmd_watch,
    "help": cmd_help,
    "undo": cmd_undo,
    "redo": cmd_redo,
    "ls": cmd_ls,
    "cd": cmd_cd,
    "pwd": cmd_pwd
}


def repl():
    print("welcome to M-Py v1.0 — type 'help' or 'exit'")
    while True:
        try:
            line = input(f"[{user}@{hostname}] m> ").strip()
        except EOFError:
            print()
            break

        if not line:
            continue

        if line in ("exit", "quit"):
            break

        try:
            parts = shlex.split(line)
        except ValueError as e:
            print(f"m: {e}")
            continue

        cmd = parts[0]
        args = parts[1:]

        fn = COMMANDS.get(cmd)
        if not fn:
            print(f"m: unknown command '{cmd}'")
            continue

        fn(args)


if __name__ == "__main__":
    repl()

