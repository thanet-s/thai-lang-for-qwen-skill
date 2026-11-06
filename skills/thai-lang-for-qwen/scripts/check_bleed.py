#!/usr/bin/env python3
"""Scan Thai text for stray CJK / kana / Hangul / full-width characters.

Language-bleed linter for Thai output: reports suspect characters with
location, context, and a suggested replacement. Report-only by design —
some East-Asian characters are intentional (translation work, quoted
sources), so the caller decides what to fix.

Usage:
  python3 -I check_bleed.py FILE...
  python3 -I check_bleed.py --text "..."
  echo "..." | python3 -I check_bleed.py [--allow CHARS]

Exit status: 1 if any suspect character was found, 0 otherwise.
"""
import argparse
import sys
import unicodedata

# Ranges that should never appear in pure Thai prose.
RANGES = [
    (0x3000, 0x303F, "CJK punctuation"),
    (0x3040, 0x30FF, "kana"),
    (0x3100, 0x312F, "bopomofo"),
    (0x3400, 0x4DBF, "CJK ext A"),
    (0x4E00, 0x9FFF, "CJK ideograph"),
    (0xAC00, 0xD7AF, "Hangul syllable"),
    (0xF900, 0xFAFF, "CJK compat"),
    (0xFF00, 0xFFEF, "full/half-width form"),
]

# High-frequency bleed with a known Thai/ASCII replacement.
SUGGEST = {
    "\u6216": "หรือ",   # 或
    "\u7684": "ของ/ที่",    # 的
    "\u662f": "คือ",      # 是
    "\u6709": "มี",     # 有
    "\u5728": "ใน/อยู่ที่", # 在
    "\u4e86": "แล้ว",  # 了
    "\u548c": "และ",   # 和
    "\u4e0d": "ไม่", # 不
    "\u5f88": "มาก",  # 很
    "\u4eba": "คน",   # 人
    "\u5927": "ใหญ่", # 大
    "\uff0c": ",",        # ，
    "\u3002": ".",        # 。
    "\u3001": ",",        # 、
    "\uff1a": ":",        # ：
    "\uff1b": ";",        # ；
    "\uff1f": "?",        # ？
    "\uff01": "!",        # ！
    "\uff08": "(",        # （
    "\uff09": ")",        # ）
    "\uff02": '"',        # ＂
    "\uff07": "'",        # ＇
}

CONTEXT = 10  # chars of context each side


def classify(ch):
    cp = ord(ch)
    for lo, hi, label in RANGES:
        if lo <= cp <= hi:
            return label
    return None


def scan(label, text, allow, out):
    hits = 0
    for lineno, line in enumerate(text.splitlines(), 1):
        for col, ch in enumerate(line):
            if ch in allow:
                continue
            kind = classify(ch)
            if not kind:
                continue
            hits += 1
            start = max(0, col - CONTEXT)
            ctx = line[start: col + CONTEXT + 1].strip()
            name = unicodedata.name(ch, "?")
            hint = f"=> {SUGGEST[ch]}" if ch in SUGGEST else name
            out(f"{label}:{lineno}:{col + 1}  U+{ord(ch):04X} {ch}  ({kind})"
                f"  ...{ctx}...  {hint}")
    return hits


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="*", type=argparse.FileType("r", encoding="utf-8"))
    parser.add_argument("--text", help="check this string instead of files")
    parser.add_argument("--allow", default="", metavar="CHARS",
                        help="characters to treat as intentional (not bleed)")
    args = parser.parse_args(argv)

    allow = set(args.allow)
    found = 0
    if args.text:
        found += scan("<text>", args.text, allow, print)
    if args.files:
        for fh in args.files:
            found += scan(fh.name, fh.read(), allow, print)
    if not args.text and not args.files:
        found += scan("<stdin>", sys.stdin.read(), allow, print)

    if found == 0:
        print("OK: no suspect characters")
        return 0
    print(f"\n{found} suspect character(s) — fix if not intentional "
          f"(quote sources via --allow)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
