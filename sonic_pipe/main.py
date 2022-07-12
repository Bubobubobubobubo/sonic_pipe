#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import contextlib
import argparse
import traceback
import os
import time
import pty
from pythonosc import (udp_client, osc_message_builder)
from inputimeout import (inputimeout, TimeoutOccurred)
from blessings import Terminal
from dataclasses import dataclass
from typing import Any
from platform import system
import subprocess
from subprocess import PIPE
import threading

VERSION = '0.0.1'


@dataclass
class HistoryItem:
    date: Any = None,
    code: str = ''


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


class SonicPipe():

    """
    SonicPipe is a tool made to pipe strings from the terminal
    to a running Sonic Pi session. It allows you to use Sonic Pi
    from outside the default IDE (Vim/Neovim/Emacs/etc).
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

        self._terminal = Terminal()
        st = self._terminal.standout
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
                self.boot_daemon()

            print("=-"*10)
            print(f"Sonic Pipe ({VERSION})\nToken: {self._values.token}")
            print(f"OSC port: {self._values.gui_listen_to_server}")
            print(self.daemon_or_spider_mode_print())
            print("=-"*10)
            print(f"{st('quit/exit:')} exit CLI.")
            print(f"{st('stop:')} stop Sonic Pi.")
            print(f"{st('(purge-)history:')}\nsave/purge history")
        except Exception as e:
            print(f"Couldn't find token and server information: {e}")
            print(traceback.format_exc())
            quit()

        ########################################
        # OSC CLIENT AND ENTERING MAIN LOOP
        ########################################

        try:

            if self._use_daemon:
                self._daemon_client = udp_client.SimpleUDPClient(
                        self._address, int(self._values.daemon_keep_alive))

            self._pipe_client = udp_client.SimpleUDPClient(
                    self._address, int(self._values.gui_send_to_server))

            if self._repl_mode:
                self.repl_mode_main_loop()

        except Exception as e:
            print(f"Failure in Main Loop: {e}")
            print(traceback.format_exc())

        ########################################
        # OTHER USAGES POSSIBLE AFTER INIT     #
        ########################################
        # Need to keep-alive anyway, whatever happens
        if self._use_daemon:
            self.keep_alive_anyway()
        else:
            # We don't need to keep anything alive!
            pass

    def keep_alive_anyway(self):
        """ Function to keep daemon alive outside of main loop """
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
        return ("[X] DAEMON [] SPIDER" if self._use_daemon
                else "[] DAEMON [X] SPIDER")

    def find_daemon_path(self, user_provided: str = None):
        """ Find OS path to the daemon.rb file. """
        user_os = system()

        if user_provided is not None:
            if os.path.isfile(user_provided):
                return user_provided
            else:
                raise FileNotFoundError
        else:
            match user_os:
                case 'Windows':
                    # I don't have a Windows Computer to verify 
                    return "C:/Program\\ Files/Sonic\\ Pi/app/server/ruby/bin/daemon.rb"
                case 'Linux':
                    return "blibli"
                case 'Darwin':
                    return '/Applications/Sonic\\ Pi.app/Contents/Resources/app/server/ruby/bin/daemon.rb'

    def boot_daemon(self):
        """ Boot Sonic Pi Ruby Daemon and keep alive)"""

        self._daemon = subprocess.Popen(
            f"ruby {self._ruby_daemon_path}",
            shell=True, stdout=PIPE)
        while self._values is None:
            for line in self._daemon.stdout:
                if line != b'':
                    values = line.rstrip().decode('utf-8').split(" ")
                    values = list(map(lambda x: int(x), values))

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
        with contextlib.redirect_stdout(open(os.devnull, 'w')):
            line = inputimeout(prompt=prompt_decoration, timeout=0.1)
        return line

    def input_multiline(self, prompt_decoration: str = "") -> str:
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
            self._history.append(HistoryItem(date=time.strftime("%H:%M:%S"),
                                             code=final_output))
            return '\n'.join(inputlist)

    def print_history(self, prompt):
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
            for item in self._history[int(split[1]):int(split[2] ) + 1]:
                print(f"[{self._history.index(item)}] ({item.date}): {item.code}")

    def send(self):
        """ Send a string for eval at Sonic Pi """
        if self._pipe_client:
            message = osc_mb.OscMessageBuilder("/run-code")
            message.add_arg(self._values.token)
            message.add_arg(prompt)
            if any(c.isalpha() for c in prompt):
                print(self._terminal.flash())
                self._pipe_client.send(message.build())

    def stop(self):
        """ Stop code from running in Sonic Pi """
        if self._pipe_client:
            message = osc_mb.OscMessageBuilder("/stop-all-jobs")
            message.add_arg(self._values.token)
            self._pipe_client.send(message.build())

    def repl_mode_main_loop(self):
        """ Pipe to send messages to Sonic Pi """
        osc_mb = osc_message_builder
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
                    print("\nThanks! Bye!")
                    quit()

                if prompt == "debug":
                    print(self._values)

                if prompt == "purge-history":
                    self.purge_history()

                # search last commands history
                if prompt.startswith("history"):
                    self.print_history(prompt)

                if prompt == "save_history":
                    self.save_history(on_quit=False)

                # stop Sonic Pi jobs
                if prompt in ["stop", "stop-all-jobs"]:
                    message = osc_mb.OscMessageBuilder("/stop-all-jobs")
                    message.add_arg(self._values.token)
                    self._pipe_client.send(message.build())

                message = osc_mb.OscMessageBuilder("/run-code")
                message.add_arg(self._values.token)
                message.add_arg(prompt)
                if any(c.isalpha() for c in prompt):
                    print(self._terminal.flash())
                    self._pipe_client.send(message.build())

        except KeyboardInterrupt:
            self.save_history(on_quit=True)
            message = osc_mb.OscMessageBuilder("/stop-all-jobs")
            message.add_arg(self._values.token)
            self._pipe_client.send(message.build())
            if self._use_daemon:
                self._daemon.terminate()
            print("\nThanks! Bye!")
            quit()

    def extract_values_from_port_line(self, portline):
        """ Extract token and values from port line """
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
        """ Find address and token in the logs """
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
        """ Save history of current session to last_session.rb """

        folder = self._home_dir + "/.sonic-pi/sonic_pipe_sessions/"
        if not on_quit:
            sessionname = time.strftime("%H%M%S")
        else:
            sessionname = time.strftime("%H%M%S"+"-endofsession")
        if not os.path.isdir(folder):
            os.mkdir(folder)

        with open(folder + f'{sessionname}.rb', 'w') as f:
            for line in self._history:
                f.write("%s\n" % line.code)

    def purge_history(self):
        """ Purge history of sessions """
        folder = self._home_dir + "/.sonic-pi/sonic_pipe_sessions/"
        if os.path.isdir(folder):
            for file in os.listdir(folder):
                print(f"{file} ... REMOVED.")
                os.remove(os.path.join(folder, file))
            print("Session History has been cleaned.")
        else:
            print("There is nothing to purge.")


def main():
    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

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
