import re
from typing import Dict, Callable, List

from .errors import CompilerError
from .utils import get_byte_array_from_integer


class OperationCompiler:
    def __init__(self):
        self.opcodes = {
            'lda': '00000001',
            'ldb': '00000010',
            'ldc': '00000011',
            'ldd': '00000100',
            'sta': '00000101',
            'stb': '00000110',
            'stc': '00000111',
            'std': '00001000',
            'add': '00001001',
            'sub': '00001010',
            'inc': '00001011',
            'dec': '00001100',
            'cmp': '00001101',
            'jil': '00001110',
            'jig': '00001111',
            'jie': '00010000',
            'jne': '00010001',
            'push': '00010010',
            'pop': '00010011',
            'call': '00010100',
            'ret': '00010101'
        }
        self.methods = {
            'ld': self.load,
            'st': self.store,
            'add': self.add_and_sub,
            'sub': self.add_and_sub,
            'inc': self.single_register_operation,
            'dec': self.single_register_operation,
            'jil': self.jmp,
            'jig': self.jmp,
            'jie': self.jmp,
            'jne': self.jmp,
            'push': self.single_register_operation,
            'pop': self.single_register_operation,
            'call': self.call,
            'ret': self.ret,

        }
        self.register_codes = {
            'ax': '0000',
            'bx': '0001',
            'cx': '0010',
            'dx': '0011',
            'acc': '0100',
            'sr': '0101',
        }

    def parse_line(self, line: Dict[str, str]) -> List[str]:
        method_to_execute: Callable[[line], List[str]] = self.methods[line['operation']]
        compiled_lines: List[str] = method_to_execute(line)
        return compiled_lines

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

        if len(address) != 8 or not self.is_binary_string(address):
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

    def load(self, line: Dict[str, str]) -> List[str]:
        register = line['first_statement']

        try:
            opcode = self.opcodes[f'ld{register[0]}']
        except KeyError:
            raise CompilerError(f'"{line}" -> Register "{register}" is invalid for this operation or does not exist')

        memory_address = self._get_ram_address(line)
        return [opcode, memory_address]

    def store(self, line: Dict[str, str]) -> List[str]:
        register = line['first_statement']

        try:
            opcode = self.opcodes[f'st{register[0]}']
        except KeyError:
            raise CompilerError(f'"{line}" -> Register "{register}" is invalid for this operation or does not exist')

        memory_address = self._get_ram_address(line)
        return [opcode, memory_address]

    def add_and_sub(self, line: Dict[str, str]) -> List[str]:
        opcode = self.get_opcode(line)
        try:
            reg0 = self.get_register_address(line['first_statement'])
            reg1 = self.get_register_address(line['second_statement'])
        except CompilerError as err:
            raise CompilerError(f'"{line}" -> {err}')

        return [opcode, f'{reg0}{reg1}']

    def jmp(self, line: Dict[str, str]) -> List[str]:
        opcode = self.get_opcode(line)
        memory_address = self._get_ram_address(line)
        return [opcode, memory_address]

    def single_register_operation(self, line: Dict[str, str]) -> List[str]:
        opcode = self.get_opcode(line)
        register_address = self.get_register_address(line['first_statement'])
        return [opcode, f'0000{register_address}']

    def call(self, line: Dict[str, str]) -> List[str]:
        opcode = self.get_opcode(line)
        memory_address = self._get_ram_address(line)
        return [opcode, memory_address]

    def ret(self, line: Dict[str, str]) -> List[str]:
        return [self.get_opcode(line), '00000000']
