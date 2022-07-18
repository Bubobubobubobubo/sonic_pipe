#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import os
from os import listdir
from os.path import isfile, join
from queue import Queue
from time import strftime
from typing import List, Union

from pythonosc import osc_message_builder
from rich.console import Console
from rich.markdown import Markdown

from .History import HistoryItem


class CommandParser():

    """
    Parse the commands piped to the script.
    """

    def __init__(self, logs: Queue, 
                history: List[HistoryItem],
                use_daemon: bool, token: int,
                client_pipe, daemon):

        self._quit_commands = {
            "exit": self._end_script}
        self._stop_commands = {
            "stop": self._stop_all_jobs,
            "stop-all-jobs": self._stop_all_jobs}
        self._debug_commands = {
            "debug": self._basic_debug}
        self._help_commands = {
            "help": self._show_available_cheatsheets}
        self._history_commands = {
            "history": self._print_history,
            "save_history": self._save_history,
            "purge_history": self._purge_history}

        self._console = Console()
        self._logs, self._history = (logs, history)
        self._home_dir = os.path.expanduser('~')
        self._client_pipe = client_pipe
        self._use_daemon, self._daemon = (use_daemon, daemon)
        self._token = token
        self._cheat_path, self._user_cheat_path = (os.path.dirname(__file__) + "/cheatsheets/",
                                                self._home_dir + "/.sonic-pi/sonic-pipe-help/")

    def get_all_available_commands(self) -> List[str]:

        """
        Get the list of all non Sonic Pi commnads
        """

        list = []
        for commands in [self._stop_commands, self._debug_commands,
                        self._help_commands, self._history_commands]:
            list.append(list(commands.keys()))
        return list

    def parse(self, text_to_parse: str) -> None:

        """
        Main function to parse strings received from the user. Valid methods are stored
        in dictionnaries. Every command can trigger the appropriate response method by
        matching a key.
        """
        text = text_to_parse.lower()

        if text in self._quit_commands:
            self._quit_commands[text]()
        elif text in self._stop_commands:
            self._stop_commands[text]()
        elif text in self._debug_commands:
            self._debug_commands[text]()
        elif text in self._help_commands:
            self._help_commands[text]()
        elif text.split(" ")[0] in self._help_commands:
            # Special case: a specific help file was required by user
            try:
                self._print_user_requested_help_file(text.split(" ")[1])
            except Exception as e:
                print(f"Help file '{text.split(' ')[1]}' does not exist. See list of help files above.\n")
                self._show_available_cheatsheets()
        elif text in self._history_commands:
            self._history_commands[text]() 
        else:
            self._forward_to_sonic_pi(text_to_parse=text_to_parse)

    def _print_user_requested_help_file(self, file_to_open: str) -> None:
        """
        Attempt to print the help file requested by user in Markdown format.
        """
        try:
            with open(self._cheat_path + file_to_open + '.md', "r") as markfile:
                self._console.print(Markdown(markfile.read()))
        except Exception:
            pass

        try:
            with open(self._user_cheat_path + file_to_open + '.md', "r") as markfile:
                self._console.print(Markdown(markfile.read()))
        except Exception:
            pass

    def _forward_to_sonic_pi(self, text_to_parse) -> None:
        message = osc_message_builder.OscMessageBuilder("/run-code")
        message.add_arg(self._token)
        message.add_arg(text_to_parse)
        if any(c.isalpha() for c in text_to_parse):
            self._client_pipe.send(message.build())

    def _print_history(self) -> None:

        """
        Inner function for the history command (see REPL above).
        TODO: regression. Restore more functionalities.
        """

        for index, item in enumerate(self._history):
            print(f"[{index}] ({item.date}): {item.code}")

    def _purge_history(self) -> None:

        """
        Clear out the folder of recorded sessions.
        Destructive operation to be used with care.
        """

        folder = self._home_dir + "/.sonic-pi/sonic_pipe_sessions/"
        if os.path.isdir(folder):
            for file in os.listdir(folder):
                print(f"{file} ... REMOVED.")
                os.remove(os.path.join(folder, file))
            print("Session History has been cleaned.")
        else:
            print("There is nothing to purge.")

    def _save_history(self) -> None:

        """
        Save an history of the current Sonic Pipe session. Every command
        ever played will be recorded in the file. Sessions are name using
        a timetag and an additionnal -endofsession flag for files automa-
        tically saved at the end of each session.
        TODO: regression. Restore -endofsession behavior.
        """

        folder = self._home_dir + "/.sonic-pi/sonic_pipe_sessions/"

        sessionname = strftime("%Y%m%d%H%M%S")
        if not os.path.isdir(folder):
            os.mkdir(folder)

        with open(folder + f'{sessionname}.rb', 'w') as f:
            for line in self._history:
                f.write("%s\n" % line.code)
        print(f"File $HOME/sonic-pi/.sonic-pipe-sessions/{sessionname}.rb written!")

    def _show_available_cheatsheets(self) -> None:

        """
        Returns a Markdown list of available cheasheets
        from the cheatsheets directories.
        """

        def get_file_list(folder_path) -> List[str]:
            if os.path.exists(folder_path):
                files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
                files = list(map(lambda x: x.replace(".md", ""), files))
                files.sort()
                return files
            else:
                return []

        user_cheat_path = self._home_dir + "/.sonic-pi/sonic-pipe-help/"
        default_available_files = get_file_list(self._cheat_path)
        user_available_files = get_file_list(self._user_cheat_path)

        markdown_page = "# Available Cheatsheets\n\n"

        # List of default files
        markdown_page += "## Default help files\n\n"
        for file in default_available_files:
            markdown_page += f"* {file}\n"

        # List of user files
        markdown_page += "## User provided help files\n\n"
        for file in user_available_files:
            markdown_page += f"* {file}\n"

        # General help
        markdown_page += (
                "\nInvoke the help command followed by a file name.\n")
        markdown_page += (
                "\nEx: help midi, help synths.\n")
        self._console.print(Markdown(markdown_page))

    def _stop_all_jobs(self) -> None:

        """
        Replicating Sonic Pi built-in /stop-all-jobs command.
        """

        message = osc_message_builder.OscMessageBuilder("/stop-all-jobs")
        message.add_arg(self._token)
        self._client_pipe.send(message.build())

    def _end_script(self) -> None:

        """
        End the script by killing every service.
        """

        if self._client_pipe:
            self._stop_all_jobs()
        if self._use_daemon:
            self._daemon.terminate()
        
        print("Autosaving on quit!")
        self._save_history()
        quit()

    def _basic_debug(self) -> None:
        """
        Dummy debug command. Used for testing.
        """
        print("Nothing to debug")
