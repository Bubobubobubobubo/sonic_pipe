# Sonic Pipe

![screenshot](sonic_pipe_screenshot.png)

/!\ Beware, things are moving fast rn. /!\ 


I couldn't wait for a new version of [sonic-pi-cli](https://github.com/Widdershin/sonic-pi-cli) or [sonic-pi-tool](https://github.com/lpil/sonic-pi-tool) following the release of Sonic Pi 4.0 so I quickly hacked a script that allows strings to be piped from the command line to the Sonic Pi Server.

The script is a proof of concept based on information gathered from the [Sonic Pi Forum](https://in-thread.sonic-pi.net/). Feel free to change anything and to push changes to the repo :). I don't pretend to replace or do better than the tools mentioned above. Use them if you can once they will be updated!

## Usage

The script requires **python-osc** and the **blessings** library. Once installed, simply run the main script `python3 sonic_pipe` or directly `python3 sonic_pipe/main.py` to start the barebones REPL. As such, you will notice that the REPL is not that useful!

For now (things will evolve for sure), the script was designed to be used along a *slime* session using Vim/Neovim. Open a new terminal, start the script and pipe your code to the REPL with just a keypress!

Basic commands are available:
* **stop** : stop Sonic Pi Server.
* **quit**/**exit** : exit the script.
* **history** : see below.
* **purge-history** : delete history.

## Session History

You can save a snapshot of the ongoing session by typing `save_history`. You can preview the current session history by sending `history` to the REPL:
* `history`: print the whole history.
* `history x`: print the xth command entered since start.
* `history x y`: print history from x to y.

A new file will be written in your `.sonic-pi/sonic_pipe_sessions/` folder. Sessions are named using the current time. Sessions are saved by default on exit, using the `[date]-endofsession` tag. This will ensure that you always keep an history of your code during improvisations. The `purge-history` command can be used to purge the `sonic_pipe_sessions` folder.

# TODO

* Package as a CLI.
* Allow one-shot usage from the command-line.

