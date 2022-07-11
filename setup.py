#!/usr/bin/env python3
from distutils.core import setup

setup(name='sonic_pipe',
      version='0.0.1',
      description='Pipe code from command line to Sonic Pi 4.0 instance',
      author='Raphaël Forment',
      author_email='raphael.forment@gmail.com',
      url='https://github.com/Bubobubobubobubo/sonic_pipe',
      install_requires=[
            'python-osc',
            'blessings',
            'inputimeout'],
      entry_points={'console_scripts': [
          'slime = sonic_pipe.main:main']
                }
      )
