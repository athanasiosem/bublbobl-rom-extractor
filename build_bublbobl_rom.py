#!/usr/bin/env python3
"""
bublbobl-rom-extractor — Recover the MAME bublbobl ROM set
from a legitimately-owned Steam copy of Bubble Bobble 4 Friends: The Baron's Workshop 
that ships the original arcade ROMs as an embedded, LZMA-compressed blob 
inside its main binary.

Pipeline (stdlib only — no external tools):
  1. Scan the input .exe/.dll for an embedded LZMA "alone" stream whose
     uncompressed-size field equals 561,408 bytes.
  2. Decompress it in memory with Python's built-in `lzma` module.
  3. Split the blob into individual MAME ROMs per the known layout.
  4. Package them as bublbobl.zip.

Usage:
  python build_bublbobl_rom.py GameBubblebobble_Windows64bit_Release.dll

Author:  Athanasios Emmanouilidis
License: MIT
"""
import argparse
import lzma
import struct
import sys
import zipfile
from pathlib import Path

__version__ = "1.0.0"

BLOB_SIZE = 0x89100  # 561,408 bytes

# LZMA-alone header we are looking for:
#   props byte  0x5D  (pb=2, lp=0, lc=3 — default)
#   dict size   4 bytes little-endian            (wildcarded)
#   unpacked    8 bytes little-endian  == BLOB_SIZE
LZMA_PROPS = 0x5D
LZMA_UNPACKED_LE = struct.pack("<Q", BLOB_SIZE)  # b"\x00\x91\x08\x00\x00\x00\x00\x00"

# (name, start, end_inclusive) within the 561,408-byte blob
ROM_LAYOUT = [
    ("a78-06-1.51", 0x00000, 0x07fff),
    ("a78-05-1.52", 0x08000, 0x17fff),
    ("a78-08.37",   0x18000, 0x1ffff),
    ("a78-07.46",   0x20000, 0x27fff),
    ("a78-01.17",   0x28000, 0x28fff),
    ("a71-25.41",   0x29000, 0x290ff),
    ("a78-09.12",   0x29100, 0x310ff),
    ("a78-10.13",   0x31100, 0x390ff),
    ("a78-11.14",   0x39100, 0x410ff),
    ("a78-12.15",   0x41100, 0x490ff),
    ("a78-13.16",   0x49100, 0x510ff),
    ("a78-14.17",   0x51100, 0x590ff),
    ("a78-15.30",   0x59100, 0x610ff),
    ("a78-16.31",   0x61100, 0x690ff),
    ("a78-17.32",   0x69100, 0x710ff),
    ("a78-18.33",   0x71100, 0x790ff),
    ("a78-19.34",   0x79100, 0x810ff),
    ("a78-20.35",   0x81100, 0x890ff),
]


def find_lzma_offset(data: bytes) -> int:
    """Return the byte offset of the embedded LZMA-alone stream, or -1."""
    pos = 0
    while True:
        hit = data.find(LZMA_UNPACKED_LE, pos)
        if hit < 0:
            return -1
        header_start = hit - 5  # 1 props byte + 4 dict-size bytes precede the size
        if header_start >= 0 and data[header_start] == LZMA_PROPS:
            return header_start
        pos = hit + 1


def decompress_blob(data: bytes, offset: int) -> bytes:
    dec = lzma.LZMADecompressor(format=lzma.FORMAT_ALONE)
    blob = dec.decompress(data[offset:])
    if len(blob) != BLOB_SIZE:
        raise ValueError(f"decompressed size {len(blob)} != expected {BLOB_SIZE}")
    return blob


def build_rom(blob: bytes, out_zip: Path) -> None:
    print(f"splitting blob into {len(ROM_LAYOUT)} files:")
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for name, start, end in ROM_LAYOUT:
            chunk = blob[start:end + 1]
            z.writestr(name, chunk)
            print(f"  {name:14s} 0x{start:05x}-0x{end:05x}  {len(chunk):6d} bytes")
    print(f"wrote {out_zip}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("binary", help="input .exe or .dll containing the embedded ROM")
    ap.add_argument("-o", "--output", default="bublbobl.zip",
                    help="output MAME zip (default: bublbobl.zip)")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = ap.parse_args()

    src = Path(args.binary).resolve()
    if not src.is_file():
        print(f"error: {src} does not exist", file=sys.stderr)
        return 1

    print(f"reading {src} ({src.stat().st_size:,} bytes)")
    data = src.read_bytes()

    offset = find_lzma_offset(data)
    if offset < 0:
        print("error: no matching LZMA stream found — this binary does not "
              "contain a 561,408-byte Bubble Bobble blob.", file=sys.stderr)
        return 2
    print(f"found LZMA stream at offset 0x{offset:x}")

    blob = decompress_blob(data, offset)
    print(f"decompressed {len(blob):,} bytes")

    build_rom(blob, Path(args.output).resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
