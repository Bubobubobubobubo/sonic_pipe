#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import argparse
from Utilities import str2bool
from SonicPipe import SonicPipe


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
