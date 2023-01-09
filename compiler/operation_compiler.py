import re
from typing import Dict, Callable

from .errors import CompilerError
from .utils import get_byte_array_from_integer


class OperationCompiler:
    def __init__(self):
        self.opcodes = {
            'lda': '0001',
            'ldb': '0010',
            'sta': '0011',
            'stb': '0100',
            'add': '0101',
            'sub': '0110',
            'jie': '0111',
            'jne': '1000'
        }
        self.methods = {
            'ld': self.load,
            'st': self.store,
            'add': self.add_and_sub,
            'sub': self.add_and_sub,
            'mov': self.move,
            'jie': self.jmpeq,
            'jne': self.jmpne,
        }
        self.register_codes = {
            'ax': '00',
            'bx': '01'
        }

    def parse_line(self, line: Dict[str, str]) -> str:
        method_to_execute: Callable[[line], str] = self.methods[line['operation']]
        compiled_line: str = method_to_execute(line)
        return compiled_line

    @staticmethod
    def is_binary_string(string):
        pattern = r'^[01]+$'
        return bool(re.search(pattern, string))

    def _get_ram_address(self, line: Dict[str, str]) -> str:
        address = line['second_statement']

        if address is None:
            address = line['first_statement']

        if address.startswith('$'):
            address_integer = address.replace('$', '')
            try:
                return get_byte_array_from_integer(int(address_integer), 4)
            except ValueError:
                raise CompilerError(f'"{line}" -> Wrong RAM syntax')

        if len(address) != 4 or not self.is_binary_string(address):
            raise CompilerError(f'"{line}" -> Wrong RAM address')
        return address

    def get_opcode(self, line: Dict[str, str]) -> str:
        try:
            return self.opcodes[line['operation']]
        except KeyError:
            raise CompilerError(f'"{line}" -> Operation "{line["operation"]}" is not a valid operation')

    def get_register_address(self, assembly_register_code: str) -> str:
        try:
            return self.register_codes[assembly_register_code]
        except KeyError:
            raise CompilerError(f'Register "{assembly_register_code}" is not a valid register')

    def load(self, line: Dict[str, str]) -> str:
        register = line['first_statement']

        if register == 'ax':
            opcode = self.opcodes['lda']
        elif register == 'bx':
            opcode = self.opcodes['ldb']
        else:
            raise CompilerError(f'"{line}" -> Register "{register}" does not exist')

        return f'{opcode}{self._get_ram_address(line)}'

    def store(self, line: Dict[str, str]) -> str:
        register = line['first_statement']

        if register == 'ax':
            opcode = self.opcodes['sta']
        elif register == 'bx':
            opcode = self.opcodes['stb']
        else:
            raise CompilerError(f'"{line}" -> Register "{register}" does not exist')

        return f'{opcode}{self._get_ram_address(line)}'

    def add_and_sub(self, line: Dict[str, str]) -> str:
        opcode = self.get_opcode(line)
        try:
            reg0 = self.get_register_address(line['first_statement'])
            reg1 = self.get_register_address(line['second_statement'])
        except CompilerError as err:
            raise CompilerError(f'"{line}" -> {err}')

        return f'{opcode}{reg0}{reg1}'

    def move(self, line: Dict[str, str]) -> str:
        reg = self.get_register_address(line['first_statement'])
        line['operation'] = 'sta' if reg == '00' else 'stb'
        opcode = self.get_opcode(line)
        memory_address = self._get_ram_address(line)
        return f'{opcode}{memory_address}'

    def jmpeq(self, line: Dict[str, str]) -> str:
        opcode = self.get_opcode(line)
        memory_address = self._get_ram_address(line)
        return f'{opcode}{memory_address}'

    def jmpne(self, line: Dict[str, str]) -> str:
        opcode = self.get_opcode(line)
        memory_address = self._get_ram_address(line)
        return f'{opcode}{memory_address}'