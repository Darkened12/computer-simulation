import os
from typing import List, Dict, Optional

from .operation_compiler import OperationCompiler
from .parser import get_parsed_code_from_file
from .utils import get_byte_array_from_integer


class Assembler:
    def __init__(
            self,
            path_to_assembly_file: str,
            output_path: str = None,
            ram_size_in_bytes: int = 256,
            operation_compiler=None
    ):
        self.path_to_assembly_file = path_to_assembly_file
        self.assembly_file_name = os.path.basename(path_to_assembly_file)
        self.assembly_file_path = os.path.dirname(path_to_assembly_file)
        self.output_path = output_path
        self.operation_compiler = OperationCompiler() if operation_compiler is None else operation_compiler
        self.parsed_assembly_code = get_parsed_code_from_file(path_to_assembly_file)
        self.ram_size_in_bytes = ram_size_in_bytes

        self.raw_labels = self._extract_labels()
        self.variables = self._get_variables()
        self.subroutines = self._get_subroutines()
        self.instructions = self._get_instructions()

    @classmethod
    def int_to_binary_address(cls, integer: int) -> str:
        return get_byte_array_from_integer(integer, 8)

    def _add_instructions_to_compiled_code(self):
        pass

    def _get_variables(self) -> List[Dict[str, str]]:
        result = []
        for reference, parsed_variable in zip(
                reversed(range(self.ram_size_in_bytes)), self.parsed_assembly_code['data']
        ):
            variable = parsed_variable.copy()
            variable.update({'ram_address': self.int_to_binary_address(reference)})
            result.append(variable)
        return result

    def _extract_labels(self) -> List[Dict[str, str | int]]:
        labels = []
        for index, instruction in enumerate(self.parsed_assembly_code['text']):
            if instruction['operation'] == 'label':
                labels.append({'label': instruction['operation'].replace(':', ''), 'index': index})

        for label in labels:
            self.parsed_assembly_code['text'].pop(label['index'])
            label.update({'value': self.int_to_binary_address(label['index'])})

        return labels

    def _get_variable_ram_address(self, variable_name: str) -> Optional[str]:
        for variable in self.variables:
            if variable['variable_name'] == variable_name:
                return variable['ram_address']

    def _get_subroutine_ram_address(self, label_name: str) -> Optional[str]:
        for subroutine in self.subroutines:
            if subroutine['label'] == label_name:
                return subroutine['ram_address']

    def _get_subroutines(self) -> List[Dict[str, str | list]]:
        result = []
        previous_subroutine_address: int = self.ram_size_in_bytes - len(self.variables)
        for subroutine in reversed(self.parsed_assembly_code['subroutines']):
            parsed_subroutine = subroutine.copy()
            label_address_in_int = previous_subroutine_address - len(subroutine['lines']) * 2
            parsed_subroutine.update({'ram_address': self.int_to_binary_address(label_address_in_int)})
            parsed_subroutine['lines'] = [self._parse_subroutine_instruction_ram_address(instruction) for instruction in parsed_subroutine['lines']]
            result.append(parsed_subroutine)
            previous_subroutine_address = label_address_in_int

        return list(reversed(result))

    def _parse_instruction_ram_address(self, instruction: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
        ram_address = self._get_variable_ram_address(instruction['first_statement'])
        if ram_address is not None:
            instruction['first_statement'] = ram_address
        elif ram_address is None:
            ram_address = self._get_subroutine_ram_address(instruction['first_statement'])
            if ram_address is not None:
                instruction['first_statement'] = ram_address

        ram_address = self._get_variable_ram_address(instruction['second_statement'])
        if ram_address is not None:
            instruction['second_statement'] = ram_address
        return instruction

    def _parse_subroutine_instruction_ram_address(self, instruction: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
        ram_address = self._get_variable_ram_address(instruction['first_statement'])
        if ram_address is not None:
            instruction['first_statement'] = ram_address

        ram_address = self._get_variable_ram_address(instruction['second_statement'])
        if ram_address is not None:
            instruction['second_statement'] = ram_address
        return instruction

    def _get_instructions(self) -> List[Dict[str, str]]:
        result = []
        for instruction in self.parsed_assembly_code['text']:
            parsed_instruction = self._parse_instruction_ram_address(instruction)
            result.append(parsed_instruction)
        return result

    def _compile_instructions(self) -> List[str]:
        compiled_code: List[str] = []
        for line in self.instructions:
            compiled_lines: List[str] = self.operation_compiler.parse_line(line)
            compiled_code += compiled_lines
        return compiled_code

    def _compile_variables(self) -> List[str]:
        compiled_code: List[str] = []
        for line in self.variables:
            compiled_code.append(get_byte_array_from_integer(int(line['value']), 8))
        return list(reversed(compiled_code))

    def _compile_subroutines(self) -> List[str]:
        compiled_code: List[str] = []
        for subroutine in self.subroutines:
            for line in subroutine['lines']:
                compiled_lines: List[str] = self.operation_compiler.parse_line(line)
                compiled_code += compiled_lines
        return compiled_code

    def _generate_empty_space(self, compiled_instructions: List[str], compiled_variables: List[str]) -> List[str]:
        instructions_size: int = len(compiled_instructions)
        variables_size: int = len(compiled_variables)

        spaces_to_create: int = self.ram_size_in_bytes - (instructions_size + variables_size)

        return ['00000000' for n in range(spaces_to_create)]

    def _write_compiled_code_to_file(self, compiled_code: List[str]) -> str:
        parsed_compiled_code = [f'{line}\n' for line in compiled_code]
        parsed_compiled_code[-1] = parsed_compiled_code[-1].replace('\n', '')  # removing blank line from the end

        file_name = self.assembly_file_name.replace('.asm', '.bin')
        if self.output_path is None:
            file_path = self.assembly_file_path
        else:
            file_path = self.output_path

        parsed_file_path_with_file_name = f'{file_path}\\{file_name}'
        with open(parsed_file_path_with_file_name, 'w') as file:
            file.writelines(parsed_compiled_code)

        return parsed_file_path_with_file_name

    @staticmethod
    def get_compiled_code_length(compiled_code: str) -> int:
        return len(compiled_code.split('\n'))

    def compile(self) -> str:
        compiled_variables: List[str] = self._compile_variables()
        compiled_subroutines: List[str] = self._compile_subroutines()
        compiled_subroutines_and_variables = compiled_subroutines + compiled_variables
        compiled_instructions: List[str] = self._compile_instructions()
        empty_space: List[str] = self._generate_empty_space(compiled_instructions, compiled_subroutines_and_variables)

        return self._write_compiled_code_to_file(compiled_instructions + empty_space + compiled_subroutines_and_variables)
