import struct
import sys


def zeros(s):
    """
    test whether the given string is all zeros
    """
    return (s == "\0" * len(s))


def printable(ch):
    """
    test whether the given character is printable
    """
    if 0x20 <= ord(ch) < 0x7F:
        return True
    else:
        return False


def dump(bytes, cols=16, unprintable=".", print_all=False):
    """
    write out a hexdump of the given bytes to stdout

    cols - how many bytes to a row to display
    unprintable - what to replace unprintable characters with
    print_all - whether to force unprintable characters into a printable range
    """

    rows, last_row = divmod(len(bytes), cols)

    for row in range(rows + 1):
        for i in range(last_row if row == rows else cols):
            byte = bytes[cols * row + i]
            sys.stdout.write("%02X " % ord(byte))
        if row == rows:
            sys.stdout.write("   " * (cols - last_row))
        for i in range(last_row if row == rows else cols):
            byte = bytes[cols * row + i]
            if print_all:
                sys.stdout.write(chr(0x20 + ((ord(byte) - 0x20) % 0x5F)))
            else:
                if printable(byte):
                    sys.stdout.write(byte)
                else:
                    sys.stdout.write(unprintable)
        sys.stdout.write("\n")


def dword(buf, offset):
    return struct.unpack("<L", buf[offset:offset + 4])[0]
