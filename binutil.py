#! /usr/bin/env python3

GROUP_BY = 8


def signed(binary):
    """convert signed binary to decimal
    """
    binary = ''.join(binary.split())
    if binary[0] == '1':
        return -(int(flip(binary), 2) + 1)
    return int(binary, 2)


def flip(binary):
    flip_map = {ord('0'): '1', ord('1'): '0'}
    return binary.translate(flip_map)


def pad_space(binary):
    """pad with space every <GROUP_BY> bits
    """
    bin_rev = ''.join(reversed(binary))
    padded = ' '.join(bin_rev[i: i + GROUP_BY]
                      for i in range(0, len(bin_rev), GROUP_BY))
    return ''.join(reversed(padded))


def min_bin(x):
    """minimal representation of x in binary
    use 2's complement
    """
    if x >= 0:
        return '0' + bin(x)[2:]
    else:
        bits = x.bit_length()
        return '1' + bin(2 ** bits - x)[2:].rjust(bits, '0')


def bin2(x, bits=32):
    """display signed integer right aligned in binary
    use 2's complement
    """
    # minimal representation with 2's complement
    output = min_bin(x)

    if len(output) > bits:
        return pad_space(output[len(output) - bits:])
    return pad_space(output.rjust(bits, output[0]))


class BinRepr(int):

    def __new__(cls, x, bits=32):
        if isinstance(x, str):
            x = signed(x)
        return super(BinRepr, cls).__new__(cls, x)

    def __init__(self, x, bits=32):
        self.bits = bits

    def __int__(self):
        return signed(str(self))

    def __str__(self, bits=None):
        return bin2(self, self.bits if bits is None else bits)

    def __repr__(self):
        return str(int(self))
