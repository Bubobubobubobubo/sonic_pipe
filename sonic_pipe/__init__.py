#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import argparse
from .Utilities import str2bool
from .SonicPipe import SonicPipe

def repl() -> None:
    parser = argparse.ArgumentParser(description='Command line pipe to a running Sonic Pi Instance.')
    parser.add_argument("--daemon", type=str2bool, nargs='?', const=True,
                        default=False, help="Run as daemon.", required=True)
    parser.add_argument("--repl", type=str2bool, nargs='?', const=True,
                        default=False, help="Start as REPL.", required=True)
    arg = parser.parse_args()
    SonicPipe(use_daemon=arg.daemon, repl_mode=arg.repl)