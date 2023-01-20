from math import log, ceil

from .base import Bit, BitArray, Demultiplexer


class Register:
    def __init__(self, size_in_bits: int):
        self._memory = BitArray(0, size=size_in_bits)
        self._read_enable = Bit(0)
        self._write_enable = Bit(0)

    def __repr__(self):
        return f'{self._memory} ({self._memory.to_int()})'

    @property
    def memory(self):
        if self._read_enable:
            return self._memory
        return BitArray(0)

    @memory.setter
    def memory(self, value: BitArray):
        if self._write_enable:
            self._memory = value

    @property
    def read_enable(self):
        return self._read_enable

    @read_enable.setter
    def read_enable(self, value: Bit):
        if value > 1:
            raise OverflowError('Value must be 0 or 1')

        self._read_enable = value

    @property
    def write_enable(self):
        return self._write_enable

    @write_enable.setter
    def write_enable(self, value: Bit):
        if value > 1:
            raise OverflowError('Value must be 0 or 1')

        self._write_enable = value


class RandomAccessMemory:
    def __init__(self, size_in_bytes: int):
        self.memory_size = size_in_bytes
        self.address_size = ceil(log(self.memory_size, 2))
        self._address = BitArray(0, size=self.address_size)
        self._memory = [BitArray(0) for n in range(self.memory_size)]
        self._read_enable = Bit(0)
        self._write_enable = Bit(0)
        self._bus = BitArray(0)
        self.demux = Demultiplexer(self._memory)

    def __repr__(self):
        return '\n'.join(f'{index:03}: {str(byte)}' for index, byte in enumerate(self._memory))

    def from_list(self, list_: list[str]):
        if len(list_) == self.memory_size:
            for index, byte in enumerate(list_):
                if len(byte) != 8:
                    raise TypeError(f'Byte in position "{index}" is not 8 bit long')
            self._memory = [BitArray(line) for line in list_]
            self.demux = Demultiplexer(self._memory)
            return
        raise OverflowError(
            f'Provided list of length "{len(list_)}" does not fit. Current mem_size: "{self.memory_size}" bytes')

    @property
    def read_enable(self):
        return self._read_enable

    @property
    def write_enable(self):
        return self._write_enable

    @property
    def address(self):
        return self._address

    @property
    def bus(self):
        if self.read_enable:
            self.demux.selection = self.address
            return self.demux.output
        return BitArray(0)

    @property
    def memory(self):
        return self._memory

    @read_enable.setter
    def read_enable(self, value: Bit):
        self._read_enable = value

    @write_enable.setter
    def write_enable(self, value: Bit):
        self._write_enable = value

    @address.setter
    def address(self, value: BitArray):
        self._address = value

    @bus.setter
    def bus(self, value: BitArray):
        if self.write_enable:
            self.demux.selection = self.address
            self.demux.output = value

    @memory.setter
    def memory(self, value: list[BitArray]):
        self._memory = value
        self.demux._input = self._memory


if __name__ == '__main__':
    ram = RandomAccessMemory(size_in_bytes=8)

    print(ram.address)
    print(ram.memory)
    print(ram.bus)

    ram.address = BitArray('111', size=3)
    ram.write_enable = Bit(1)
    ram.bus = BitArray(1)
    ram.write_enable = Bit(0)
    ram.read_enable = Bit(1)

    print(ram.address)
    print(ram.memory)
    print(ram.bus)

    ram.bus = BitArray(0)
    print(ram)
