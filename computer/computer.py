import time

from .alu import ArithmeticLogicUnit
from .cpu import CentralProcessingUnit
from .memory import RandomAccessMemory


class Computer:
    def __init__(self, clock_speed_limiter_in_hertz: int = 0):
        self._alu = ArithmeticLogicUnit()
        self._ram = RandomAccessMemory(size_in_bytes=256)
        self.cpu = CentralProcessingUnit(
            alu=self._alu, ram=self._ram, clock_speed_limiter_in_hertz=clock_speed_limiter_in_hertz
        )
        self._total_run_time = 0

    @property
    def ram(self):
        return self.cpu.ram

    @property
    def alu(self):
        return self._alu

    def run(self):
        start_time = time.perf_counter()
        while not self.cpu.halt:
            self.cpu.cycle()
        self._total_run_time = time.perf_counter() - start_time

    def status(self):
        print(f'-----------------------\n'
              f'execution took: {self._total_run_time} seconds\n'
              f'cycles: {self.cpu.cycle_counter}\n'
              # f'average clock speed: {self.cpu.cycle_counter / self._total_run_time} Hz\n'
              f'-----------------------\n'
              f'ax: {self.cpu.register_A}\n'
              f'bx: {self.cpu.register_B}\n'
              f'cx: {self.cpu.register_C}\n'
              f'dx: {self.cpu.register_D}\n'
              f'-----------------------\n'
              f'ac: {self.cpu.accumulator_register}\n'
              f'sr: {self.cpu.status_register}\n'
              f'pc: {self.cpu.program_counter_register}\n'
              f'sp: {self.cpu.stack_pointer}\n'
              f'-----------------------\n'
              f'ram:\n'
              f'{self.ram}')

