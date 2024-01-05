# AntaresChessGUI

This is a work in progress GUI made in python using pygame.
This GUI only supports Mac and Windows currently, but functionality with other platforms will be easy to implement.

## Use the GUI

Currently, there is no download or binary for the GUI.

To use the GUI on your own, you must have a python interpreter installed.
The GUI requires the additional modules: pygame, numpy, pyperclip.

## Functionality

This GUI currently supports playing a "game" of chess. A user can make moves on the GUI.
The GUI will automatically exit once the game has ended, e.g. checkmate or stalemate hass been reached.

This GUI also supports analysis with one engine, Altair (6.0.0).

Currently, adding other engines must be done manually by adding them in the Engines folder and changing one line in the python code.
Importing and Exporting Fens is also supported.

## TODO

A short unordered TODO list.

- An undo move button
- Keep the GUI open after a game has ended
- Starting a new game
  - Create games with clocks / time controls
  - Create games with different options (TBD)
- Implement the import PGN button
- Support selecting and adding engines
