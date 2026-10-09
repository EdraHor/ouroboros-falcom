# ouroboros-falcom

A trimmed fork of [Ouroboros/Falcom](https://github.com/Ouroboros/Falcom) ("Decompiler2") for the script files
of **Trails of Cold Steel III** (`Falcom/ED83`), **Trails of Cold Steel IV** (`Falcom/ED84`) and **Trails into
Reverie** (`Falcom/ED85`), with fixes so that every original script of the games decompiles to Python and compiles
back to the same file. Useful for fan translations into any language.

* Branch `main` (this one): only `Decompiler2` for Cold Steel III (ED83), Cold Steel IV (ED84) and Reverie (ED85),
  plus the fixes below.
* Branch `master`: the original repository, unchanged. The upstream README is kept as `README.upstream.md`.

## Requirements

* Python 3.10+
* the helper library `ml` from [ouroboros-pylibs](https://github.com/EdraHor/ouroboros-pylibs) (branch `main`:
  no third-party packages needed)

```
set PYTHONPATH=<this repo>\Decompiler2;<ouroboros-pylibs>
python -m Falcom.ED83.scena2py t0060.dat      -> t0060.py      (Cold Steel III; ED84 Cold Steel IV, ED85 Reverie)
python t0060.py                               -> t0060.dat (written to the current directory)
```

`scena2py` writes a `sys.path.append(...)` line with an absolute path at the top of the generated file; it can be
removed when `PYTHONPATH` is set.

## Fixes (one commit each)

Cold Steel III (ED83, partly shared with ED84):

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

Cold Steel IV (ED84):

8. Opcode `OP_D8` (`e2200`, `m1300`, `m5070`, `m9102`, `r1410`, `r2800`, `t3520` could not be decompiled) and the
   longer `EffectCmd 0x0A` / `LoadEffect` with one more u32 (Japanese `minigame/dat/mg11.dat`, as in ED85).
9. Book files, as for Cold Steel III.
10. Bytes after data tables, as for Cold Steel III (`WithTail`, `BreakTableTerm`); tables end with Return except
    `FaceAuto`. Before, 59 battle files did not compile back.
11. Strings of data tables (AnimeClips paths like `map\m9031_00.eff`, names) are written with escapes.
12. `ParamFloat` values are written exactly (`%g` changed 14 scena files and `btl0409`, -0.0 became 0).
13. An `AlgoTable` that ends the file without its terminator entry (`almon355_c00`, `almon355_c01`) is written back
    as `AlgoTableNoTerm(...)`.

Reverie (ED85):

14. The dword `00 00 00 FF` after the script name is written (every script has it; all offsets were shifted by 4).
15. `OP_3E` with the second word `0xFFFF` has three more bytes (`a1001`, `e3100`), `OP_CF 0x14` a word more
    (`a0000`). The upstream skip list by file offset no longer matched the current game files.
16. Book files (`BookData`), as for Cold Steel III and IV.
17. Data tables are read with the Reverie entry classes (a full terminator entry), `ReactionTable` ends with a
    `0xFFFF` entry, an `AlgoTable` without terminator before short functions (`almon355_c01`); bytes after tables
    are kept (`WithTail`).

## Verification

Every original script of the Steam versions: decompile -> compile -> byte comparison with the original.

Cold Steel III (English):

| folder | files | result |
|---|---|---|
| scena | 364 | 322 identical, 42 differ only by dropped unreachable code |
| talk | 96 | 83 identical, 13 differ only by dropped unreachable code |
| minigame | 2 | identical |
| battle | 475 | identical |
| book | 18 | identical |

Cold Steel IV (English and Japanese):

| folder | files (en / jp) | result |
|---|---|---|
| scena | 448 / 448 | 412 / 412 identical, 36 / 36 differ only by dropped unreachable code |
| talk | 162 / 161 | 144 / 143 identical, 18 / 18 differ only by dropped unreachable code |
| minigame | 6 / 6 | identical |
| battle | 795 / 795 | 789 / 789 identical, 6 / 6 differ only by dropped unreachable code |
| book | 24 / 24 | identical |

Reverie (English; the PC version has no Japanese scripts):

| folder | files | result |
|---|---|---|
| scena | 442 | 415 identical, 27 differ only by dropped unreachable code |
| talk | 140 | 139 identical, 1 differs only by dropped unreachable code |
| minigame | 11 | identical |
| battle | 1172 | 1170 identical, 2 differ only by dropped unreachable code |
| book | 29 | identical |

Every Reverie instruction carries a dword with its source line and size; the compiler writes `0xFF000000` there
(as upstream), and the game accepts it. "Identical" for Reverie means identical except these dwords.

"Unreachable code" is what the decompiler leaves out because nothing can reach it (e.g. a jump right after
`Return`, debug functions); it does not change how the game runs. Such files are checked by decompiling the rebuilt
file again: the script is the same. `ani` (animation scripts, no text) is not covered. Five Cold Steel IV
`scena` files (`a0102`, `a0104`, `a0106`, `a0108`, `a2050`) and Reverie `a0106` are Cold Steel III leftovers and are
decompiled with ED83.

## Credits

Decompiler2 and `ml` are by [Ouroboros](https://github.com/Ouroboros). Book and monster set layouts follow
[SenScriptsDecompiler](https://github.com/TwnKey/SenScriptsDecompiler) by TwnKey. `OP_D8` follows the Russian
translation team of Cold Steel IV.
