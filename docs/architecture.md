# Architecture

> Skeleton — fill in as the design solidifies.

## Overview

_Brief description of how the game is structured and why._

## Modules

| File | Responsibility |
| ---- | --------------- |
| `main.py` | Entry point; starts the game. |
| `executive.py` | Game loop, event handling, board setup, rendering, win/loss logic. |
| `cell.py` | `Cell` data model (mine/revealed/flagged/adjacent-mine state). |

## Data Flow / Game Loop

_Describe the Pygame event loop: input handling → state updates → rendering._

## Key Design Decisions

- _e.g. why the first click is protected from mines_
- _e.g. why flood-fill is implemented recursively_
- _e.g. grid size / mine count bounds_

## Known Limitations / Future Work

_List anything intentionally left out of scope, or planned improvements._

## Diagrams

_Add any diagrams (e.g. component diagram, state diagram) here._
