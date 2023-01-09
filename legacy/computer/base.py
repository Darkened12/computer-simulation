def to_int(list_of_bits: list[int]):
    result = '0b'
    for bit in list_of_bits:
        result += str(bit)
    return int(result, base=2)


class Binary(int):
    def __new__(cls, value, *args, **kwargs):
        return super(Binary, cls).__new__(cls, value)

    def __init__(self, value):
        if self.bit_length() > 1:
            raise OverflowError('Value must be 1 or 0')


def NOT(binary: Binary) -> Binary:
    if binary == 1:
        return Binary(0)
    if binary == 0:
        return Binary(1)


class BinarySet:
    def __init__(self, size: int, array: list or None = None):
        self.size = size
        self._set = array or [Binary(0) for n in range(size)]

        if array:
            if not isinstance(array[0], Binary):
                self._set = [Binary(n) for n in array]

    def __getitem__(self, item):
        return self._set[~item]

    def __setitem__(self, key, value):
        if value > 1:
            raise OverflowError('Value must be 1 or 0')
        if isinstance(value, Binary):
            self._set[~key] = value
        else:
            self._set[~key] = Binary(value)

    def __iter__(self):
        return iter(reversed(self._set))

    def __call__(self, *args, **kwargs):
        return self._set

    def __eq__(self, other):
        return self._set == other

    def __len__(self):
        return len(self._set)

    def __repr__(self):
        return ''.join([str(n) for n in self._set])

    def to_int(self):
        return to_int(self._set)

    def length(self):
        return len(self._set)


class Multiplexer4:
    """Fixed size: 4"""

    def __init__(self, input_: BinarySet):
        self.input = input_
        self.size = len(input_)
        if self.size > 4:
            raise NotImplementedError

        self.selection = BinarySet(size=3)
        self.output = Binary(0)

    def __repr__(self):
        return f"""INPUT: {self.input}
SELECTION: {self.selection}
OUTPUT: {self.output}"""

    def update(self):
        and1 = self.selection[1] & self.selection[0] & self.input[3]
        and2 = self.selection[1] & NOT(self.selection[0]) & self.input[2]
        and3 = NOT(self.selection[1]) & self.selection[0] & self.input[1]
        and4 = NOT(self.selection[1]) & NOT(self.selection[0]) & self.input[0]
        self.output = Binary(and1 | and2 | and3 | and4)


class Multiplexer8:
    """Fixed size: 8"""

    def __init__(self, input_: BinarySet):
        self.input = input_
        self.size = len(input_)
        if self.size > 8:
            raise NotImplementedError

        self.selection = BinarySet(size=int(self.size / 2))
        self.output = Binary(0)

    def __repr__(self):
        return f"""INPUT: {self.input}
SELECTION: {self.selection}
OUTPUT: {self.output}"""

    def update(self):
        and0 = self.selection[0] & self.selection[1] & self.selection[2] & self.input[7]
        and1 = NOT(self.selection[0]) & NOT(self.selection[1]) & self.selection[2] & self.input[6]
        and2 = NOT(self.selection[0]) & NOT(self.selection[1]) & self.selection[2] & self.input[5]
        and3 = NOT(self.selection[0]) & NOT(self.selection[1]) & self.selection[2] & self.input[4]
        and4 = self.selection[0] & self.selection[1] & NOT(self.selection[2]) & self.input[3]
        and5 = NOT(self.selection[0]) & self.selection[1] & NOT(self.selection[2]) & self.input[2]
        and6 = self.selection[0] & NOT(self.selection[1]) & NOT(self.selection[2]) & self.input[1]
        and7 = NOT(self.selection[0]) & NOT(self.selection[1]) & NOT(self.selection[2]) & self.input[0]

        self.output = Binary(and0 | and1 | and2 | and3 | and4 | and5 | and6 | and7)


class Demultiplexer8:
    """Fixed size: 8"""

    def __init__(self, input_: Binary = Binary(1)):
        self.input = input_
        self.size = 8
        self.selection = BinarySet(size=3)
        self.output = BinarySet(size=8)

    def __repr__(self):
        return f"""INPUT: {self.input}
SELECTION: {self.selection}
OUTPUT: {self.output}"""

    def update(self):
        and0 = self.selection[0] & self.selection[1] & self.selection[2] & self.input
        and1 = NOT(self.selection[0]) & self.selection[1] & self.selection[2] & self.input
        and2 = self.selection[0] & NOT(self.selection[1]) & self.selection[2] & self.input
        and3 = NOT(self.selection[0]) & NOT(self.selection[1]) & self.selection[2] & self.input
        and4 = self.selection[0] & self.selection[1] & NOT(self.selection[2]) & self.input
        and5 = NOT(self.selection[0]) & self.selection[1] & NOT(self.selection[2]) & self.input
        and6 = self.selection[0] & NOT(self.selection[1]) & NOT(self.selection[2]) & self.input
        and7 = NOT(self.selection[0]) & NOT(self.selection[1]) & NOT(self.selection[2]) & self.input

        self.output = BinarySet(array=[and0, and1, and2, and3, and4, and5, and6, and7], size=8)


def _debug_mux_4():
    mux = Multiplexer4(BinarySet(array=[0, 1, 0, 0], size=4))
    mux.selection[0] = 0
    mux.selection[1] = 1
    mux.update()
    print(mux)


def _debug_mux_8():
    mux = Multiplexer8(BinarySet(array=[0, 1, 0, 1, 0, 1, 0, 1], size=8))
    mux.selection[0] = 0
    mux.selection[1] = 1
    mux.selection[2] = 1
    mux.update()
    print(mux)


def _debug_demux_8():
    demux = Demultiplexer8()
    demux.selection[0] = 0
    demux.selection[1] = 0
    demux.selection[2] = 0
    demux.update()
    print(demux)


if __name__ == '__main__':
    _debug_demux_8()
