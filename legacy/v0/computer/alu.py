from base import Binary, BinarySet, NOT as not_, Demultiplexer8


class Unit:
    def __init__(self, a: BinarySet, b: BinarySet):
        self.A = a
        self.B = b
        self.size = self.A.size
        self.output = BinarySet(size=self.size)
        self.output_enable = Binary(0)


class FullAdderSet(Unit):
    def __init__(self, a: BinarySet, b: BinarySet):
        super().__init__(a, b)
        self.carry = Binary(0)
        self._xor = Binary(0)

    @staticmethod
    def add(a: Binary, b: Binary, c: Binary) -> tuple[Binary, Binary]:
        xor1 = a ^ b
        xor2 = xor1 ^ c

        and1 = xor1 & c
        and2 = a & b

        carry = and1 | and2
        sum_ = xor2

        return sum_, carry

    @property
    def xor(self):
        return self._xor

    @xor.setter
    def xor(self, b: Binary):
        self._xor = b ^ self.carry

    def update(self):
        old_carry = Binary(self.carry)
        for index, a, b in zip(range(self.A.length()), self.A, self.B):
            self.xor = b
            sum_, carry = self.add(a, self.xor, old_carry)
            self.output[index] = Binary(sum_) & self.output_enable
            old_carry = Binary(carry)


class Increment(Unit):
    def update(self):
        b = BinarySet(size=self.size)
        b[0] = Binary(1)
        adder = FullAdderSet(self.A, b)
        adder.output_enable = self.output_enable
        adder.update()
        self.output = adder.output


class Decrement(Unit):
    def update(self):
        b = BinarySet(size=self.size)
        b[0] = Binary(1)
        adder = FullAdderSet(self.A, b)
        adder.carry = Binary(1)
        adder.output_enable = self.output_enable
        adder.update()
        self.output = adder.output


class NOT(Unit):
    def update(self):
        for index, a in enumerate(self.A):
            self.output[index] = not_(a) & self.output_enable


class AND(Unit):
    def update(self):
        for index, a, b in zip(range(self.A.length()), self.A, self.B):
            self.output[index] = a & b & self.output_enable


class OR(Unit):
    def update(self):
        for index, a, b in zip(range(self.A.length()), self.A, self.B):
            self.output[index] = (a | b) & self.output_enable


class XOR(Unit):
    def update(self):
        for index, a, b in zip(range(self.A.length()), self.A, self.B):
            self.output[index] = (a ^ b) & self.output_enable


class ArithmeticLogicUnit:
    def __init__(self, size):
        self.size = size
        self._A = BinarySet(size)
        self._B = BinarySet(size)
        self._output = BinarySet(size)
        self._opcode = BinarySet(int(size / 2))
        self.adder = FullAdderSet(self._A, self._B)
        self.subtraction = FullAdderSet(self._A, self._B)
        self.subtraction.carry = Binary(1)
        self.increment = Increment(self._A, self._B)
        self.decrement = Decrement(self._A, self._B)
        self.NOT = NOT(self._A, self._B)
        self.AND = AND(self._A, self._B)
        self.OR = OR(self._A, self._B)
        self.XOR = XOR(self._A, self._B)
        self.demux = Demultiplexer8()
        self.unit_list = [self.adder, self.increment, self.decrement, self.NOT, self.AND,
                          self.OR, self.XOR]

    @property
    def A(self):
        return self._A

    @A.setter
    def A(self, value: BinarySet):
        self._A = value
        for unit in self.unit_list:
            unit.A = self._A

    @property
    def B(self):
        return self._B

    @B.setter
    def B(self, value: BinarySet):
        self._B = value
        for unit in self.unit_list:
            unit.B = self._B

    @property
    def opcode(self):
        return self._opcode

    @opcode.setter
    def opcode(self, value: BinarySet):
        self._opcode = value

        self.demux.selection = self._opcode
        self.demux.update()

        for bit, unit in zip(self.demux.output, self.unit_list):
            unit.output_enable = bit

    @property
    def output(self):
        for unit in self.unit_list:
            if unit.output_enable:
                return unit.output
        return BinarySet(self.size)

    def update(self):
        for unit in self.unit_list:
            unit.update()


def _debug_adder():
    A = BinarySet(array=[0, 0, 1, 1], size=4)
    B = BinarySet(array=[0, 0, 0, 1], size=4)
    adder = FullAdderSet(A, B)
    adder.carry = Binary(1)
    adder.output_enable = Binary(1)
    adder.update()
    print(adder.output)


def _debug_increment():
    inc = Increment(BinarySet(size=4), BinarySet(size=4))
    inc.A[0] = Binary(1)
    inc.output_enable = Binary(1)
    inc.update()
    print(inc.output)


def _debug_decrement():
    dec = Decrement(BinarySet(size=4), BinarySet(size=4))
    dec.A[0] = Binary(1)
    dec.output_enable = Binary(1)
    dec.update()
    print(dec.output)


def _debug_not():
    n = NOT(BinarySet(array=[1, 0, 1, 1], size=4), BinarySet(4))
    n.output_enable = Binary(1)
    n.update()
    print(n.output)


def _debug_and():
    a = AND(BinarySet(array=[1, 0, 1, 1], size=4), BinarySet(array=[1, 1, 1, 1], size=4))
    a.output_enable = Binary(1)
    a.update()
    print(a.output)


def _debug_or():
    o = OR(BinarySet(array=[1, 0, 1, 1], size=4), BinarySet(array=[1, 1, 1, 1], size=4))
    o.output_enable = Binary(1)
    o.update()
    print(o.output)


def _debug_xor():
    x = XOR(BinarySet(array=[0, 0, 0, 1], size=4), BinarySet(array=[0, 1, 0, 1], size=4))
    x.output_enable = Binary(1)
    x.update()
    print(x.output)


def _debug_alu():
    ALU = ArithmeticLogicUnit(8)
    ALU.A = BinarySet(array=[0, 0, 0, 0, 0, 0, 0, 1], size=8)
    ALU.B = BinarySet(array=[0, 0, 0, 0, 0, 0, 1, 1], size=8)
    ALU.opcode = BinarySet(array=[0, 1, 1], size=3)
    ALU.update()

    print(ALU.output)


if __name__ == '__main__':
    _debug_alu()
