import sys


try:
    source_code = sys.argv[1]
    output_file = sys.argv[2]
except IndexError:
    raise NotImplementedError('Invalid commmand. Use "source_code_file" "output_file" without quotation marks.')

opcodes = {
    'ld reg0': '0001',
    'ld reg1': '0010',
    'mov reg0': '0011',
    'mov reg1': '0100',
    'add reg1, reg2': '0101',
    'sub reg1, reg2:': '0111',
    'jmp': '1111'
}


def hex_to_binary_string(hex_string: str, size: str = '4') -> str:
    integer = int(hex_string, 16)
    binary_string = f'{integer:0{size}b}'
    return binary_string


with open(f'{source_code}.s', 'r') as file:
    source = file.readlines()

compiled_code = []
numbers_to_store = []
for line in source:
    code = line.split(' ', 2)
    if 'st' in code[0]:
        hex_ram_address = code[1]
        hex_value_to_store = code[2]
        ram_address_integer = int(hex_ram_address, 16)
        binary_value_to_store = hex_to_binary_string(hex_value_to_store, size='8')
        numbers_to_store.append([binary_value_to_store, ram_address_integer])
        continue

    opcode_key = ' '.join([code[0], code[1]])
    if 'jmp' not in opcode_key:
        opcode = opcodes[opcode_key]
        hex_string_address = code[2]
        binary_address = hex_to_binary_string(hex_string_address)
        compiled_code.append(''.join([opcode, binary_address]))

if len(compiled_code) < 16:
    for n in range(16 - len(compiled_code)):
        compiled_code.append('00000000')

for item in numbers_to_store:
    compiled_code[item[1]] = item[0]


with open(f'{output_file}.exec', 'w') as file:
    file.write('\n'.join(compiled_code))
