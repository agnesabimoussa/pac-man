# PLAN.md

- **aabi-mou** — Core / Game Logic / Data layer: config, maze integration,
  gameplay rules, scoring/levels, cheat mode, highscores.
- **miissa** — Rendering / UI / Pygame layer: window, graphics, input,
  menus/HUD/screens, packaging.

## Step 0 — Joint kickoff (do together before splitting)

1. Agree the module/folder layout (see ownership table below).
2. Agree the shared game-state contract: what data describes the maze, the
   player, the ghosts, and overall game status (score, lives, level, time,
   pause/cheat flags) — just the shape, not the behavior. This is the only
   thing miissa's UI is allowed to depend on.
3. Agree on controls (movement keys, pause key, cheat-mode keys).
4. Both skim the assigned maze-generator package's public interface together
   so movement rules and wall rendering agree on the same conventions.


## Folder ownership

| Owner | Areas |
|---|---|
| aabi-mou | config parsing, maze integration, game state & entities, ghost behavior, scoring/levels, cheat-mode logic, highscore system, related tests |
| miissa | window & rendering, input handling, menus/HUD/screens, packaging & deployment |
| Joint (touch only at integration checkpoints) | main entry point wiring, README, Makefile |

---

## aabi-mou — Core / Game Logic / Data

- [x] Configuration: define and document all config keys, defaults, and
      graceful handling of missing/invalid/unknown values.
- [x] Maze integration: wrap the assigned maze-generator package, handle the
      fixed seed for level 1 vs. random for later levels, handle generation
      failures cleanly.
- [x] Game state & entities: player and ghost movement rules, pacgum and
      super-pacgum placement and consumption, collisions.
- [x] Ghost behavior: chase logic when not edible, flee logic when edible,
      respawn behavior after being eaten.
- [x] Level & scoring rules: score increases, lives, level win/lose
      conditions, level time limit, progression across levels.
- [x] Cheat mode (logic side): invincibility, level skip, ghost freeze, extra
      lives, speed boost, or other useful states — exposed for the UI layer
      to trigger.
- [x] Highscore system: persistent storage, validation of names/scores,
      top-10 tracking, load at start / save at end.
- [ ] Tests covering the above.
- [x] README sections: Configuration, Highscore, Maze Generation.

## miissa — Rendering / UI / Pygame

- [ ] Window setup and main loop.
- [ ] Maze and entity rendering (walls, corridors, pacgums, player, ghosts).
- [ ] In-game HUD: score, lives, level, remaining time.
- [ ] Input handling: movement keys, pause, cheat-mode hotkeys.
- [ ] Main Menu: start game, view highscores, instructions, exit.
- [ ] Pause Menu: resume, return to main menu.
- [ ] Game Over screen and Victory screen, each with name entry for
      highscores.
- [ ] Instructions screen.
- [ ] Packaging and deployment to a public platform (e.g. Itch.io), with
      in-package instructions and a re-runnable packaging script committed
      to the repo.
- [ ] README sections: Implementation, Usage/Instructions, UI-facing part of
      the Software Architecture section.

---

## Integration checkpoints (the only points where shared files are touched)

1. **After Step 0**: both confirm the agreed shared state/contract works for
   their side before building further.
2. **Checkpoint 1**: basic maze + movement (aabi-mou) wired into basic
   rendering + input (miissa).
3. **Checkpoint 2**: scoring/levels/highscores (aabi-mou) wired into the full
   menu/HUD/screen flow (miissa) — full Main Menu → play → win/lose → enter
   name → Main Menu loop working end to end.
4. **Checkpoint 3**: cheat mode wired end to end; joint playtest pass.
5. **Final**: merge README sections, fill in the project-management
   directory (timeline, progress tracking, team organization, risk analysis,
   acceptance test plan), packaging dry run.
