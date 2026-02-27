# Jack's Time Terminal

A story-driven terminal puzzle game with node-based travel, mini-games, hints, scoring, and encrypted save state.

## Run

```bash
python main.py
```

## Core Commands

- `help`, `man <command>`
- `nodes`, `routes`, `travel <N#>`, `travelgod <N#> <CODE>`
- `games`, `play <game_id>`
- `story`, `story all`, `hint`, `hint <id>`
- `showcode <A|B|C>`
- `solve <colors|chess|code|regex|tictactoe|dilemma> ...`
- `unlock <anything>`
- `godskip <CODE>`
- `isgoal`
- `resetuser Ifuckedup`

## Game Flow

- `N1`: colors
- `N2`: chess fork
- `N3`: code routing
- `N4`: regex rounds
- `N5`: binary-clock tic-tac-toe (`1010`)
- `N6`: Nim gauntlet (3 wins)
- `N7`: dancing goal unlock

## Notes

- Saves are stored in `~/.time_terminal_game/`.
- Configuration is loaded from `nodes.json` with fallback to `Config.json`.
