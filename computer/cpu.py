import time

from .alu import ArithmeticLogicUnit
from .base import Bit, BitArray, Demultiplexer
from .memory import Register, RandomAccessMemory


class CentralProcessingUnit:
    def __init__(self, alu: ArithmeticLogicUnit, ram: RandomAccessMemory, clock_speed_limiter_in_hertz: int = 0):
        self.clock_speed_limiter_in_hertz = clock_speed_limiter_in_hertz
        self.alu = alu
        self.ram = ram

        self.register_A = Register(size_in_bits=8)
        self.register_B = Register(size_in_bits=8)
        self.register_C = Register(size_in_bits=8)
        self.register_D = Register(size_in_bits=8)

        self.instruction_register = Register(size_in_bits=8)
        self.address_register = Register(size_in_bits=8)
        self.program_counter_register = Register(size_in_bits=8)
        self.accumulator_register = Register(size_in_bits=8)
        self.status_register = Register(size_in_bits=8)

        self.selectable_registers = [
            self.register_A,
            self.register_B,
            self.register_C,
            self.register_D,
            self.accumulator_register,
            self.status_register
        ]
        self.instructions = [
            self.HLT,
            self.LDA,
            self.LDB,
            self.STA,
            self.STB,
            self.ADD,
            self.SUB,
            self.INC,
            self.DEC,
            self.CMP,
            self.JIL,
            self.JIG,
            self.JIE,
            self.JNE,
        ]
        self.instruction_selector = Demultiplexer(self.instructions)
        self.register_selector = Demultiplexer([
            self.register_A,
            self.register_B,
            self.register_C,
            self.register_D,
            self.program_counter_register,
            self.status_register
        ])

        self.is_equal_mask = BitArray('00000010')
        self.is_greater_mask = BitArray('00000100')
        self.is_lesser_mask = BitArray('00000000')

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
        self.program_counter_register.read_enable = true
        self.alu.A = self.program_counter_register.memory
        self.program_counter_register.read_enable = false
        self.alu.opcode = BitArray('0011', size=4)
        self.program_counter_register.write_enable = self._not_skip_increment
        self.program_counter_register.memory = self.alu.output
        self._not_skip_increment = true
        self.flush()

    def fetch_phase_one(self):
        true = Bit(1)
        self.instruction_register.write_enable = true
        self.program_counter_register.read_enable = true
        self.ram.read_enable = true

        self.ram.address = self.program_counter_register.memory
        self.instruction_register.memory = self.ram.bus

        self.flush()

    def fetch_phase_two(self):
        true = Bit(1)
        self.address_register.write_enable = true
        self.program_counter_register.read_enable = true
        self.ram.read_enable = true

        self.ram.address = self.program_counter_register.memory
        self.address_register.memory = self.ram.bus

        self.flush()

    def decode_phase(self):
        self.instruction_register.read_enable = Bit(1)
        self.address_register.read_enable = Bit(1)
        self._current_instruction = self.instruction_register.memory
        self._current_address = self.address_register.memory

    def execute_phase(self):
        self.instruction_selector.selection = self._current_instruction
        self.instruction_selector.output(self._current_address)
        self.flush()

    def end_phase(self):
        self.increment_program_counter()

    def flush(self):
        false = Bit(0)
        units = [self.ram]
        units += self.selectable_registers
        for unit in units:
            unit.read_enable = false
            unit.write_enable = false

        self.alu.A = BitArray(0, size=8)
        self.alu.B = BitArray(0, size=8)

    def cycle(self):
        def execute_cycle():
            self.fetch_phase_one()
            self.increment_program_counter()
            self.fetch_phase_two()
            self.decode_phase()
            self.execute_phase()
            # print(f'instruction_register: {self.instruction_register}, address_register: {self.address_register}, program_counter: {self.program_counter_register}, accumulator_register: {self.accumulator_register}')
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

    def update_status_register(self):
        self.status_register.write_enable = Bit(1)
        self.status_register.memory = BitArray(
            f'00000{self.alu.negative_bit_flag}{self.alu.zero_bit_flag}{self.alu.carry}')
        self.status_register.write_enable = Bit(0)

    def update_accumulator_register(self):
        self.accumulator_register.write_enable = Bit(1)
        self.accumulator_register.memory = self.alu.output
        self.accumulator_register.write_enable = Bit(0)
        self.update_status_register()

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
        reg2.read_enable = false
        self.update_accumulator_register()

    def ADD(self, registers: BitArray):
        self._add_sub('0000', registers)

    def SUB(self, registers: BitArray):
        self._add_sub('0001', registers)

    def INC(self, register: BitArray):
        self.register_selector.selection = BitArray(register.to_int(), size=2)
        selected_register: Register = self.register_selector.output
        selected_register.read_enable = Bit(1)

        self.alu.A = selected_register.memory
        self.alu.opcode = BitArray('0011')

        selected_register.read_enable = Bit(0)
        selected_register.write_enable = Bit(1)

        selected_register.memory = self.alu.output
        self.update_status_register()

    def DEC(self, register: BitArray):
        self.register_selector.selection = BitArray(register.to_int(), size=2)
        selected_register: Register = self.register_selector.output
        selected_register.read_enable = Bit(1)

        self.alu.A = selected_register.memory
        self.alu.opcode = BitArray('0100')

        selected_register.read_enable = Bit(0)
        selected_register.write_enable = Bit(1)

        selected_register.memory = self.alu.output
        self.update_status_register()

    def CMP(self, registers: BitArray):
        true = Bit(1)

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
        self.alu.opcode = BitArray('0001')

        self.update_status_register()

    def JIL(self, address: BitArray):
        self.status_register.read_enable = Bit(1)
        is_lesser_flag = Bit(int(self.status_register.memory[2]))
        self._not_skip_increment = ~is_lesser_flag
        self.program_counter_register.write_enable = is_lesser_flag
        self.program_counter_register.memory = address

    def JIG(self, address: BitArray):
        self.status_register.read_enable = Bit(1)
        is_lesser_flag = Bit(int(self.status_register.memory[2]))
        self._not_skip_increment = is_lesser_flag
        self.program_counter_register.write_enable = ~is_lesser_flag
        self.program_counter_register.memory = address

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
        self.program_counter_register.write_enable = self.alu.zero_bit_flag
        instruction_address = BitArray(address.to_int(), size=4)
        self.program_counter_register.memory = instruction_address

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
        self.program_counter_register.write_enable = ~self.alu.zero_bit_flag
        instruction_address = BitArray(address.to_int(), size=4)
        self.program_counter_register.memory = instruction_address
