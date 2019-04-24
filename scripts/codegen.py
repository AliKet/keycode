# Copyright 2019 Dietrich Epp.
# This file is licensed under the terms of the MIT license. See LICENSE.txt
# for details.
"""Code generation helper functions."""
import io
import os
import sys

from common import Error


class WriteFile:
    """Context manager for writing output files.

    This will add guards, print out informational messages, and decorate
    exceptions inside the context with the filename.
    """

    def __init__(self, dirname, filename, quiet=False, guard=None):
        if not quiet:
            print("Writing", filename, file=sys.stderr)
        try:
            fp = open(os.path.join(dirname, filename), "w")
        except Exception as ex:
            raise Error("Could not create output file: {}".format(ex),
                        filename=filename)
        try:
            fp.write("/* This file is automatically generated. */\n")
            if guard is not None:
                fp.write("#ifndef {0}\n#define {0}\n".format(guard))
        except:
            fp.close()
            raise
        self.fp = fp
        self.guard = guard

    def __enter__(self):
        return self.fp

    def __exit__(self, exc_type, exc_value, exc_tb):
        try:
            if exc_type is None:
                if self.guard is not None:
                    self.fp.write("#endif\n")
        finally:
            self.fp.close()
        if isinstance(exc_value, Error):
            if exc_value.filename is not None:
                exc_value.filename = self.filename


def format_data(data, indent):
    """Format a bytestring as a C string literal.

    Arguments:
      data: Bytestring to write
      indent: Indentation for each line, a string
    Returns:
      A multiline string containing the code, with indentation before every line
      including the first. There is no final newline.
    """
    fp = io.StringIO()
    fp.write(indent)
    fp.write('"')
    rem = 80 - 3 - len(indent)

    def advance(n):
        nonlocal rem
        if rem < n:
            fp.write('"\n')
            fp.write(indent)
            fp.write('"')
            rem = 80 - 3 - len(indent)
        rem -= n

    for n, c in enumerate(data.rstrip(b"\0")):
        if 32 <= c <= 126:
            if c in b'\\"':
                advance(2)
                fp.write("\\")
            else:
                advance(1)
            fp.write(chr(c))
        elif c == 0 and (n == len(data) - 1
                         or not b"0" <= data[n + 1:n + 2] <= b"7"):
            advance(2)
            fp.write("\\0")
        else:
            advance(4)
            fp.write("\\{:03o}".format(c))
    fp.write('"')
    return fp.getvalue()


def format_numbers(numbers, indent):
    """Format an array as comma-separated values across multiple lines.

    Arguments:
      data: Array of numbers to write
      indent: Indentation for each line, a string
    Returns:
      A multiline string containing the code, with indentation before every line
      including the first. There is no final newline.
    """
    fp = io.StringIO()
    fp.write(indent)
    rem = 80 - len(indent)

    def advance(n):
        nonlocal rem
        if rem < n:
            fp.write("\n")
            fp.write(indent)
            rem = 80 - len(indent)
        rem -= n

    for n in numbers[:-1]:
        s = str(n) + ","
        advance(len(s))
        fp.write(s)
    s = str(numbers[-1])
    advance(len(s))
    fp.write(s)
    return fp.getvalue()


def make_string_table(strings):
    """Combine many strings into a single bytestring.

    Arguments:
      strings: List of strings

    Returns:
      (data, strmap), where data is a bytestring containing all of the string
      data, and strmap maps the input strings to their offsets in the
      bytestring. An empty string is always present at offset 0.
    """
    strset = set()
    strlist = []
    for s in sorted(strings, key=lambda s: len(s), reverse=True):
        if s not in strset:
            strlist.append(s)
            strset.update(s[n:] for n in range(len(s)))
    strlist.sort()
    result = io.BytesIO()
    result.write(b"\0")
    for s in strlist:
        result.write(s.encode("ASCII"))
        result.write(b"\0")
    data = result.getvalue()
    strmap = {s: data.index(s.encode("ASCII") + b"\0") for s in strings}
    return data, strmap


def ctype(maxval):
    """Return the smallest unsigned C type with the given range."""
    if maxval < (1 << 8):
        return "unsigned char"
    if maxval < (1 << 16):
        return "unsigned short"
    return "unsigned"


NAMEMAP_TEMPLATE = """\
static const char {uname}_DATA[] =
{ddata};
static const {otype} {uname}_OFFSET[] = {{
{odata}
}};
const char *{lname}(unsigned index) {{
    unsigned offset;
    if ({count} <= index)
        return 0;
    offset = {uname}_OFFSET[index];
    if (offset == 0)
        return 0;
    return {uname}_DATA + offset;
}}
"""


def make_namemap(table, fname):
    """Create a function that maps integers to strings.

    Arguments:
      table: List of (input, output) pairs, where inputs are integers and
        outputs are strings
      fname: The output function name
    Returns:
      A string, contaning C source code which defines a function converting
      integers to strings according to the table.
    """
    kmap = {}
    for code, kname in table:
        kname2 = kmap.get(code)
        if kname2 is not None and kname != kname2:
            raise Error("Name conflict: code {} is {!r} and {!r}".format(
                code, kname, kname2))
        kmap[code] = kname
    data, strmap = make_string_table([kname for (code, kname) in table])
    count = max(code for code, kname in table) + 1
    stridx = [0] * count
    for code, kname in table:
        stridx[code] = strmap[kname]
    return NAMEMAP_TEMPLATE.format(
        lname=fname.lower(),
        uname=fname.upper(),
        ddata=format_data(data, "    "),
        odata=format_numbers(stridx, "    "),
        otype=ctype(max(stridx)),
        count=count,
    )


XTABLE_TEMPLATE = """\
const unsigned char {name}[{size}] = {{
{data}
}};
"""


def make_xtable(table, name):
    """Format a translation table as C source code."""
    return XTABLE_TEMPLATE.format(
        name=name,
        size=len(table),
        data=format_numbers(table, "    "),
    )


def emit_keytable(open_file, keytable):
    """Emit the code files for a keycode table."""
    name = keytable.name.lower()
    common_head = '#include "keytable.h"\n'
    with open_file("{}_rawname.c".format(name)) as fp:
        fp.write(common_head)
        fp.write(
            make_namemap(keytable.scancodes,
                         "keycode_{}_rawname".format(name)))
    with open_file("{}_name.c".format(name)) as fp:
        fp.write(common_head)
        fp.write(
            make_namemap(keytable.displaynames,
                         "keycode_{}_name".format(name)))
    with open_file("{}_tohid.c".format(name)) as fp:
        fp.write(common_head)
        fp.write(
            make_xtable(keytable.to_hid_table,
                        "KEYCODE_{}_TO_HID".format(name.upper())))
    with open_file("{}_fromhid.c".format(name)) as fp:
        fp.write(common_head)
        fp.write(
            make_xtable(keytable.from_hid_table,
                        "KEYCODE_{}_FROM_HID".format(name.upper())))
