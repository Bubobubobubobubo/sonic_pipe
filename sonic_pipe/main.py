#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import contextlib
import argparse
import os
import time
from pythonosc import (udp_client, osc_message_builder)
from inputimeout import inputimeout, TimeoutOccurred
from blessings import Terminal
from dataclasses import dataclass
from typing import Any

VERSION = '0.0.1'

@dataclass
class HistoryItem:
    date: Any = None,
    code: str = '' 


class SonicPipe():

    def __init__(self, address='127.0.0.1', port=4560):

        self._token, self._values = (None, None)
        self._address, self._port = address, port
        self._terminal = Terminal()

        self._home_dir = os.path.expanduser('~')

        # history of inputs
        self._history = []

        # Gather required information for piping strings accross
        try:
            self.find_address_and_token()
            print(
                    self._terminal.bold_red_on_bright_green(
                        f"Sonic Pipe ({VERSION})\nToken: {self._token}"))
            print(f"--> [{self._terminal.bold} quit/exit]{self._terminal.normal}: exit REPL")
            print(f"--> [{self._terminal.bold} stop]: {self._terminal.normal} stop Sonic Pi exec.")
        except Exception as e:
            print(f"Couldn't fetch into spider.log: {e}")
            quit()

        # Opening an OSC client and piping informations accross
        try:
            self._pipe_client = udp_client.SimpleUDPClient(
                    self._address, int(self._values['server_port']))

            self.pipe_to_sonic_pi(self._pipe_client)
        except Exception as e:
            print(f"Failed to instantiate OSC server: {e}")

    def input_without_newline(
        self, prompt_decoration: str = "", timeout: float = 0.1):
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
            # self._history.append(final_output)
            self._history.append(
                HistoryItem(date=time.strftime("%H:%M:%S"),
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

        if command_length == 3 and all(n.isnumeric() for n in split[1:]):
            for item in self._history[int(split[1]):int(split[2] ) + 1]:
                print(f"[{self._history.index(item)}] ({item.date}): {item.code}")

    def pipe_to_sonic_pi(self, pipe_client):
        """ Pipe to send messages to Sonic Pi """
        osc_mb = osc_message_builder
        try:
            while True:
                prompt = self.input_multiline()
                if prompt is None:
                    continue

                # exit REPL if needed
                if prompt in ["exit", "quit", "exit()", "quit()"]:
                    quit()

                # search last commands history
                if prompt.startswith("history"):
                    self.print_history(prompt)

                if prompt == "save_history":
                    self.save_history()

                # stop Sonic Pi jobs
                if prompt in ["stop", "stop-all-jobs"]:
                    message = osc_mb.OscMessageBuilder("/stop-all-jobs")
                    message.add_arg(int(self._token))
                    self._pipe_client.send(message.build())

                # Other messages
                message = osc_mb.OscMessageBuilder("/run-code")
                message.add_arg(int(self._token))
                message.add_arg(prompt)
                if any(c.isalpha() for c in prompt):
                    print(self._terminal.flash())
                    self._pipe_client.send(message.build())

        except KeyboardInterrupt:
            self.save_history(on_quit=True)
            message = osc_mb.OscMessageBuilder("/stop-all-jobs")
            message.add_arg(int(self._token))
            self._pipe_client.send(message.build())
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

        self._values = self.extract_values_from_port_line(
                port_line)
        self._token = int(token_line.replace("Token: ", ""))

    def save_history(self, on_quit: bool):
        """ Save history of current session to last_session.rb """
        # Create folder if folder doesn't exist yet
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


def main():
    parser = argparse.ArgumentParser(
            description='Command line pipe to a running Sonic Pi Instance.')
    arg = parser.parse_args()
    runner = SonicPipe()


if __name__ == "__main__":
    main()
