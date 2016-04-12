#! /usr/bin/env python3

"""
Python C signed integer/float library
mimic behavior of C int/float
"""

# for compatibility with python2
from __future__ import division
try:
    from string import maketrans  # python 2
except ImportError:
    maketrans = str.maketrans     # python 3


GROUP_BY = 8


def signed(binary):
    """convert signed binary to decimal
    """
    binary = ''.join(binary.split())
    if binary[0] == '1':
        return -(int(invert(binary), 2) + 1)
    return int(binary, 2)


def invert(binary):
    invert_table = maketrans('01', '10')
    return binary.translate(invert_table)


def pad_space(binary):
    """pad with space every <GROUP_BY> bits
    """
    bin_rev = binary[::-1]
    padded = ' '.join(bin_rev[i: i + GROUP_BY]
                      for i in range(0, len(bin_rev), GROUP_BY))
    return padded[::-1]


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
        """Int(x: int, bits: int = 32) -> Int
        """
        if bits <= 0:
            raise ArithmeticError("invalid number of bits for Int: {}".
                                  format(bits))

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

    # +
    def __add__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = max(self.bits, value.bits)
        return self.__class__(int.__add__(self, value), bits)

    def __radd__(self, value):
        value = self.__class__(value, self.bits)
        return self.__class__.__add__(value, self)

    # -
    def __sub__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = max(self.bits, value.bits)
        return self.__class__(int.__sub__(self, value), bits)

    def __rsub__(self, value):
        value = self.__class__(value, self.bits)
        return self.__class__.__sub__(value, self)

    # *
    def __mul__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = max(self.bits, value.bits)
        return self.__class__(int.__mul__(self, value), bits)

    def __rmul__(self, value):
        value = self.__class__(value, self.bits)
        return self.__class__.__mul__(value, self)

    # /
    def __floordiv__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = max(self.bits, value.bits)
        # default behavior for python is round towards -Infinity
        # while in C is round towards 0
        # round towards 0
        if (self < 0) ^ (value < 0):
            # self + (-self % value)
            adjusted = int.__add__(self, int.__neg__(self) % value)
            return self.__class__(int.__floordiv__(adjusted, value), bits)
        else:
            return self.__class__(int.__floordiv__(self, value), bits)

    __truediv__ = __floordiv__

    def __rfloordiv__(self, value):
        value = self.__class__(value, self.bits)
        return self.__class__.__floordiv__(value, self)

    __rtruediv__ = __rfloordiv__

    # bit level
    # &
    def __and__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = max(self.bits, value.bits)
        return self.__class__(int.__and__(self, value), bits)

    def __rand__(self, value):
        value = self.__class__(value, self.bits)
        return self.__class__.__and__(value, self)

    # |
    def __or__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = max(self.bits, value.bits)
        return self.__class__(int.__or__(self, value), bits)

    def __ror__(self, value):
        value = self.__class__(value, self.bits)
        return self.__class__.__or__(value, self)

    # ~
    def __invert__(self):
        return self.__class__(int.__invert__(self), self.bits)

    # ^
    def __xor__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = max(self.bits, value.bits)
        return self.__class__(int.__xor__(self, value), bits)

    def __rxor__(self, value):
        value = self.__class__(value, self.bits)
        return self.__class__.__xor__(value, self)

    # <<
    def __lshift__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = max(self.bits, value.bits)
        return self.__class__(int.__lshift__(self, value), bits)

    def __rlshift__(self, value):
        value = self.__class__(value, self.bits)
        return self.__class__.__lshift__(value, self)

    # >>
    def __rshift__(self, value):
        if not isinstance(value, self.__class__):
            value = self.__class__(value, self.bits)
        bits = max(self.bits, value.bits)
        return self.__class__(int.__rshift__(self, value), bits)

    def __rrshift__(self, value):
        value = self.__class__(value, self.bits)
        return self.__class__.__rshift__(value, self)

    @classmethod
    def TMAX(cls, bits=32):
        return cls((1 << (bits - 1)) - 1, bits)

    @classmethod
    def TMIN(cls, bits=32):
        return cls(-(1 << (bits - 1)), bits)


class Float(float):
    pass
