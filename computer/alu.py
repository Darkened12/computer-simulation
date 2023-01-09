from .base import Bit, BitArray, Demultiplexer


class ArithmeticLogicUnit:
    def __init__(self):
        self._A = BitArray(0)
        self._B = BitArray(0)
        self._output = BitArray(0)
        self._opcode = BitArray(0)
        self.carry = BitArray(0)
        self.negative_bit_flag = Bit(0)

    @property
    def output(self):
        return self._output

    @property
    def zero_bit_flag(self):
        dif = self.A - self.B
        return Bit(1) if dif == BitArray(0) else Bit(0)

    @property
    def A(self):
        return self._A

    @property
    def B(self):
        return self._B

    @A.setter
    def A(self, value: BitArray):
        self.negative_bit_flag = Bit(0)
        self._A = value

    @B.setter
    def B(self, value: BitArray):
        self.negative_bit_flag = Bit(0)
        self._B = value

    @property
    def opcode(self):
        return self._opcode

    @opcode.setter
    def opcode(self, value: BitArray):
        units = [self.ADD, self.SUB, self.NOT,
                 self.INC, self.DEC, self.OR, self.AND, self.XOR]
        demux = Demultiplexer(units)
        demux.selection = value
        selected_action = demux.output
        selected_action()

    def ADD(self):
        self._output = self.A + self.B
        self.carry = self._output.carry

    def SUB(self):
        output = self.A - self.B
        if len(output) > 8:
            self.negative_bit_flag = Bit(1)
            string = BitArray.from_bit_array(output[1:])
            parsed_string = ''.join(reversed(string))
            self._output = BitArray(parsed_string)

            return
        self._output = output

    def INC(self):
        self._output = self.A + BitArray(1)

    def DEC(self):
        self._output = self.A - BitArray(1)

    def AND(self):
        self._output = self.A & self.B

    def OR(self):
        self._output = self.A | self.B

    def NOT(self):
        self._output = ~self.A

    def XOR(self):
        self._output = self.A ^ self.B


if __name__ == '__main__':
    alu = ArithmeticLogicUnit()
    alu.A = BitArray('00000001')
    alu.B = BitArray('00000010')
    alu.opcode = BitArray('0001')
    print(alu.negative_bit_flag)
    print(alu.output)
    alu.A = BitArray('00000001')
    alu.B = BitArray('00000010')
    alu.opcode = BitArray('0000')
    print(alu.negative_bit_flag)
    print(alu.output)
