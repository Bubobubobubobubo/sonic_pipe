#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import os
import contextlib
import argparse
import traceback
import subprocess
import threading

from rich import print as rich_print
from rich.console import Console
from rich.markdown import Markdown
from art import tprint

from pythonosc import (udp_client, osc_message_builder,
                       dispatcher, osc_server)
from inputimeout import (inputimeout, TimeoutOccurred)

from dataclasses import dataclass, field
from typing import Any, List

from time import sleep, strftime
from platform import system
from subprocess import PIPE
from queue import Queue

from Utilities import (color, str2bool)
from History import HistoryItem
from Logs import Logs
from DaemonConfig import DaemonConfig
from CommandParsing import CommandParser


class SonicPipe():

    """
    SonicPipe is a tool made to pipe strings from the terminal
    to a daemon session or already opened session of Sonic Pi.
    You can use it along a Vim/Neovim Slime Session or as a
    standard Python Library. The software is modal and can be
    used in multiple ways:

    - **daemon**:
        - true: the script will attempt to boot Sonic Pi in the
          background and hold the session open until the script
          is terminated by sending "exit" or by pressing ^D.
        - false: the script will attempt to find if a Sonic Pi
          session is already running and find the right ports
          and addresses to talk to it.
    - **repl**:
        - true: the current buffer will turn into a loop of
          timeout controlled stdin queries. Every line received
          will either be interpreted as Sonic Pi code or, for a
          few reserved keywords, as an additional command made
          available by Sonic Pipe.
        - false: currently unavailable!

    Sonic Pipe will attempt to log the history of every session.
    Sessions can be found at $HOME/.sonic-pi/sonic-pipe-sessions.

    An embedded help system running with Markdown files has been
    added and can be accessed by various "help_x" methods. See
    documentation for more information about this feature.

    """

    def __init__(self, address='127.0.0.1', use_daemon=False,
                 daemon_rb_location: str = None, repl_mode=True):

        ########################################
        # LOCATE DAEMON.RB FILE
        ########################################

        try:
            self._ruby_daemon_path = self.find_daemon_path(
                    daemon_rb_location)
        except FileNotFoundError:
            print("Invalid path for daemon.rb file.")
            quit()
        self._use_daemon = use_daemon
        self._daemon = None
        self._daemon_killed_by_user = False

        ########################################
        # DATA INIT
        ########################################

        self._values = None
        self._address = address
        self._home_dir = os.path.expanduser('~')
        self._logs = Queue()
        self._repl_mode = repl_mode

        # History Management
        self._history = []

        ########################################
        # GATHER OSC INFORMATION / BOOT SUBPROC
        ########################################

        try:
            if not self._use_daemon:
                self.find_address_and_token()
            else:
                # booting through the daemon.rb script
                self.boot_daemon()

            if self._repl_mode:
                # print some nice ascii art :)
                self.greeter()

        except Exception as e:
            print(f"Couldn't find token or boot: {e}")
            print(traceback.format_exc())
            quit()

        ########################################
        # OSC CLIENT/SERV AND ENTERING MAIN LOOP
        ########################################

        try:

            if self._use_daemon:
                self._daemon_client = udp_client.SimpleUDPClient(
                        self._address, int(self._values.daemon_keep_alive))

            self._pipe_client = udp_client.SimpleUDPClient(
                    self._address, int(self._values.gui_send_to_server))

            self.setup_log_server()

            if self._repl_mode:
                # entering infinite timeout of stdin queries.
                self.repl_mode_main_loop()

        except Exception as e:
            print(f"Failure to finish initialization: {e}")
            print(traceback.format_exc())

        ########################################
        # OTHER USAGES POSSIBLE AFTER INIT     #
        ########################################

        if self._use_daemon and not self._daemon_killed_by_user:
            # Whatever we do in daemon mode, we need to ping the service.
            self.keep_alive_anyway()
        else:
            # We don't need to keep anything alive!
            pass

    def greeter(self):

        """
        ASCII Art banner displayed when booting in REPL mode.
        """

        tprint("Sonic Pipe", font="swan")
        print(f"Token: {self._values.token} OSC port:\
                {self._values.gui_listen_to_server}")
        print("See documentation on GitHub :')")

    def setup_log_server(self):

        """
        Opening up a server to display Sonic Pi GUI
        logs from the terminal.
        """

        # A dispatcher for OSC messages
        self._dispatcher, self._dispatcher_lock = (
            dispatcher.Dispatcher(), threading.Lock())
        self._log_server = osc_server.BlockingOSCUDPServer(
                ('127.0.0.1', int(self._values.gui_listen_to_server)),
                self._dispatcher)

        # Setting up custom dispatchers for every type of information
        self._dispatcher.map(
                "/log/info", self.log_info_dispatcher)
        self._dispatcher.map(
                "/log/multi_message", self.log_multi_message_dispatcher)
        self._dispatcher.map(
                "/error", self.error_dispatcher)
        self._dispatcher.map(
                "/syntax_error", self.syntax_error_dispatcher)

        # Starting the blocking server in another thread: dirty but it works!
        self._log_server_thread = threading.Thread(
            target=self._log_server.serve_forever)
        self._log_server_thread.daemon = True
        self._log_server_thread.start()

    def log_info_dispatcher(self, address: str,
                            fixed_argument: List[Any],
                            *osc_arguments: List[Any]) -> None:

        """
        Dealing with /log/info messages coming from the OSC server.
        """

        self._logs.put_nowait(color.YELLOW + "\n".join(
            osc_arguments) + color.END)

    def log_multi_message_dispatcher(self, address: str,
                                     fixed_argument: List[Any],
                                     *osc_arguments: List[Any]) -> None:

        """
        Dealing with /log/info messages coming from the OSC server.
        """

        self._logs.put_nowait(color.GREEN + " ".join(
            list(map(lambda x: str(x), osc_arguments))) + color.END)

    def error_dispatcher(self, address: str,
                         fixed_argument: List[Any],
                         *osc_arguments: List[Any]) -> None:

        """
        Dealing with /error messages coming from the OSC server
        """

        self._logs.put_nowait(color.RED + " ".join(
            list(map(lambda x: str(x), osc_arguments))) + color.END)

    def syntax_error_dispatcher(self, address: str,
                                fixed_argument: List[Any],
                                *osc_arguments: List[Any]) -> None:

        """
        Dealing with /syntax_error messages coming from the OSC server
        """

        self._logs.put_nowait(color.RED + " ".join(
            list(map(lambda x: str(x), osc_arguments))) + color.END)

    def keep_alive_anyway(self):

        """
        This function will attempt to keep the daemon alive outside of
        the main loop. This is to allow usage of the SonicPipe class in
        a Python REPL or in any program not relying on the REPL mode.
        """

        osc_mb = osc_message_builder

        def awake():
            while self._keep_alive:
                if self._daemon.poll() is not None:
                    print("Daemon died! Daemon should stay alive")
                    quit()
                keep_alive = osc_mb.OscMessageBuilder("/daemon/keep-alive")
                keep_alive.add_arg(self._values.token)
                self._daemon_client.send(keep_alive.build())
                sleep(0.2)

        self._keep_alive = threading.Event()
        self._alive_thread = threading.Thread(target=awake)
        self._alive_thread.start()
        print("Started keep alive dedicated thread.")

    def find_daemon_path(self, user_provided: str = None):

        """
        Find OS path to the daemon.rb file.
        """

        user_os = system()

        if user_provided is not None:
            if os.path.isfile(user_provided):
                return user_provided
            else:
                raise FileNotFoundError
        else:
            # Linters can be quite lost using this new Python syntax.
            match user_os:
                case 'Windows':
                    # I don't have a Windows Computer to verify 
                    return "C:/Program\\ Files/Sonic\\ Pi/app/server/ruby/bin/daemon.rb"
                case 'Linux':
                    print("Not implemented yet...")
                    quit()
                    return "blibli"
                case 'Darwin':
                    return '/Applications/Sonic\\ Pi.app/Contents/Resources/app/server/ruby/bin/daemon.rb'

    def boot_daemon(self):

        """
        Boot Sonic Pi Ruby Daemon. Gather information from the daemon,
        necessary for piping messages, receiving logs and keeping the
        daemon.rb process alive!
        """

        self._daemon = subprocess.Popen(
            f"ruby {self._ruby_daemon_path}",
            shell=True, stdout=PIPE)
        while self._values is None:
            for line in self._daemon.stdout:
                if line != b'':
                    values = line.rstrip().decode('utf-8').split(" ")
                    try:
                        values = list(map(lambda x: int(x), values))
                    except Exception as e:
                        print(f"Couldn't boot Sonic Pi Daemon: {e}")
                        quit()
                    self._values = DaemonConfig(
                        daemon_keep_alive=values[0],
                        gui_listen_to_server=values[1],
                        gui_send_to_server=values[2],
                        scsynth=values[3],
                        osc_cues=values[4],
                        tau_api=values[5],
                        tau_phx=values[6],
                        token=values[7])
                    break

                self._daemon.stdout.flush()

    def input_without_newline(self, prompt_decoration: str = "", timeout: float = 0.1):

        """
        A very hacky function that will perform a timeout based stdin query.
        For cosmetic reasons, stdin content will not be echoed to sdout by
        temporarily disabling the latter. This is not great, but this is not
        bad either I guess... The function seems to cause problems with other
        libraries used to manipulate the terminal.
        """

        with contextlib.redirect_stdout(open(os.devnull, 'w')):
            print("\n")
            line = inputimeout(prompt=prompt_decoration, timeout=timeout)
        return line

    def input_multiline(self, prompt_decoration: str = "") -> str:

        """
        Handling multiline input in REPL mode.
        """

        inputlist = []
        while True:
            try:
                line = self.input_without_newline()
                if line != '':
                    inputlist.append(line)
            except TimeoutOccurred:
                break
        final_output = '\n'.join(inputlist)
        if inputlist == []:
            return None
        else:
            self._history.append(HistoryItem(
                date=strftime("%Y:%b:%d:%H:%M:%S"),
                code=final_output))
            return '\n'.join(inputlist)

    def set_initial_volume(self, volume=0.75):

        """
        Using this function, one can try to set Sonic Pi's default
        volume at the beginning of the main loop.
        """

        if self._pipe_client:
            message = osc_message_builder.OscMessageBuilder("/run-code")
            message.add_arg(self._values.token)
            message.add_arg(f"set_volume! {volume}")
            self._pipe_client.send(message.build())

    def _send_keep_alive_message(self):

        """
        Format and send the keep alive message required by daemon.rb
        """

        keep_alive = osc_message_builder.OscMessageBuilder("/daemon/keep-alive")
        keep_alive.add_arg(self._values.token)
        self._daemon_client.send(keep_alive.build())

    def repl_mode_main_loop(self):

        """
        Main loop of the REPL mode.
        """

        self.set_initial_volume()
        command_parser = CommandParser(
            history=self._history,
            logs=self._logs,
            daemon=self._daemon,
            client_pipe=self._pipe_client,
            use_daemon = self._use_daemon,
            token=self._values.token)

        try:
            while True:

                if self._use_daemon:
                    if self._daemon.poll() is not None:
                        print("Daemon died! Daemon should stay alive.")
                        quit()
                    self._send_keep_alive_message()

                while not self._logs.empty():
                    if self._logs.full():
                        # If the queue is full, don't loose time
                        self._logs.queue.clear()
                    print("\n" + self._logs.get())

                prompt = self.input_multiline()
                if prompt is None:
                    continue
                command_parser.parse(prompt)

        except KeyboardInterrupt:
            self._daemon_killed_by_user = True
            # TODO: Fix the autosaving on quit
            self.stop_all_jobs()
            if self._use_daemon:
                self._daemon.terminate()
            self._exit_banner()
            quit()

    def extract_values_from_port_line(self, portline):

        """
        Grab the message received from spider.log and interpret data.
        """

        values = {}

        def pairwise(iterable):
            """ Iterate pairwise on iterator """
            a = iter(iterable)
            return zip(a, a)

        # list of string replacements to perform
        to_replace = [
            "Ports: {", "", "}",
            "", "\n", "", ":", " ",
            ",", " ", "=>", " "]

        for token, replacer in pairwise(to_replace):
            portline = portline.replace(token, replacer)
        portline = portline.split(" ")
        portline = [x for x in filter(
                lambda x: x != "",
                portline)]
        for field, value in pairwise(portline):
            values[field] = int(value)

        return values

    def find_address_and_token(self):

        """
        Reading the spider.log file to gather necessary ports and
        addresses used by the script. This function is only used
        for the spider.log method of booting.
        """

        suffix = "/.sonic-pi/log/spider.log"

        port_line = None
        token_line = None
        with open(self._home_dir + suffix, "r") as f:
            for i in f.readlines():
                if i.startswith("Ports:"):
                    port_line = i
                if i.startswith("Token: "):
                    token_line = i

        self._values = self.extract_values_from_port_line(port_line)
        print(self._values)

        self._values = DaemonConfig(
            daemon_keep_alive=self._values['server_port'],
            gui_listen_to_server=self._values['gui_port'],
            gui_send_to_server=self._values['scsynth_port'],
            scsynth=self._values['scsynth_send_port'],
            osc_cues=self._values['osc_cues_port'],
            tau_api=self._values['tau_port'],
            tau_phx=self._values['listen_to_tau_port'],
            token=abs(int(token_line.replace("Token: ", ""))))