import time

from .alu import ArithmeticLogicUnit
from .base import Bit, BitArray, Demultiplexer
from .memory import Register, RandomAccessMemory


class CentralProcessingUnit:
    def __init__(self, alu: ArithmeticLogicUnit, ram: RandomAccessMemory, clock_speed_limiter_in_hertz: int = 0):
        self.clock_speed_limiter_in_hertz = clock_speed_limiter_in_hertz
        self.alu = alu
        self.ram = ram

        self.register_A = Register()
        self.register_B = Register()
        self.instruction_address_register = Register()
        self.instruction_register = Register()
        self.instructions = [self.HLT, self.LDA, self.LDB, self.STA, self.STB, self.ADD, self.SUB, self.JIE, self.JNE]
        self.instruction_selector = Demultiplexer(self.instructions)
        self.register_selector = Demultiplexer([self.register_A, self.register_B])

        self._current_instruction = BitArray(0, size=4)
        self._current_address = BitArray(0, size=4)
        self._halt = Bit(0)
        self._not_skip_increment = Bit(1)
        self._cycle_counter = 0

    @property
    def halt(self):
        return self._halt

    @property
    def cycle_counter(self):
        return self._cycle_counter

    def increment_program_counter(self):
        false = Bit(0)
        true = Bit(1)
        self.instruction_address_register.read_enable = true
        self.alu.A = self.instruction_address_register.memory
        self.instruction_address_register.read_enable = false
        self.alu.opcode = BitArray('0011', size=4)
        self.instruction_address_register.write_enable = self._not_skip_increment
        self.instruction_address_register.memory = self.alu.output
        self._not_skip_increment = true
        self.flush()

    def fetch_phase(self):
        true = Bit(1)
        self.instruction_address_register.read_enable = true
        self.instruction_register.write_enable = true
        self.ram.read_enable = true
        self.ram.address = self.instruction_address_register.memory
        self.instruction_register.memory = self.ram.bus
        self.flush()

    def decode_phase(self):
        self.instruction_register.read_enable = Bit(1)
        self._current_instruction = BitArray(BitArray.from_bit_array(self.instruction_register.memory[4:]), size=4)
        self._current_address = BitArray(BitArray.from_bit_array(self.instruction_register.memory[:4]), size=4)

    def execute_phase(self):
        self.instruction_selector.selection = self._current_instruction
        self.instruction_selector.output(self._current_address)
        self.flush()

    def end_phase(self):
        self.increment_program_counter()

    def flush(self):
        false = Bit(0)
        for unit in [self.register_A, self.register_B,
                     self.instruction_register, self.instruction_address_register,
                     self.ram]:
            unit.read_enable = false
            unit.write_enable = false

    def cycle(self):
        def execute_cycle():
            self.fetch_phase()
            self.decode_phase()
            self.execute_phase()
            self.end_phase()

        if self.clock_speed_limiter_in_hertz > 0:
            start_time = time.perf_counter()
            execute_cycle()
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            time.sleep(1 / self.clock_speed_limiter_in_hertz - elapsed_time)
        else:
            execute_cycle()

        self._cycle_counter += 1

    def LDA(self, address: BitArray):
        """Load contents of RAM {address} into the Register A"""
        self.ram.address = address
        self.ram.read_enable = Bit(1)
        self.register_A.write_enable = Bit(1)
        self.register_A.memory = self.ram.bus

    def LDB(self, address: BitArray):
        """Load contents of RAM {address} into the Register B"""
        self.ram.address = address
        self.ram.read_enable = Bit(1)
        self.register_B.write_enable = Bit(1)
        self.register_B.memory = self.ram.bus

    def STA(self, address: BitArray):
        """Stores contents on RAM {address} from Register A"""
        self.ram.address = address
        self.ram.write_enable = Bit(1)
        self.register_A.read_enable = Bit(1)
        self.ram.bus = self.register_A.memory

    def STB(self, address: BitArray):
        """Stores contents on RAM {address} from Register B"""
        self.ram.address = address
        self.ram.write_enable = Bit(1)
        self.register_B.read_enable = Bit(1)
        self.ram.bus = self.register_B.memory

    def HLT(self, *args, **kwargs):
        self._halt = Bit(1)

    def _add_sub(self, opcode: str, registers: BitArray):
        true = Bit(1)
        false = Bit(0)
        reg1_address = BitArray(sum(registers[2:]))
        reg2_address = BitArray(sum(registers[:2]))
        self.register_selector.selection = reg1_address
        reg1 = self.register_selector.output
        self.register_selector.selection = reg2_address
        reg2 = self.register_selector.output
        reg1.read_enable = true
        reg2.read_enable = true
        self.alu.A = reg1.memory
        self.alu.B = reg2.memory
        self.alu.opcode = BitArray(opcode, size=4)
        reg2.read_enable = false
        reg2.write_enable = true
        reg2.memory = self.alu.output

    def ADD(self, registers: BitArray):
        self._add_sub('0000', registers)

    def SUB(self, registers: BitArray):
        self._add_sub('0001', registers)

    def JIE(self, address: BitArray):
        true = Bit(1)
        self.register_selector.selection = BitArray('00', size=2)
        reg0 = self.register_selector.output
        self.register_selector.selection = BitArray('01', size=2)
        reg1 = self.register_selector.output
        reg0.read_enable = true
        reg1.read_enable = true
        self.alu.A = reg0.memory
        self.alu.B = reg1.memory
        self.alu.opcode = BitArray('0001')
        self._not_skip_increment = ~self.alu.zero_bit_flag
        self.instruction_address_register.write_enable = self.alu.zero_bit_flag
        self.instruction_address_register.memory = BitArray(sum([bit for bit in address]), size=4)

    def JNE(self, address: BitArray):
        true = Bit(1)
        self.register_selector.selection = BitArray('00', size=2)
        reg0 = self.register_selector.output
        self.register_selector.selection = BitArray('01', size=2)
        reg1 = self.register_selector.output
        reg0.read_enable = true
        reg1.read_enable = true
        self.alu.A = reg0.memory
        self.alu.B = reg1.memory
        self.alu.opcode = BitArray('0001')
        self._not_skip_increment = self.alu.zero_bit_flag
        self.instruction_address_register.write_enable = ~self.alu.zero_bit_flag
        self.instruction_address_register.memory = BitArray(sum([bit for bit in address]), size=4)
