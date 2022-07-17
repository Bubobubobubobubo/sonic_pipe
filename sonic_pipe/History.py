#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Any


@dataclass
class HistoryItem:
    date: Any = None,
    code: str = ''
