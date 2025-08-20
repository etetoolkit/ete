#!/usr/bin/env python3
"""
ExternalCmdInvoker
~~~~~~~~~~~~~~~~~~
Cross-platform external command execution helper.
This module provides functionality to execute external commands in a cross-platform manner,
handling differences between Windows and Unix-like systems appropriately.

Example usage:
    >>> from ete4.py4egps_treeview import ExternalCmdInvoker
    >>> invoker = ExternalCmdInvoker()
    >>> out, err, code = invoker.run_cmd(["java", "-jar", "MyTool.jar", "--help"])
"""
import platform
import subprocess
import shlex
from typing import List, Tuple, Optional, Dict


class ExternalCmdInvoker:
    """
    A class to invoke external commands in a cross-platform manner.

    This class provides functionality to execute external commands with comprehensive
    control over execution parameters, handling differences between Windows and
    Unix-like systems appropriately.

    The class provides two main methods:
    1. run_cmd() - For executing standalone executable files (e.g., java, python)
    2. run_shell_cmd() - For executing shell commands including shell builtins
       (e.g., dir on Windows cmd, ls on Unix shells)
    """

    def _quote(self, args: List[str]) -> str:
        """
        Convert argument list to a command line string suitable for the current OS.
        This method is primarily used for logging/printing purposes to generate
        a copy-pasteable command line string that would execute the same command.

        Args:
            args: List of command arguments

        Returns:
            A properly quoted command line string for the current operating system
        """
        system = platform.system()
        if system == "Windows":
            # Using the official list2cmdline which properly handles spaces and quotes
            from subprocess import list2cmdline
            return list2cmdline(args)
        else:  # Linux / Darwin (macOS)
            # Python 3.8+ provides shlex.join for this purpose
            return shlex.join(args)

    def run_cmd(
            self,
            argv: List[str],
            cwd: Optional[str] = None,
            env: Optional[Dict[str, str]] = None,
            check: bool = False,
            capture_output: bool = True,
            text: bool = True,
    ) -> Tuple[str, str, int]:
        """
        Execute an external command with comprehensive control over execution parameters.

        This method provides a convenient wrapper around subprocess.run with sensible
        defaults for common use cases and proper cross-platform argument handling.

        NOTE: This method executes programs directly and cannot run shell builtin
        commands like 'dir' on Windows or 'ls' on Unix. For shell builtin commands,
        use run_shell_cmd() instead.

        Args:
            argv : List[str]
                Command and its arguments as a list, e.g. ["java", "-jar", "/path/to/app.jar", "--flag", "value"]
                Note: This should not be a shell builtin command.
            cwd : str | None
                Working directory for the command execution; if None, inherits the parent process directory
            env : dict | None
                Additional environment variables; if None, inherits the parent process environment
            check : bool
                If True, raises a CalledProcessError when the command returns a non-zero exit code
            capture_output : bool
                If True, captures and returns stdout and stderr; if False, they are not captured
            text : bool
                If True, returns output as strings; if False, returns output as bytes

        Returns:
            A tuple containing (stdout, stderr, return_code)

        Example:
            >>> invoker = ExternalCmdInvoker()
            >>> out, err, code = invoker.run_cmd(["python", "--version"])
            >>> print(f"Command exited with code: {code}")

        Note:
            This method will NOT work for:
            - Windows cmd builtin commands like 'dir', 'cd'
            - PowerShell commands like 'ls' (which is an alias for Get-ChildItem)
            - Unix shell builtin commands like 'cd', 'export'
        """
        cmd_str = self._quote(argv)
        print(f"[RUN] {cmd_str}")  # Log the copy-pasteable full command line

        completed = subprocess.run(
            argv,
            cwd=cwd,
            env=env,
            check=check,
            capture_output=capture_output,
            text=text,
        )
        return completed.stdout, completed.stderr, completed.returncode

    def run_shell_cmd(
            self,
            cmd: str,
            cwd: Optional[str] = None,
            env: Optional[Dict[str, str]] = None,
            check: bool = False,
            capture_output: bool = True,
            text: bool = True,
    ) -> Tuple[str, str, int]:
        """
        Execute a shell command with comprehensive control over execution parameters.

        This method provides a convenient wrapper around subprocess.run with shell=True,
        allowing execution of shell builtin commands like 'dir' on Windows or 'ls' on Unix.
        Use this method when you need to execute shell builtin commands or when you want
        to execute commands through the system shell.

        Args:
            cmd : str
                The command string to execute through the shell, e.g. "dir" or "ls -l"
            cwd : str | None
                Working directory for the command execution; if None, inherits the parent process directory
            env : dict | None
                Additional environment variables; if None, inherits the parent process environment
            check : bool
                If True, raises a CalledProcessError when the command returns a non-zero exit code
            capture_output : bool
                If True, captures and returns stdout and stderr; if False, they are not captured
            text : bool
                If True, returns output as strings; if False, returns output as bytes

        Returns:
            A tuple containing (stdout, stderr, return_code)

        Example:
            >>> invoker = ExternalCmdInvoker()
            >>> # On Windows (cmd builtins)
            >>> out, err, code = invoker.run_shell_cmd("dir")
            >>>
            >>> # On Windows (PowerShell aliases work when PowerShell is default shell)
            >>> out, err, code = invoker.run_shell_cmd("ls")
            >>>
            >>> # On Unix/Linux/macOS
            >>> out, err, code = invoker.run_shell_cmd("ls -l")
            >>> print(f"Command exited with code: {code}")

        Note:
            This method works for:
            - Windows cmd builtin commands like 'dir', 'cd'
            - PowerShell commands and aliases like 'ls'
            - Unix shell builtin commands like 'cd', 'export'
            - All commands that work when typed directly in the system shell
        """
        print(f"[RUN] {cmd}")  # Log the command

        completed = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            env=env,
            check=check,
            capture_output=capture_output,
            text=text,
        )
        return completed.stdout, completed.stderr, completed.returncode


# For backward compatibility, expose the old function-based interface
def run_cmd(
        argv: List[str],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        check: bool = False,
        capture_output: bool = True,
        text: bool = True,
) -> Tuple[str, str, int]:
    """
    Backward compatibility function.

    Execute an external command with comprehensive control over execution parameters.
    This is a wrapper around ExternalCmdInvoker.run_cmd() for backward compatibility.
    Note: This method cannot execute shell builtin commands like 'dir' on Windows.
    For shell builtin commands, use ExternalCmdInvoker class directly.
    """
    invoker = ExternalCmdInvoker()
    return invoker.run_cmd(argv, cwd, env, check, capture_output, text)


# —————— Simple Example ——————
if __name__ == "__main__":
    # Example: java -jar demo.jar --input sample.txt
    # Running a sample command to demonstrate usage
    invoker = ExternalCmdInvoker()
    out, err, code = invoker.run_shell_cmd(
        ["java", "-jar", "demo.jar", "--input", "sample.txt"], check=False
    )
    print("exit code:", code)
    if out:
        print("stdout:\n", out)
    if err:
        print("stderr:\n", err)
