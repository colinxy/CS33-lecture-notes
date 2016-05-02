#! /usr/bin/env python3

"""
Python C signed integer/float library
mimic behavior of C int/float
"""

# for compatibility with python2
from __future__ import division
import sys
import struct
try:
    from string import maketrans  # python 2
except ImportError:
    maketrans = str.maketrans     # python 3

INVERT_TABLE = maketrans('01', '10')

ENDIANNESS = sys.byteorder
if ENDIANNESS != 'little' and ENDIANNESS != 'big':
    raise OSError("unsupported endianness")
BYTE_REVERSED = ENDIANNESS == 'little'

GROUP_BY = 8


def signed(binary):
    """convert 2's complement binary to decimal
    """
    binary = ''.join(binary.split())
    if binary[0] == '1':
        return -(int(invert(binary), 2) + 1)
    return int(binary, 2)


def invert(binary):
    return binary.translate(INVERT_TABLE)


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


def int2bin(x, bits=32):
    """display signed integer right aligned in binary
    use 2's complement
    """
    # minimal representation with 2's complement
    output = min_bin(x)

    if len(output) > bits:
        return pad_space(output[len(output) - bits:])
    return pad_space(output.rjust(bits, output[0]))


def byte2bin(byte_arr):
    # indexing bytes in python2 produce a one-item slice of bytes, while
    # indexing bytes in python3 produce an int
    # convert bytes to bytearray to resolve this issue
    return ' '.join(bin(b)[2:].rjust(8, '0')  # 0 extend byte
                    for b in bytearray(byte_arr))


def byte2bin_float(byte_arr):
    binary = ''.join(bin(b)[2:].rjust(8, '0')  # 0 extend byte
                     for b in bytearray(byte_arr))
    if len(byte_arr) == 4:
        # float
        # 1 sign, 8 exp, 23 frac
        binary = binary[:1] + ' ' + binary[1:9] + ' ' + binary[9:]
    elif len(byte_arr) == 8:
        # double
        # 1 sign, 11 exp, 52 frac
        binary = binary[:1] + ' ' + binary[1:12] + ' ' + binary[12:]
    return binary


class Int(int):
    """Mimic behavior of C signed int.

    For this class, an integer can be chosen to be
    reprsented in an arbitrary number of bits.
    """

    def __new__(cls, x, bits=32):
        """Int(x: int, bits: int = 32) -> Int
        """
        if bits <= 0 or not isinstance(bits, int):
            raise ArithmeticError(
                "{} cannot be used as the number of bits for Int".
                format(bits))
        if not isinstance(x, int):
            raise ArithmeticError(
                "{} cannot be interpreted as an integer".
                format(x))

        # make sure is negative when 2**(bits-1) < x < 2**bits
        x = signed(int2bin(x, bits))
        return super(Int, cls).__new__(cls, x)

    def __init__(self, x, bits=32):
        self.bits = bits

    def __str__(self):
        return int2bin(self, self.bits)

    __repr__ = __str__

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

    # negate
    def __neg__(self):
        return 0 - self

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
    """Mimic behavior of C float.

    For this class, only float (4 bytes) and
    double (8 bytes) are accepted.
    """

    def __new__(cls, x, double=False):
        """Float(x: float, double: bool = False) -> Float
        """
        if not isinstance(x, (float, int)):
            raise ArithmeticError(
                "{} cannot be interpreted as a float".
                format(x))

        return super(Float, cls).__new__(cls, x)

    def __init__(self, x, double=False):
        if double:
            self._struct_fmt = 'd'
        else:
            self._struct_fmt = 'f'

    def __str__(self):
        byte_rep = struct.pack(self._struct_fmt, self)
        if BYTE_REVERSED:
            byte_rep = byte_rep[::-1]

        return byte2bin_float(byte_rep)

    __repr__ = __str__

    @classmethod
    def POS0(cls, double=False):
        return cls(0.0, double)

    @classmethod
    def NEG0(cls, double=False):
        return cls(-0.0, double)

    @classmethod
    def POS_INF(cls, double=False):
        return cls(float('inf'), double)

    @classmethod
    def NEG_INF(cls, double=False):
        return cls(float('-inf'), double)
