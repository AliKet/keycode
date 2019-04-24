"""Generate keycode maps from extracted data files."""
import argparse
import os
import sys

from common import Error

import tables


def generate(*, datadir, outdir, quiet):
    """Generate keycode library source files.

    Arguments:
      datadir: Directory containing data files
      outdir: Directory to write output source code
      quiet: Print only informational messages
    """
    with tables.ReadFile(datadir, "hid.csv") as fp:
        hid_table = tables.read_hid(fp)
    for key in hid_table:
        print(key)
    for platform in ["linux", "macos", "windows"]:
        fname = "{}_scancodes.csv".format(platform)
        with tables.ReadFile(datadir, fname) as fp:
            scancode_table = tables.read_scancodes(fp)
        for key in scancode_table:
            print(key)


def main(argv):
    p = argparse.ArgumentParser(
        description="Generate keycode maps from extracted data files")
    p.add_argument("--data-dir", help="directory containing input CSV data")
    p.add_argument("--out-dir", help="directory to write generated code")
    p.add_argument("--quiet",
                   "-q",
                   help="print no informational messages",
                   action="store_true")
    args = p.parse_args(argv)

    repodir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datadir = os.path.join(repodir, "data")
    if args.data_dir is not None:
        datadir = args.data_dir
    outdir = os.path.join(repodir, "src")
    if args.out_dir is not None:
        outdir = args.out_dir

    try:
        generate(datadir=datadir, outdir=outdir, quiet=args.quiet)
    except Error as ex:
        print("Error:", ex, file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
