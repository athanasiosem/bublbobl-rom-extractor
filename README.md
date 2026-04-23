# bublbobl-rom-extractor

Recover the MAME `bublbobl` ROM set from a legitimately-owned Windows build of
*Bubble Bobble* that ships the original arcade ROMs as an embedded,
LZMA-compressed blob inside its main binary (`GameBubblebobble_Windows64bit_Release.dll`).

Pure Python, standard library only — no binwalk, no 7-Zip, no external tools.

## Requirements

- Python 3.3 or newer (for the built-in `lzma` module)
- A copy of the Windows build you legally own

## Usage

```
python build_bublbobl_rom.py GameBubblebobble_Windows64bit_Release.dll
```

Produces `bublbobl.zip` in the current directory. Drop it into your MAME
`roms/` folder and launch:

```
mame bublbobl
```

Options:

```
-o, --output PATH    output zip path (default: bublbobl.zip)
--version            print version and exit
```

## How it works

The Windows release embeds the full arcade ROM data as a single
LZMA "alone"-format stream somewhere inside the DLL. The extractor:

1. Scans the input binary for an LZMA-alone header whose uncompressed-size
   field equals exactly **561,408 bytes** (`0x89100`). The match is anchored on
   the properties byte (`0x5D`) and the 8-byte little-endian size field; the
   dictionary-size field is wildcarded so the tool keeps working if future
   builds change LZMA parameters.
2. Feeds the stream through `lzma.LZMADecompressor(format=FORMAT_ALONE)`.
3. Splits the resulting blob into 18 individual ROM files at the offsets
   shown below.
4. Writes them into a deflate-compressed zip named like MAME expects.

## ROM layout

| File | Offset (hex) | Size | Role |
| --- | --- | --- | --- |
| `a78-06-1.51` | `0x00000`–`0x07fff` | 32 KiB | Main CPU (Z80) program |
| `a78-05-1.52` | `0x08000`–`0x17fff` | 64 KiB | Main CPU program (banked) |
| `a78-08.37`   | `0x18000`–`0x1ffff` | 32 KiB | Sub CPU (Z80) program |
| `a78-07.46`   | `0x20000`–`0x27fff` | 32 KiB | Sound CPU (Z80) program |
| `a78-01.17`   | `0x28000`–`0x28fff` | 4 KiB  | 68705 MCU |
| `a71-25.41`   | `0x29000`–`0x290ff` | 256 B  | Video timing PROM (shared with *Tokio*) |
| `a78-09.12`   | `0x29100`–`0x310ff` | 32 KiB | Graphics |
| `a78-10.13`   | `0x31100`–`0x390ff` | 32 KiB | Graphics |
| `a78-11.14`   | `0x39100`–`0x410ff` | 32 KiB | Graphics |
| `a78-12.15`   | `0x41100`–`0x490ff` | 32 KiB | Graphics |
| `a78-13.16`   | `0x49100`–`0x510ff` | 32 KiB | Graphics |
| `a78-14.17`   | `0x51100`–`0x590ff` | 32 KiB | Graphics |
| `a78-15.30`   | `0x59100`–`0x610ff` | 32 KiB | Graphics |
| `a78-16.31`   | `0x61100`–`0x690ff` | 32 KiB | Graphics |
| `a78-17.32`   | `0x69100`–`0x710ff` | 32 KiB | Graphics |
| `a78-18.33`   | `0x71100`–`0x790ff` | 32 KiB | Graphics |
| `a78-19.34`   | `0x79100`–`0x810ff` | 32 KiB | Graphics |
| `a78-20.35`   | `0x81100`–`0x890ff` | 32 KiB | Graphics |

Total: 561,408 bytes across 18 files, matching the MAME `bublbobl` parent set.

Two PAL chips (`pal16l8.bin`, `pal16r4.bin`) are not present — they are
listed as *NO GOOD DUMP KNOWN* in MAME and emulated in code. MAME prints a
warning about them regardless of the source of your ROM set; the game runs
fine.

## Notes

- The tool operates entirely in memory. Nothing is written to disk except the
  final zip.
- Works on any input that contains the same 561,408-byte LZMA-alone stream,
  so it is resilient to the blob moving to a different offset in future
  builds.
- Exit codes: `0` success, `1` missing input, `2` no matching LZMA stream in
  the binary.

## Legal

This project does **not** include, distribute, or redistribute any
copyrighted ROM data. It only operates on a file the user already owns.

You are responsible for ensuring your use complies with the license of the
Windows release you are extracting from and with the copyright laws of your
jurisdiction. The output of this tool is intended for personal use only
(for example, playing your own copy of the game in MAME on hardware that a
modern native binary cannot target, such as a CRT via GroovyMAME).

Do not redistribute the generated `bublbobl.zip`.

## Author

Athanasios Emmanouilidis

## License

MIT — see [LICENSE](LICENSE).
