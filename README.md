# M-Py

M-Py is a lightweight, command-line based text editor inspired by traditional Unix line editors. It provides a simple and efficient way to edit text files directly from your terminal.

## Features

- **Line-oriented editing:** Add, delete, and modify lines of text with simple commands.
- **File definition:** Define a file to work on and easily switch between files.
- **Undo/Redo:** Easily undo and redo your changes.
- **Live-view:** Watch a file for changes in real-time.
- **Basic shell commands:** Run basic shell commands without leaving the editor.

## Getting Started

1.  **Run the editor:**
    ```bash
    ./m.py
    ```

2.  **Define a file to edit:**
    ```
    def my_file.txt
    ```

3.  **Start editing:**
    - `add <text>`: Add a new line with the given text.
    - `dl`: Delete the last line.
    - `dsl <line_number>`: Delete the line at the given number.
    - `rl <text>`: Replace the last line with the given text.
    - `rsl <line_number> <text>`: Replace the line at the given number with the given text.
    - `check`: Show the contents of the file.
    - `undo`: Undo the last change.
    - `redo`: Redo the last undone change.

4.  **Get help:**
    Type `help` to see a list of all available commands.

5.  **Exit the editor:**
    Type `exit` or `quit`.

## Vision

M-Py aims to recreate the simplicity and power of older Bash-based text editors in a modern Python environment. It's designed for developers who are comfortable with the command line and prefer a minimalist, keyboard-driven workflow.
