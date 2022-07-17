#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from queue import Queue


class Logs():

    """
    Log Items. Deprecated.
    """

    def __init__(self):
        self.info = Queue(maxsize=20)
        self.multi_message = Queue()
        self.error = Queue()
        self.syntax_error = Queue()
