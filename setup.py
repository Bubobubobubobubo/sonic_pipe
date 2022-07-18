#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='sonic_pipe',
      version='0.0.1',
      description='Pipe code from command line to Sonic Pi 4.0 instance',
      author='Raphaël Forment',
      author_email='raphael.forment@gmail.com',
      url='https://github.com/Bubobubobubobubo/sonic_pipe',
      install_requires=['python-osc', 'rich', 'inputimeout', 'art'],
      entry_points={
            'console_scripts': [
                  'sonic-pipe= sonic_pipe:repl']})
