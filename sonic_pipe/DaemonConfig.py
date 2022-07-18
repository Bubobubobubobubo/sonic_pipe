#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass

@dataclass
class DaemonConfig:

    """
    Storing ports used by Sonic Pi daemon.rb or spider.log file.
    """

    daemon_keep_alive: int
    gui_listen_to_server: int
    gui_send_to_server: int
    scsynth: int
    osc_cues: int
    tau_api: int
    tau_phx: int
    token: int
