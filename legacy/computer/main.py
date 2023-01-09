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


class BinarySet:
    def __init__(self, size: int, array: list or None = None):
        self.size = size
        self._set = array or [Binary(0) for n in range(size)]

        if array:
            for bit in self._set:
                if bit > 1:
                    raise OverflowError('Value must be 1 or 0')

    def __getitem__(self, item):
        return self[~item]

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

    def __repr__(self):
        return ''.join([str(n) for n in self._set])

    def __eq__(self, other):
        return self._set == other

    def to_int(self):
        return to_int(self._set)

    def length(self):
        return len(self._set)


class ArithmeticLogicUnit:
    """
    Addition: 000
    Subtraction: 001
    Increment: 010
    Decrement: 011
    NOT : 100
    AND: 101
    OR: 110
    XOR: 111

    """

    def __init__(self, bit_size: int):
        self.A = BinarySet(bit_size)
        self.B = BinarySet(bit_size)
        self.output = BinarySet(bit_size)
        self.carry = Binary(0)
        self.overflow = Binary(0)

        self.operation_code = BinarySet(size=3)
        self.size = bit_size

    def __repr__(self):
        op_codes = self._operation_code_dict()
        op_code = next(filter(lambda code: self.operation_code == op_codes[code], op_codes))
        return f"""
OP: {op_code}
A: {self.A} = int {self.A.to_int()}
B: {self.B} = int {self.B.to_int()}
Y: {self.output} = int {self.output.to_int()}
C: int {self.carry}"""

    def __call__(self, *args, **kwargs):
        if self.operation_code == [0, 0, 0]:  # Addition
            self._adder()
        elif self.operation_code == [0, 0, 1]:  # Subtraction
            self._adder(subtraction=1)
        elif self.operation_code == [0, 1, 0]:  # Increment
            self._increment()
        elif self.operation_code == [0, 1, 1]:  # Decrement
            self._increment(subtraction=1)
        elif self.operation_code == [1, 0, 0]:  # NOT
            return self._not()
        elif self.operation_code == [1, 0, 1]:  # AND
            return self._and()
        elif self.operation_code == [1, 1, 0]:  # OR
            return self._or()
        elif self.operation_code == [1, 1, 1]:  # XOR
            return self._xor()
        return self

    def _operation_code_dict(self):
        return {
            'ADD': BinarySet(array=[0, 0, 0], size=3),
            'SUB': BinarySet(array=[0, 0, 1], size=3),
            'INC': BinarySet(array=[0, 1, 0], size=3),
            'DEC': BinarySet(array=[0, 1, 1], size=3),
            'NOT': BinarySet(array=[1, 0, 0], size=3),
            'AND': BinarySet(array=[1, 0, 1], size=3),
            'OR': BinarySet(array=[1, 1, 0], size=3),
            'XOR': BinarySet(array=[1, 1, 1], size=3),
        }

    def _adder(self, subtraction=0):
        self.carry = Binary(0)
        for index, a, b in zip(range(self.output.length()), self.A, self.B):
            if subtraction:
                b = b ^ self.carry
                # b = not b
                # if b and not self.carry:
                #     b = Binary(0)
                #     self.carry = Binary(1)
                # elif not b and not self.carry:
                #     b = Binary(1)
                # elif b and self.carry:
                #     b = Binary(0)

            if self.carry:
                if a and b:
                    self.output[index] = Binary(1)
                    self.carry = Binary(1)
                elif a or b:
                    self.output[index] = Binary(0)
                    self.carry = Binary(1)
                else:
                    self.output[index] = Binary(1)
                    self.carry = Binary(0)
            else:
                if a and b:
                    self.output[index] = Binary(0)
                    self.carry = Binary(1)
                elif a or b:
                    self.output[index] = Binary(1)
                    self.carry = Binary(0)
                else:
                    self.output[index] = Binary(0)
                    self.carry = Binary(0)

    def _increment(self, subtraction=0):
        self.carry = Binary(0)
        old_data = self.B._set.copy()
        new_data = [Binary(0) for n in range(self.size)]
        new_data[-1] = Binary(1)

        self.B._set = new_data
        self._adder(subtraction)
        self.B._set = old_data

    def _not(self):
        self.carry = Binary(0)
        result = [Binary(0) if byte else Binary(1) for byte in self.A]
        self.output = BinarySet(array=result, size=self.size)

    def _and(self):
        self.carry = Binary(0)
        for index, a, b in zip(range(self.output.length()), self.A, self.B):
            if a and b:
                self.output[index] = Binary(1)
            else:
                self.output[index] = Binary(0)

    def _or(self):
        self.carry = Binary(0)
        for index, a, b in zip(range(self.output.length()), self.A, self.B):
            if a or b:
                self.output[index] = Binary(1)
            else:
                self.output[index] = Binary(0)

    def _xor(self):
        self.carry = Binary(0)
        for index, a, b in zip(range(self.output.length()), self.A, self.B):
            if a ^ b:
                self.output[index] = Binary(1)
            else:
                self.output[index] = Binary(0)


class RandomAccessMemory:
    def __init__(self, size: int):
        self.size = size
        self._data = [BinarySet(size=8) for n in range(int(size / 8))]
        self.address = BinarySet(size=4)
        self.write = Binary(0)
        self.read = Binary(0)


class FullAdderSet:
    def __init__(self, a: BinarySet, b: BinarySet):
        self.A = a
        self.B = b
        self.output = BinarySet(size=self.A.size)
        self.carry = Binary(0)

    @staticmethod
    def add(a: Binary, b: Binary, c: Binary) -> tuple[Binary, Binary]:
        xor1 = a ^ b
        xor2 = xor1 ^ c

        and1 = xor1 & c
        and2 = a & b

        carry = and1 | and2
        sum_ = xor2

        return sum_, carry

    def execute(self, subtraction: Binary = 0):
        self.carry = Binary(subtraction)
        for index, a, b in zip(range(self.output.length()), self.A, self.B):
            sum_, carry = self.add(a, b ^ self.carry, self.carry)
            self.output[index] = Binary(sum_)
            self.carry = Binary(carry)


def adder_debug():
    A = BinarySet(size=4)
    B = BinarySet(size=4)

    A[0] = 1
    A[1] = 1
    A[2] = 0
    A[3] = 0

    B[0] = 1
    B[1] = 0
    B[2] = 0
    B[3] = 0

    full_adder = FullAdderSet(A, B)
    full_adder.execute(subtraction=Binary(1))

    print(full_adder.output)


def ALU_debug():
    ALU = ArithmeticLogicUnit(bit_size=4)
    ALU.A[0] = Binary(0)
    ALU.A[1] = Binary(0)
    ALU.A[2] = Binary(1)
    ALU.A[3] = Binary(0)

    ALU.B[0] = Binary(1)
    ALU.B[1] = Binary(1)
    ALU.B[2] = Binary(0)
    ALU.B[3] = Binary(0)

    ALU.operation_code = BinarySet(array=[Binary(0), Binary(0), Binary(1)], size=3)
    ALU()
    print(ALU)


def RAM_debug():
    RAM = RandomAccessMemory(size=128)
    RAM._data[0][0] = Binary(1)
    for byte in RAM._data:
        print(byte)
    print(RAM._data)


if __name__ == '__main__':
    adder_debug()
