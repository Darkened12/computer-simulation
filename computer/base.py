from math import pow
from typing import Union, Tuple


class Bit(int):
    def __new__(cls, value, *args, **kwargs):
        return super(Bit, cls).__new__(cls, value)

    def __init__(self, value):
        if self.bit_length() > 1:
            raise OverflowError(f'Value must be 1 or 0. Tried value: "{value}"')

    def __invert__(self):
        return Bit(0) if self == 1 else Bit(1)


class BitArray:
    def __init__(self, content: Union[str, int], size: int = 8):
        self.size = size
        if isinstance(content, int):
            self._str_repr = self.from_integer(content, self.size)
        else:
            self._str_repr = self.from_integer(self.from_bit_string(content), self.size)
        self._str_repr = self._str_repr.replace('-', '10')
        self._array = [Bit(bit) for bit in reversed(self._str_repr)]

    @staticmethod
    def from_integer(number: int, size: int) -> str:
        bit_length = f'0{size}b'
        return f'{number:{bit_length}}'

    @staticmethod
    def from_bit_string(string: str) -> int:
        return int(string, 2)

    @classmethod
    def from_bit_array(cls, array: list[Bit]) -> str:
        string = ''.join([str(bit) for bit in reversed(array)])
        return cls.from_integer(cls.from_bit_string(string), len(array))

    @property
    def carry(self):
        return len(self._str_repr) - self.size

    def divide(self, bit_size: int) -> Tuple:
        upper_half = self._array[:bit_size]
        lower_half = self._array[bit_size:]
        upper_half = BitArray.from_bit_array(upper_half)
        lower_half = BitArray.from_bit_array(lower_half)
        return BitArray(upper_half, size=bit_size), BitArray(lower_half, size=bit_size)

    def to_int(self):
        return int(self._str_repr, 2)

    def __repr__(self):
        return self._str_repr

    def __len__(self):
        return len(self._array)

    def __getitem__(self, item):
        return self._array[item]

    def __setitem__(self, key, value):
        self._array[key] = Bit(value)
        self._str_repr = self.from_bit_array(self._array)

    def __add__(self, other):
        return BitArray(self.from_integer(self.to_int() + other.to_int(), self.size), size=self.size)

    def __sub__(self, other):
        return BitArray(self.from_integer(self.to_int() - other.to_int(), self.size), size=self.size)

    def __and__(self, other):
        return BitArray(self.from_integer(self.to_int() & other.to_int(), self.size), size=self.size)

    def __or__(self, other):
        return BitArray(self.from_integer(self.to_int() | other.to_int(), self.size), size=self.size)

    def __xor__(self, other):
        return BitArray(self.from_integer(self.to_int() ^ other.to_int(), self.size), size=self.size)

    def __invert__(self):
        return BitArray(self.from_integer(self.to_int() ^ int(pow(2, self.size) - 1), self.size), size=self.size)

    def __bool__(self):
        return bool(self.to_int())

    def __eq__(self, other):
        return self.to_int() == other.to_int()


class Demultiplexer:
    def __init__(self, input_: list):
        self._selection = BitArray(0)
        self._input = input_

    @property
    def selection(self):
        return self._selection

    @property
    def output(self):
        return self._input[self.selection.to_int()]

    @output.setter
    def output(self, value: BitArray):
        self._input[self.selection.to_int()] = value

    @selection.setter
    def selection(self, value: BitArray):
        self._selection = value


if __name__ == '__main__':
    # demux = Demultiplexer([BitArray(1), BitArray(1), BitArray(1)])
    # demux.selection = BitArray(0, size=2)
    # print(demux.output)
    # demux.output = BitArray(0)
    # print(demux.output)
    # print(demux._input)

    print(BitArray('01000001').divide(4))
