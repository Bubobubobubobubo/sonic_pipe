#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import argparse
from pythonosc import (udp_client, osc_message_builder)
from inputimeout import inputimeout, TimeoutOccurred
from blessings import Terminal
VERSION = '0.0.1'


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

    def input_without_newline(self,
                              prompt_decoration: str = "",
                              timeout: float = 0.1):
        sys.__stdout__, sys.__stderr__ = sys.stdout, sys.stderr
        sys.stdout = open(os.devnull, 'w+')
        line = inputimeout(prompt=prompt_decoration, timeout=0.1)
        sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
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
            self._history.append(final_output)
            return '\n'.join(inputlist)

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

                if prompt == "history":
                    for (i, z) in zip(self._history, range(len(self._history))):
                        print(f"[{z}]: {i}")

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
            self.save_history()
            message = osc_mb.OscMessageBuilder("/stop-all-jobs")
            message.add_arg(int(self._token))
            self._pipe_client.send(message.build())
            print("\nThanks! Bye!")
            quit()

    def is_user_directory_path_valid(self, home_path) -> bool:
        """ Is given user directory folder valid? """
        exists = os.path.isdir(self._home_dir)
        exists_message = (
                f"[{self._home_dir}]: [{'Exists' if exists else 'Not found'}] | ")
        contains = os.path.isdir(
                self._home_dir+"/.sonic-pi/log/")
        contains_message = (
                f"[Spider logs]: [{'Exists' if contains else 'Not found'}]")
        print(exists_message + contains_message)
        if exists and contains:
            return True
        else:
            raise FileNotFoundError

    def extract_values_from_port_line(self, portline):
        """ Extract token and values from port line """
        values = {}

        def pairwise(iterable):
            """ Iterate pairwise on iterator """
            a = iter(iterable)
            return zip(a, a)

        # list of string replacements to perform
        to_replace = ["Ports: {", "", "}", "", "\n", "", ":", " ",
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

    def save_history(self):
        """ Save history of current session to last_session.rb """
        # Increment filename if file already exists
        with open(self._home_dir + '/last_session.rb', 'w') as f:
            for line in self._history:
                f.write("%s\n" % line)


def main():
    parser = argparse.ArgumentParser(
            description='Command line pipe to a running Sonic Pi Instance.')
    arg = parser.parse_args()
    runner = SonicPipe()


if __name__ == "__main__":
    main()
