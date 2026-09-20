# Architecture

> As the program is now

## Overview

This game is structured in 3 blocks. First, the user selects the mine count. Then, the user plays the actual minesweeper. Then, dependent on win or loss, the user gets a screen displayed accordingly. This makes the game flow simple and easy to follow.

## Modules

| File | Responsibility |
| ---- | --------------- |
| `main.py` | Entry point; starts the game. |
| `executive.py` | Game loop, event handling, board setup, rendering, win/loss logic. |
| `cell.py` | `Cell` data model (mine/revealed/flagged/adjacent-mine state). |

## Data Flow / Game Loop

PyGame follows a loop of updating constantly. Whenever the user moves anything, PyGame will update it to be seen. This is shown through the user being able to move a slider to select their mine count and play minesweeper with almost instantaneous results from inputs. It works by using a while True loop to cycle through the current board state constantly.

## Key Design Decisions

- First click is protected from mines and ensures it is not surrounded by mines to make the game winnable.
- Empty spaces are filled in using a recursive flood fill to clear all adjoining non mine connected spaces
- The board is 10x10 and can accommodate 10-20 mines depending on user input.
- PyGame was used for this to make a simple UI that is streamlined and easy to follow

## Known Limitations / Future Work

- The game does not restart automatically, so adding a button to do that would be a primary goal.
- Board size is limited to 10x10, this could be extended upon to make more challenging minesweeper modes


## Diagrams
<img width="619" height="377" alt="state diagram" src="https://github.com/user-attachments/assets/46e4518d-9aa0-4b80-b039-25517eac84aa" />

