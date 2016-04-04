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
        x = -x
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


class Int(int):
    """Mimic behavior of C signed int
    """

    def __new__(cls, x, bits=32):
        """x: int"""
        if isinstance(x, str):
            x = signed(x)
        # make sure is negative when 2**(bits-1) < x < 2**bits
        x = signed(bin2(x, bits))
        return super(Int, cls).__new__(cls, x)

    def __init__(self, x, bits=32):
        self.bits = bits

    # def __int__(self):
    #     # default method might not handle negative numbers correctly
    #     return signed(str(self))

    def __str__(self):
        return bin2(self, self.bits)

    def __repr__(self):
        return str(self)

    # always promote to higher precision
    def _bits(self, value):
        return max(self.bits, value.bits)

    # +
    def __add__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = self._bits(value)
        return self.__class__(int.__add__(self, value), bits)

    # -
    def __sub__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = self._bits(value)
        return self.__class__(int.__sub__(self, value), bits)

    # *
    def __mul__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = self._bits(value)
        return self.__class__(int.__mul__(self, value), bits)

    # /
    def __floordiv__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = self._bits(value)
        return self.__class__(int.__floordiv__(self, value), bits)

    __truediv__ = __floordiv__

    # bit level
    # &
    def __and__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = self._bits(value)
        return self.__class__(int.__and__(self, value), bits)

    # |
    def __or__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = self._bits(value)
        return self.__class__(int.__or__(self, value), bits)

    # ~
    def __invert__(self):
        return self.__class__(int.__invert__(self), self.bits)

    # ^
    def __xor__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = self._bits(value)
        return self.__class__(int.__xor__(self, value), bits)

    # <<
    def __lshift__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = self._bits(value)
        return self.__class__(int.__lshift__(self, value), bits)

    # >>
    def __rshift__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = self._bits(value)
        return self.__class__(int.__rshift__(self, value), bits)


class Float:
    pass
