# ouroboros-falcom

A trimmed fork of [Ouroboros/Falcom](https://github.com/Ouroboros/Falcom) ("Decompiler2") for the script files
of **Trails of Cold Steel III** (`Falcom/ED83`), with fixes so that every original script of the game decompiles
to Python and compiles back to the same file. Useful for fan translations into any language.

* Branch `main` (this one): only `Decompiler2` for Cold Steel III (ED83), Cold Steel IV (ED84) and Reverie (ED85),
  plus the fixes below. All fixes are in ED83 (and one in the shared `Assembler`); ED84/ED85 are as upstream.
* Branch `master`: the original repository, unchanged. The upstream README is kept as `README.upstream.md`.

## Requirements

* Python 3.10+
* the helper library `ml` from [ouroboros-pylibs](https://github.com/EdraHor/ouroboros-pylibs) (branch `main`:
  no third-party packages needed)

```
set PYTHONPATH=<this repo>\Decompiler2;<ouroboros-pylibs>
python -m Falcom.ED83.scena2py t0060.dat      -> t0060.py
python t0060.py                               -> t0060.dat (written to the current directory)
```

`scena2py` writes a `sys.path.append(...)` line with an absolute path at the top of the generated file; it can be
removed when `PYTHONPATH` is set.

## Fixes (one commit each)

1. `ModelCmd 0x07` takes 8 int operands, like `0x08`. Before, the operands were decoded as instructions and the
   rebuilt `system.dat` (ARCUS menu) crashed the game.
2. Floats are formatted exactly (`repr`). `'%g'` kept 6 significant digits and turned tiny values (integers stored
   in float operands, e.g. in `OP_BC`) into 0.
3. Data tables: while parsing, each table is serialized again and compared with the file (a mismatch stops with an
   error); bytes after it that the table class does not describe are kept as `WithTail(table, tail = b'...')`.
   Tables end with a Return byte (`0x01`) like the game's own files; no padding after the last function.
   Before, battle `ActionTable`s lost about 190 bytes each.
4. `AlgoTable` terminator is 2 bytes, as it is read (parameters 1,2,3,4 were written into it); `BreakTable`
   terminator keeps its high word (0 or 1); `ReactionTable` reads up to 8 entries (was 4).
   (Upstream fixed the same kind of problems for ED85 in `e72d414`.)
5. Battle monster sets: after the 8 probabilities there are either 8 zero bytes or a monster name padded to
   12 bytes (rule from [SenScriptsDecompiler](https://github.com/TwnKey/SenScriptsDecompiler)). `r4400` could not
   be decompiled before; these bytes are now written back instead of zeros.
6. Book files (`data/scripts/book`, functions `BookDataNN_MM`): new types `ScenaBookData99` / `ScenaBookData`,
   layout from SenScriptsDecompiler. Books could not be decompiled before.
7. `ReplaceBGMReset()` helper (used by decompiled `a0000`).

## Verification

Every original English script of the Steam version: decompile -> compile -> byte comparison with the original.

| folder | files | result |
|---|---|---|
| scena | 364 | 322 identical, 42 differ only by dropped unreachable code |
| talk | 96 | 83 identical, 13 differ only by dropped unreachable code |
| minigame | 2 | identical |
| battle | 475 | identical |
| book | 18 | identical |

"Unreachable code" is what the decompiler leaves out because nothing can reach it (e.g. a jump right after
`Return`, debug functions); it does not change how the game runs. `ani` (animation scripts, no text) is not covered.

## Credits

Decompiler2 and `ml` are by [Ouroboros](https://github.com/Ouroboros). Book and monster set layouts follow
[SenScriptsDecompiler](https://github.com/TwnKey/SenScriptsDecompiler) by TwnKey.
