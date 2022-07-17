#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import contextlib
import argparse
import traceback
import os
from rich import print as rich_print
from rich.console import Console
from rich.markdown import Markdown
import time
from pythonosc import (udp_client, osc_message_builder,
                       dispatcher, osc_server)
from inputimeout import (inputimeout, TimeoutOccurred)
from dataclasses import dataclass, field
from typing import Any, List
from platform import system
from art import tprint
import subprocess
from subprocess import PIPE
import threading
from queue import Queue

from Utilities import (color, str2bool)
from History import HistoryItem


@dataclass
class DaemonConfig:
    daemon_keep_alive: int
    gui_listen_to_server: int
    gui_send_to_server: int
    scsynth: int
    osc_cues: int
    tau_api: int
    tau_phx: int
    token: int


class Logs():
    def __init__(self):
        self.info = Queue(maxsize=20)
        self.multi_message = Queue()
        self.error = Queue()
        self.syntax_error = Queue()


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
                # running logs from spider.log
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

        if self._use_daemon:
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
        print(self.daemon_or_spider_mode_print())
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
                time.sleep(0.2)

        self._keep_alive = threading.Event()
        self._alive_thread = threading.Thread(target=awake)
        self._alive_thread.start()
        print("Started keep alive dedicated thread.")

    def daemon_or_spider_mode_print(self):

        """
        Cosmetic function to display current mode.
        TODO: To be removed or replaced by something else.
        """

        return ("[X] DAEMON          [] SPIDER" if self._use_daemon
                else "[] DAEMON          [X] SPIDER")

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

    def input_without_newline(self, prompt_decoration: str = "",
                              timeout: float = 0.1):

        """
        A very hacky function that will perform a timeout based stdin query.
        For cosmetic reasons, stdin content will not be echoed to sdout by
        temporarily disabling the latter. This is not great, but this is not
        bad either I guess... The function seems to cause problems with other
        libraries used to manipulate the terminal.
        """

        with contextlib.redirect_stdout(open(os.devnull, 'w')):
            print("\n")
            line = inputimeout(prompt=prompt_decoration, timeout=0.1)
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
                date=time.strftime("%Y:%b:%d:%H:%M:%S"),
                code=final_output))
            return '\n'.join(inputlist)

    def _print_history(self, prompt):

        """
        Inner function for the history command (see REPL above).
        """

        """ Print history of commands """
        split = prompt.split(" ")
        command_length = len(split)

        if prompt == "history":
            for index, item in enumerate(self._history):
                print(f"[{index}] ({item.date}): {item.code}")

        if command_length == 2 and split[1].isnumeric():
            index = int(split[1])
            if 0 <= index <= len(self._history):
                print(f"[{index}] ({self._history[index].date}): {self._history[index].code}")

        # TODO: this command is broken. Fix it.
        if command_length == 3 and all(n.isnumeric() for n in split[1:]):
            for item in self._history[int(split[1]):int(split[2]) + 1]:
                print(f"[{self._history.index(item)}] ({item.date}): {item.code}")

    def send(self):

        """
        Generic function to send code from the terminal to Sonic Pi
        through OSC.
        """

        if self._pipe_client:
            message = osc_mb.OscMessageBuilder("/run-code")
            message.add_arg(self._values.token)
            message.add_arg(prompt)
            if any(c.isalpha() for c in prompt):
                self._pipe_client.send(message.build())

    def stop(self):

        """
        Replicating Sonic Pi built-in /stop-all-jobs command.
        """

        """ Stop code from running in Sonic Pi """
        if self._pipe_client:
            message = osc_message_builder.OscMessageBuilder("/stop-all-jobs")
            message.add_arg(self._values.token)
            self._pipe_client.send(message.build())

    def set_initial_volume(self, volume=0.8):

        """
        Using this function, one can try to set Sonic Pi's default
        volume at the beginning of the main loop.
        """

        if self._pipe_client:
            message = osc_message_builder.OscMessageBuilder("/run-code")
            message.add_arg(self._values.token)
            message.add_arg(f"set_volume! {volume}")
            self._pipe_client.send(message.build())

    def repl_mode_main_loop(self):

        """
        Main loop of the REPL mode.
        """

        osc_mb = osc_message_builder
        self.set_initial_volume()
        try:
            while True:
                #####################
                # KEEP DAEMON ALIVE #
                #####################

                if self._use_daemon:
                    if self._daemon.poll() is not None:
                        print("Daemon died! Daemon should stay alive")
                        quit()
                    keep_alive = osc_mb.OscMessageBuilder("/daemon/keep-alive")
                    keep_alive.add_arg(self._values.token)
                    self._daemon_client.send(keep_alive.build())

                #####################
                # PRINT LOGS        #
                #####################
                while not self._logs.empty():
                    if self._logs.full():
                        # If the queue is full, don't loose time
                        self._logs.queue.clear()
                    print("\n" + self._logs.get())

                #####################
                # PARSE INPUT       #
                #####################

                prompt = self.input_multiline()
                if prompt is None:
                    continue

                # exit REPL if needed
                if prompt in ["exit", "quit", "exit()", "quit()"]:
                    message = osc_mb.OscMessageBuilder("/stop-all-jobs")
                    message.add_arg(self._values.token)
                    self._pipe_client.send(message.build())
                    if self._use_daemon:
                        self._daemon.terminate()
                    print(color.PURPLE + "\nThanks! Bye!" + color.END)
                    quit()

                if prompt == "debug":
                    print("No debug mode")

                if prompt in ("synths", "help_midi", "help_link", "fxs",
                              "help_ziffers"):
                    console = Console()
                    help_map = {
                            "synths": "cheatsheets/allsynths.md",
                            "fxs": "cheatsheets/allfxs.md",
                            "help_midi": "cheatsheets/midi.md",
                            "help_link": "cheatsheets/link.md",
                            "help_ziffers": "cheatsheets/ziffers.md"}
                    with open(help_map[prompt], 'r') as file:
                        console.print(Markdown(file.read()))

                if prompt == "purge_history":
                    self.purge_history()

                # search last commands history
                if prompt.startswith("history"):
                    self._print_history(prompt)

                if prompt == "save_history":
                    self.save_history(on_quit=False)

                # stop Sonic Pi jobs
                if prompt in ["stop", "stop-all-jobs"]:
                    message = osc_mb.OscMessageBuilder("/stop-all-jobs")
                    message.add_arg(self._values.token)
                    self._pipe_client.send(message.build())

                if prompt not in ("stop", "stop-all-jobs", "save_history", "fxs",
                                  "history", "purge_history", "synths", "debug",
                                  "help_midi", "help_link", "help_ziffers"):
                    message = osc_mb.OscMessageBuilder("/run-code")
                    message.add_arg(self._values.token)
                    message.add_arg(prompt)
                    if any(c.isalpha() for c in prompt):
                        self._pipe_client.send(message.build())

        except KeyboardInterrupt:
            self.save_history(on_quit=True)
            message = osc_mb.OscMessageBuilder("/stop-all-jobs")
            message.add_arg(self._values.token)
            self._pipe_client.send(message.build())
            if self._use_daemon:
                self._daemon.terminate()
            print(color.PURPLE + "\nThanks! Bye!" + color.END)
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

    def save_history(self, on_quit: bool):

        """
        Save an history of the current Sonic Pipe session. Every command
        ever played will be recorded in the file. Sessions are name using
        a timetag and an additionnal -endofsession flag for files automa-
        tically saved at the end of each session.
        """

        folder = self._home_dir + "/.sonic-pi/sonic_pipe_sessions/"
        if not on_quit:
            sessionname = time.strftime("%m%D%H%M%S")
        else:
            sessionname = time.strftime("%m%D%H%M%S"+"-endofsession")
        if not os.path.isdir(folder):
            os.mkdir(folder)

        with open(folder + f'{sessionname}.rb', 'w') as f:
            for line in self._history:
                f.write("%s\n" % line.code)

    def purge_history(self):

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


def main():
    parser = argparse.ArgumentParser(
            description='Command line pipe to a running Sonic Pi Instance.')
    parser.add_argument("--daemon", type=str2bool, nargs='?', const=True,
                        default=False, help="Run as daemon.")
    parser.add_argument("--repl", type=str2bool, nargs='?', const=True,
                        default=False, help="Start as REPL.")
    arg = parser.parse_args()
    runner = SonicPipe(use_daemon=arg.daemon, repl_mode=arg.repl)


if __name__ == "__main__":
    main()
