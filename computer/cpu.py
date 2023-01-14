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
        self.stack_pointer = Register(size_in_bits=8)

        self.selectable_registers = [
            self.register_A,
            self.register_B,
            self.register_C,
            self.register_D,
            self.accumulator_register,
            self.status_register
        ]
        self.instructions = [
            self.HLT,  # 00000000 -> int 0
            self.LDA,  # 00000001 -> int 1
            self.LDB,  # 00000010 -> int 2
            self.LDC,  # 00000011 -> int 3
            self.LDD,  # 00000100 -> int 4
            self.STA,  # 00000101 -> int 5
            self.STB,  # 00000110 -> int 6
            self.STC,  # 00000111 -> int 7
            self.STD,  # 00001000 -> int 8
            self.ADD,  # 00001001 -> int 9
            self.SUB,  # 00001010 -> int 10
            self.INC,  # 00001011 -> int 11
            self.DEC,  # 00001100 -> int 12
            self.CMP,  # 00001101 -> int 13
            self.JIL,  # 00001110 -> int 14
            self.JIG,  # 00001111 -> int 15
            self.JIE,  # 00010000 -> int 16
            self.JNE,  # 00010001 -> int 17
            self.PUSH,  # 00010010 -> int 18
            self.POP,  # 00010011 -> int 19
            self.CALL,  # 00010100 -> int 20
            self.RET,  # 00010101 -> int 21
        ]
        self.instruction_selector = Demultiplexer(self.instructions)
        self.register_selector = Demultiplexer([
            self.register_A,
            self.register_B,
            self.register_C,
            self.register_D,
            self.accumulator_register,
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
        units = [self.ram, self.program_counter_register, self.stack_pointer]
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

    def _load(self, register_address: BitArray, ram_address: BitArray):
        self.ram.address = ram_address
        self.ram.read_enable = Bit(1)
        self.register_selector.selection = register_address
        selected_register = self.register_selector.output
        selected_register.write_enable = Bit(1)
        selected_register.memory = self.ram.bus

    def _store(self, register_address: BitArray, ram_address: BitArray):
        self.ram.address = ram_address
        self.ram.write_enable = Bit(1)

        self.register_selector.selection = register_address
        selected_register = self.register_selector.output

        selected_register.read_enable = Bit(1)
        self.ram.bus = selected_register.memory

    def LDA(self, ram_address: BitArray):
        """Load contents of RAM {address} into the Register A"""
        self._load(register_address=BitArray('0000'), ram_address=ram_address)

    def LDB(self, ram_address: BitArray):
        """Load contents of RAM {address} into the Register B"""
        self._load(register_address=BitArray('0001'), ram_address=ram_address)

    def LDC(self, ram_address: BitArray):
        """Load contents of RAM {address} into the Register C"""
        self._load(register_address=BitArray('0010'), ram_address=ram_address)

    def LDD(self, ram_address: BitArray):
        """Load contents of RAM {address} into the Register D"""
        self._load(register_address=BitArray('0011'), ram_address=ram_address)

    def STA(self, ram_address: BitArray):
        """Stores contents on RAM {address} from Register A"""
        self._store(register_address=BitArray('0000'), ram_address=ram_address)

    def STB(self, ram_address: BitArray):
        """Stores contents on RAM {address} from Register B"""
        self._store(register_address=BitArray('0001'), ram_address=ram_address)

    def STC(self, ram_address: BitArray):
        """Stores contents on RAM {address} from Register C"""
        self._store(register_address=BitArray('0010'), ram_address=ram_address)

    def STD(self, ram_address: BitArray):
        """Stores contents on RAM {address} from Register D"""
        self._store(register_address=BitArray('0011'), ram_address=ram_address)

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

    def ADD(self, register_addresses: BitArray):
        self._add_sub('0000', register_addresses)

    def SUB(self, register_addresses: BitArray):
        self._add_sub('0001', register_addresses)

    def INC(self, register_address: BitArray):
        self.register_selector.selection = BitArray(register_address.to_int(), size=2)
        selected_register: Register = self.register_selector.output
        selected_register.read_enable = Bit(1)

        self.alu.A = selected_register.memory
        self.alu.opcode = BitArray('0011')

        selected_register.read_enable = Bit(0)
        selected_register.write_enable = Bit(1)

        selected_register.memory = self.alu.output
        self.update_status_register()

    def DEC(self, register_address: BitArray):
        self.register_selector.selection = BitArray(register_address.to_int(), size=2)
        selected_register: Register = self.register_selector.output
        selected_register.read_enable = Bit(1)

        self.alu.A = selected_register.memory
        self.alu.opcode = BitArray('0100')

        selected_register.read_enable = Bit(0)
        selected_register.write_enable = Bit(1)

        selected_register.memory = self.alu.output
        self.update_status_register()

    def CMP(self, register_addresses: BitArray):
        true = Bit(1)

        reg1_address = BitArray(sum(register_addresses[2:]))
        reg2_address = BitArray(sum(register_addresses[:2]))
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

    def JIL(self, ram_address: BitArray):
        self.status_register.read_enable = Bit(1)
        is_lesser_flag = Bit(int(self.status_register.memory[2]))
        self._not_skip_increment = ~is_lesser_flag
        self.program_counter_register.write_enable = is_lesser_flag
        self.program_counter_register.memory = ram_address

    def JIG(self, ram_address: BitArray):
        self.status_register.read_enable = Bit(1)
        is_lesser_flag = Bit(int(self.status_register.memory[2]))
        self._not_skip_increment = is_lesser_flag
        self.program_counter_register.write_enable = ~is_lesser_flag
        self.program_counter_register.memory = ram_address

    def JIE(self, ram_address: BitArray):
        self.status_register.read_enable = Bit(1)
        zero_bit_flag = Bit(int(self.status_register.memory[1]))
        self._not_skip_increment = ~zero_bit_flag
        self.program_counter_register.write_enable = zero_bit_flag
        self.program_counter_register.memory = ram_address

    def JNE(self, ram_address: BitArray):
        self.status_register.read_enable = Bit(1)
        zero_bit_flag = Bit(int(self.status_register.memory[1]))
        self._not_skip_increment = zero_bit_flag
        self.program_counter_register.write_enable = ~zero_bit_flag
        self.program_counter_register.memory = ram_address

    def PUSH(self, register_address: BitArray):
        true = Bit(1)

        self.register_selector.selection = register_address
        register = self.register_selector.output

        register.read_enable = true
        self.stack_pointer.write_enable = true

        self.stack_pointer.memory = register.memory

    def POP(self, register_address: BitArray):
        true = Bit(1)

        self.register_selector.selection = register_address
        register = self.register_selector.output

        register.write_enable = true
        self.stack_pointer.read_enable = true

        register.memory = self.stack_pointer.memory

    def CALL(self, ram_address: BitArray):
        true = Bit(1)
        false = Bit(0)

        self.program_counter_register.read_enable = true
        self.stack_pointer.write_enable = true
        self.stack_pointer.memory = self.program_counter_register.memory
        self.stack_pointer.write_enable = false
        self.program_counter_register.read_enable = false

        self.program_counter_register.write_enable = true
        self.program_counter_register.memory = ram_address

    def RET(self):
        true = Bit(1)
        false = Bit(0)

        self.program_counter_register.write_enable = true
        self.stack_pointer.read_enable = true
        self.program_counter_register = self.stack_pointer.memory
        self.stack_pointer.read_enable = false
        self.program_counter_register.write_enable = false
