#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import os
import argparse
import signal
from pythonosc import (udp_client, osc_message_builder)
from inputimeout import inputimeout, TimeoutOccurred

class SonicPipe():

    def __init__(self, home_path,
                 address='127.0.0.1', port=4560):

        self._token, self._values = (None, None)
        self._address, self._port = address, port

        # Check if the file containing logs can be found
        try:
            if self.is_user_directory_path_valid(home_path):
                self._user_directory_path = home_path
        except FileNotFoundError:
            print("Invalid path.. Try again..")
            quit()

        # Gather required information for piping strings accross
        try:
            self.find_address_and_token()
            print(f"TOKEN: {self._token} PORT: {self._values['osc_cues_port']}")
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

    def input_multiline(self, prompt_decoration: str = "") -> str:
        timeout, inputlist = 0.1, []
        while True:
            try:
                line = inputimeout(prompt=prompt_decoration, timeout=1)
                if line != '':
                    inputlist.append(line)
            except TimeoutOccurred:
                break
        return '\n'.join(inputlist)

    def pipe_to_sonic_pi(self, pipe_client):
        """ Pipe to send messages to Sonic Pi """
        osc_mb = osc_message_builder
        while True:
            prompt = self.input_multiline()

            # exit REPL if needed
            if prompt in ["exit", "quit", "exit()", "quit()"]:
                quit()

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
                self._pipe_client.send(message.build())

    def is_user_directory_path_valid(self, home_path) -> bool:
        """ Is given user directory folder valid? """
        exists = os.path.isdir(home_path)
        exists_message = (
                f"[{home_path}]: [{'Exists' if exists else 'Not found'}] | ")
        contains = os.path.isdir(
                home_path+"/.sonic-pi/log/")
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
        with open(self._user_directory_path + suffix, "r") as f:
            for i in f.readlines():
                if i.startswith("Ports:"):
                    port_line = i
                if i.startswith("Token: "):
                    token_line = i

        self._values = self.extract_values_from_port_line(
                port_line)
        self._token = int(token_line.replace("Token: ", ""))


def main():
    parser = argparse.ArgumentParser(
            description='Command line pipe to a running Sonic Pi Instance.')
    parser.add_argument('userdir_path', type=str,
                        help="Path to user directory")
    arg = parser.parse_args()
    runner = SonicPipe(home_path=arg.userdir_path)


if __name__ == "__main__":
    main()
