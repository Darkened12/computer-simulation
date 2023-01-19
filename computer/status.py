from typing import Callable

from .cpu import CentralProcessingUnit


class StatusEmitter:
    def __init__(self, cpu_object: CentralProcessingUnit):
        self._cpu = cpu_object
        self._callback_to_execute_after_event_emits: Callable[[str, CentralProcessingUnit], None] = lambda event, cpu: None

        self._cpu.fetch_phase_one = self._add_emitter_to_cpu_method(self._cpu.fetch_phase_one)
        self._cpu.fetch_phase_two = self._add_emitter_to_cpu_method(self._cpu.fetch_phase_two)
        self._cpu.decode_phase = self._add_emitter_to_cpu_method(self._cpu.decode_phase)
        self._cpu.execute_phase = self._add_emitter_to_cpu_method(self._cpu.execute_phase)
        self._cpu.end_phase = self._add_emitter_to_cpu_method(self._cpu.end_phase)

    def _add_emitter_to_cpu_method(self, method: Callable) -> Callable:
        def wrapper():
            method()
            self._callback_to_execute_after_event_emits(method.__name__, self._cpu)
        return wrapper

    def on_cpu_update(self, callback: Callable[[str, CentralProcessingUnit], None]) -> None:
        self._callback_to_execute_after_event_emits = callback

