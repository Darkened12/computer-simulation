class Assembler:
    def __init__(self, assembly_file: str, output_file: str):
        self.output_file = output_file
        self.assembly_file = assembly_file
        self.assembly_code = self.load_assembly_file()
        self._line_count: int = 0
        self.compiled_code: list[str] = []
        self.compiled_numbers: list[list] = []

        self.methods = {
            'ld': self.load,
            'st': self.store,
            'add': self.add,
            'mov': self.move,
            'jie': self.jmpeq,
            'jne': self.jmpne,
        }
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
        self.register_codes = {
            'reg0': '00',
            'reg1': '01'
        }

    def load_assembly_file(self):
        with open(f'{self.assembly_file}', 'r') as file:
            return file.readlines()

    @staticmethod
    def hex_to_binary_string(hex_string: str, size: str = '4') -> str:
        integer = int(hex_string, 16)
        binary_string = f'{integer:0{size}b}'
        return binary_string

    def split_line(self, line: str) -> list[str]:
        result = line.split(' ')
        if len(result) > 3:
            raise CompilerError(
                f'{self.current_line}"{line}" -> Line is too big. It cannot contain more than 3 statements')
        elif len(result) < 2:
            raise CompilerError(
                f'{self.current_line}"{line}" -> Line is too small. It should contain more than 1 statement')
        return result

    def get_opcode(self, string: str) -> str:
        return self.opcodes[string]

    def get_memory_address_integer(self, hex_string: str) -> int:
        return int(hex_string, 16)

    def get_memory_address_binary(self, hex_string: str) -> str:
        return self.hex_to_binary_string(hex_string)

    def get_memory_value_to_store(self, hex_value: str) -> str:
        return self.hex_to_binary_string(hex_value, size='8')

    def get_register(self, string: str) -> str:
        return self.register_codes[string]

    @property
    def current_line(self) -> str:
        return f'On line {self._line_count}: '

    def load(self, line: str):
        split_line = self.split_line(line)
        register = split_line[1]

        if register == 'reg0':
            opcode = self.opcodes['lda']
        elif register == 'reg1':
            opcode = self.opcodes['ldb']
        else:
            raise CompilerError(f'{self.current_line}"{line}" -> Register "{split_line[1]}" does not exist')

        try:
            address = self.hex_to_binary_string(split_line[2])
        except KeyError:
            raise CompilerError(f'{self.current_line}"{line}" -> Missing RAM address')
        self.compiled_code.append(f'{opcode}{address}')

    def store(self, line: str):
        split_line = self.split_line(line)
        hex_ram_address = split_line[1]
        hex_value_to_store = split_line[2]
        ram_address_integer = self.get_memory_address_integer(hex_ram_address)
        binary_value_to_store = self.get_memory_value_to_store(hex_value_to_store)
        self.compiled_numbers.append([binary_value_to_store, ram_address_integer])

    def add(self, line: str):
        split_line = line.replace(',', '').split(' ')
        opcode = self.get_opcode(split_line[0])
        reg0 = self.get_register(split_line[1])
        reg1 = self.get_register(split_line[2])
        self.compiled_code.append(f'{opcode}{reg0}{reg1}')

    def move(self, line: str):
        split_line = self.split_line(line)
        reg = self.get_register(split_line[1])
        opcode = self.get_opcode('sta') if reg == '00' else self.get_opcode('stb')
        memory_address = self.get_memory_address_binary(split_line[2])
        self.compiled_code.append(f'{opcode}{memory_address}')

    def jmpeq(self, line: str):
        split_line = line.split(' ')
        opcode = self.get_opcode('jie')
        memory_address = self.get_memory_address_binary(split_line[-1])
        self.compiled_code.append(f'{opcode}{memory_address}')

    def jmpne(self, line: str):
        split_line = line.split(' ')
        opcode = self.get_opcode('jne')
        memory_address = self.get_memory_address_binary(split_line[-1])
        self.compiled_code.append(f'{opcode}{memory_address}')

    def fill_gaps(self):
        for n in range(16 - len(self.compiled_code)):
            self.compiled_code.append('00000000')

    def add_memory_numbers(self):
        for item in self.compiled_numbers:
            self.compiled_code[item[1]] = item[0]

    def compile(self):
        for line in self.assembly_code:
            self._line_count += 1
            if line == '\n':
                continue
            self.methods[line.split(' ', 1)[0]](line.replace('\n', ''))

        if len(self.compiled_code) < 16:
            self.fill_gaps()

        self.add_memory_numbers()

        with open(f'{self.output_file}', 'w') as file:
            file.write('\n'.join(self.compiled_code))


class CompilerError(Exception):
    pass


if __name__ == '__main__':
    Assembler('../scripts/main.s', 'main.exec').compile()
