"""Extract keycode tables from various SDK headers."""
import argparse
import os
import re
import sys


def die(*msg):
    print("Error:", *msg, file=sys.stderr)
    raise SystemExit(1)


def linux_read_table(infile):
    if infile is None:
        infile = "/usr/include/linux/input-event-codes.h"
    with open(infile, "rb") as fp:
        text = fp.read()
    for m in re.finditer(rb"#define\s+KEY_(\w+)\s+(\w+)", text):
        if not m.group(2).startswith(b"KEY_"):
            yield int(m.group(2), 0), m.group(1).decode("ASCII")


def macos_open_header(infile):
    if infile is not None:
        return open(infile, "rb")
    # The headers may be in one of these places.
    bases = [
        "/",
        (
            "/Applications/Xcode.app/Contents/Developer/Platforms"
            + "/MacOSX.platform/Developer/SDKs/MacOSX.sdk"
        ),
        "/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk",
    ]
    for base in bases:
        fpath = os.path.join(
            base,
            "System/Library/Frameworks/Carbon.framework"
            + "/Frameworks/HIToolbox.framework/Headers/Events.h",
        )
        try:
            return open(fpath, "rb")
        except FileNotFoundError:
            pass
    die("Could not find Carbon Events.h. Are the developer tools installed?")


def macos_read_table(infile):
    """Read the Linux keymap from Carbon Events.h."""
    with macos_open_header(infile) as fp:
        text = fp.read()
    for m in re.finditer(rb"kVK_(\w+)\s*=\s*(\w+)", text):
        yield int(m.group(2), 0), m.group(1).decode("ASCII")


def windows_read_table(infile):
    if infile is None:
        die("Cannot find WinUser.h automatically, use --input.")
    with open(infile, "rb") as fp:
        text = fp.read()
    for m in re.finditer(rb"#define\s+VK_(\w+)\s+(\w+)", text):
        yield int(m.group(2), 0), m.group(1).decode("ASCII")


PLATFORMS = {
    "linux": linux_read_table,
    "macos": macos_read_table,
    "windows": windows_read_table,
}


def write_table(table, fp):
    for row in table:
        fp.write("{},{}\n".format(*row))


def main(argv):
    p = argparse.ArgumentParser(
        description="Extract keycode tables from various SDK headers"
    )
    p.add_argument(
        "--platform",
        help="extract tables for PLATFORM",
        metavar="PLATFORM",
        choices=PLATFORMS,
        required=True,
    )
    p.add_argument("--input", "-i", help="input header file")
    p.add_argument("--output", "-o", help="output CSV file")
    args = p.parse_args(argv)

    read_table = PLATFORMS[args.platform]
    try:
        table = list(read_table(args.input))
    except FileNotFoundError as ex:
        die(ex)
    if not table:
        die("Could not find keycode definitions in input file.")
    output = args.output
    if output is None:
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output = os.path.join(repo, "data", args.platform + "_scancodes.csv")
    with open(output, "w") as fp:
        write_table(table, fp)


if __name__ == "__main__":
    main(sys.argv[1:])
