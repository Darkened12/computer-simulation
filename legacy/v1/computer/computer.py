import time

from .alu import ArithmeticLogicUnit
from .cpu import CentralProcessingUnit
from .memory import RandomAccessMemory


class Computer:
    def __init__(self, clock_speed_limiter_in_hertz: int = 0):
        self._alu = ArithmeticLogicUnit()
        self._ram = RandomAccessMemory(size_in_bytes=16)
        self._cpu = CentralProcessingUnit(
            alu=self._alu, ram=self._ram, clock_speed_limiter_in_hertz=clock_speed_limiter_in_hertz
        )
        self._total_run_time = 0

    @property
    def ram(self):
        return self._cpu.ram

    @property
    def alu(self):
        return self._alu

    def run(self):
        start_time = time.perf_counter()
        while not self._cpu.halt:
            self._cpu.cycle()
        self._total_run_time = time.perf_counter() - start_time

    def status(self):
        print(f'execution took: {self._total_run_time} seconds\n'
              f'average clock speed: {self._cpu.cycle_counter / self._total_run_time} Hz\n'
              f'cycles: {self._cpu.cycle_counter}\n'
              f'program_counter: {self._cpu.instruction_address_register}\n'
              f'ax: {self._cpu.register_A}\n'
              f'bx: {self._cpu.register_B}\n'
              f'ram:\n'
              f'{self.ram}')

